import os
import csv
import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from g4f.client import Client

input_file = "unique_colleges.csv"
output_file = "college_packages.csv"
missing_file = "missing_colleges.csv"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def check_for_captcha(driver):
    while True:
        try:
            page_source = driver.page_source.lower()
        except Exception:
            time.sleep(2)
            continue
            
        if "our systems have detected unusual traffic" in page_source or \
           "please show you're not a robot" in page_source or \
           "solving the above captcha" in page_source or \
           "cloudflare" in page_source or \
           "we're sorry" in page_source:
            print("\n=======================================================")
            print("[AWAITING HUMAN CAPTCHA RESOLUTION]")
            print("Please solve the CAPTCHA in the opened Chrome window.")
            print("The script will automatically resume once the search results appear.")
            print("=======================================================\n")
            time.sleep(5)
        else:
            break

def extract_with_llm(college_name, context):
    prompt = f"""
    You are a highly precise placement data extraction AI. Extract the placement statistics for '{college_name}' from the context below.

    Context:
    {context}

    STRICT GUARDRAILS:
    1. Sanity Check: Ensure highest_package_lpa >= average_package_lpa >= median_package_lpa. If average is higher than highest, swap them.
    2. Normalize Currency: If text says '1.2 Cr', convert to 120. If '45 LPA' or '45 Lakhs', use 45. Output strictly numbers.
    3. Strict Outlier Filter: Reject any highest package > 40 LPA. If text mentions huge values > 40 LPA, ignore them and find the highest domestic on-campus package instead.
    4. Fallback to Unverified Sources: If there is no official or verified data, you MUST STILL EXTRACT the best available numbers from other sources in the context, but assign a Confidence Score below 60.

    OUTPUT FORMAT: Return ONLY a valid JSON object. No markdown tags.
    {{
        "highest_package_lpa": "number or empty string",
        "average_package_lpa": "number or empty string",
        "median_package_lpa": "number or empty string",
        "placement_percentage": "number or empty string",
        "placement_year": "newest year mentioned or empty string",
        "top_recruiters": "comma separated string",
        "confidence_score": 0,
        "sources": "comma separated string of URLs or domains used"
    }}
    """
    
    # Full regex parser (from agent_research.py) as fallback
    def local_fallback(ctx):
        import re
        ctx = ctx.replace(",", "").replace("₹", "").replace('\n', ' ')

        # --- Highest package ---
        highest = None
        h_matches = re.findall(r'(?i)(?:highest|maximum|top)\s+(?:package|salary|ctc|offer).{0,60}?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac|cr|crore)', ctx)
        if not h_matches:
            h_matches = re.findall(r'(?i)(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac|cr|crore).{0,60}?(?:highest|maximum|top)', ctx)
        valid_h = []
        for m in h_matches:
            try:
                val = float(m)
                if 'cr' in ctx.lower() or 'crore' in ctx.lower():
                    idx = ctx.find(m)
                    if idx != -1 and ('cr' in ctx[idx:idx+20].lower()):
                        val *= 100
                if 1 < val < 500:
                    valid_h.append(val)
            except:
                pass
        if valid_h:
            highest = max(valid_h)

        # --- Average package ---
        average = None
        a_matches = re.findall(r'(?i)(?:average|mean)\s+(?:package|salary|ctc).{0,60}?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac)', ctx)
        if not a_matches:
            a_matches = re.findall(r'(?i)(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac).{0,60}?(?:average|mean)', ctx)
        valid_a = []
        for m in a_matches:
            try:
                val = float(m)
                if 1 < val < 100:
                    valid_a.append(val)
            except:
                pass
        if valid_a:
            average = max(valid_a)

        # --- Median package ---
        median = None
        m_matches = re.findall(r'(?i)(?:median)\s+(?:package|salary|ctc).{0,60}?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac)', ctx)
        valid_m = []
        for m in m_matches:
            try:
                val = float(m)
                if 1 < val < 100:
                    valid_m.append(val)
            except:
                pass
        if valid_m:
            median = max(valid_m)

        # --- Placement percentage ---
        percentage = None
        p_matches = re.findall(r'(?i)([\d\.]+)\s*%\s*(?:students)?\s*(?:placed|placement|got placed)', ctx)
        if not p_matches:
            p_matches = re.findall(r'(?i)(?:placement|placed)\s*(?:percentage|rate)?\s*(?:of|is|at|stood at)?\s*([\d\.]+)\s*%', ctx)
        valid_p = []
        for m in p_matches:
            try:
                val = float(m)
                if 20 <= val <= 100:
                    valid_p.append(val)
            except:
                pass
        if valid_p:
            percentage = max(valid_p)

        # --- Validation: swap if needed ---
        if highest and average and highest < average:
            highest, average = average, highest
        if highest and median and highest < median:
            highest, median = median, highest

        # --- Top Recruiters ---
        recruiters = []
        companies = ['TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture', 'Capgemini', 'IBM', 'Amazon', 'Microsoft', 'Tech Mahindra', 'L&T', 'Reliance', 'HCL', 'Cisco', 'Oracle']
        for c in companies:
            if re.search(r'\b' + re.escape(c) + r'\b', ctx, re.IGNORECASE):
                recruiters.append(c)

        # --- Placement Year ---
        year = None
        y_matches = re.findall(r'(?i)\b(202[0-5])\b', ctx)
        if y_matches:
            year = max(y_matches)

        # --- Confidence score ---
        confidence = 40
        if highest or average:
            confidence = 60

        data = {
            "highest_package_lpa": highest if highest else "",
            "average_package_lpa": average if average else "",
            "median_package_lpa": median if median else "",
            "placement_percentage": percentage if percentage else "",
            "placement_year": year if year else "",
            "top_recruiters": ", ".join(recruiters),
            "confidence_score": confidence,
            "sources": ""
        }
        return data

    for attempt in range(3):
        try:
            client = Client()
            chat_res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            text = chat_res.choices[0].message.content.strip()
            
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            text = text.strip()
            data = json.loads(text)
            
            def to_float(val):
                try: return float(val)
                except: return None
                
            h = to_float(data.get("highest_package_lpa"))
            if h and h > 60:
                data["highest_package_lpa"] = ""
                data["confidence_score"] = 30
                
            return data
        except Exception as e:
            print(f"LLM parsing attempt {attempt+1} failed: {e}")
            time.sleep(1)
            
    # If all LLM attempts fail, fallback to regex
    print("Falling back to regex parsing...")
    return local_fallback(context)

def process_college(driver, college_name):
    query = f"placement statistics highest average median package top recruiters of {college_name}"
    encoded_query = urllib.parse.quote_plus(query)
    # Using the exact URL template the user provided with the updated query
    url = f"https://www.google.com/search?q={encoded_query}&sxsrf=APpeQnuGAsJLOTMtMkmbzZ5xcPt6v6tZ1A%3A1781869766723&udm=50&aep=1&ntc=1&mstk=AUtExfC8uuKi95hbfk3XKxfB4nFajML24LVRBDKYLpgTmvezQrqZwozZXZ6EaxOEjVzEJzMSnp0FMtL_95fXOFX0_vTDcSawQLldQ2nZoiADxYO97eWUTKr8-lFnv4bsx-aem1hYUL4e6UCHUdvmSTMZ--qZjuiGorkM75084lr8_-txOhomQuRhZaO7y9AvUv0ktrJ7GlTvBQayVVjKoWKiVqNc8yo0NylJC74ED8-3Sm3DUG-2ZZyM5YaAbIQFMRmfGCnwuJC5KnqOX45xbKyzo7GzZax8E6B0e3D-KHOiK7St6tf4yL70Ic_ADbUEzvSulC2hvf6PQSkiyg&csuir=1&mtid=yyw1apuMKKyhseMP8pbGmQw"
    
    driver.get(url)
    time.sleep(2)
    check_for_captcha(driver)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    body = soup.find('body')
    if body:
        context = body.get_text(separator=' ', strip=True)[:4000]
    else:
        context = ""
    
    if not context.strip() or len(context) < 100:
        return None

    return extract_with_llm(college_name, context)

def main():
    import pandas as pd
    
    fieldnames = [
        "college_name", "highest_package_lpa", "average_package_lpa", 
        "median_package_lpa", "placement_percentage", "placement_year", 
        "top_recruiters", "confidence_score", "sources"
    ]
    
    all_df = pd.read_csv(input_file)
    colleges = all_df['college_name'].tolist()

    file_exists = os.path.exists(output_file)
    if file_exists:
        try:
            done_df = pd.read_csv(output_file, names=fieldnames, header=0 if 'college_name' in open(output_file).readline() else None)
            done_colleges = set(done_df['college_name'].dropna().tolist())
            colleges = [c for c in colleges if c not in done_colleges]
        except pd.errors.EmptyDataError:
            pass

    missing_exists = os.path.exists(missing_file)
    if missing_exists:
        try:
            missing_df = pd.read_csv(missing_file)
            if 'college_name' in missing_df.columns:
                missing_colleges_set = set(missing_df['college_name'].dropna().tolist())
                colleges = [c for c in colleges if c not in missing_colleges_set]
        except pd.errors.EmptyDataError:
            pass

    total = len(colleges)
    print(f"Starting execution using User's Google URL Template... {total} colleges remaining to process.")

    file_exists = os.path.exists(output_file)
    missing_exists = os.path.exists(missing_file)
    
    driver = setup_driver()
    
    try:
        with open(output_file, "a", newline="", encoding="utf-8") as csvfile, \
             open(missing_file, "a", newline="", encoding="utf-8") as missingfile:
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            missing_writer = csv.writer(missingfile)
            
            if not missing_exists:
                missing_writer.writerow(["college_name"])

            if not file_exists:
                writer.writeheader()

            for idx, college in enumerate(colleges, 1):
                print(f"\n[{idx}/{total}] Processing: {college}")
                
                data = process_college(driver, college)
                    
                if not data or (not data.get("highest_package_lpa") and not data.get("average_package_lpa")):
                    print(f"--> MISSING: No verified placement data found for {college}")
                    missing_writer.writerow([college])
                    missingfile.flush()
                    continue

                data["college_name"] = college
                writer.writerow(data)
                csvfile.flush()
                print(f"--> EXTRACTED: Highest: {data.get('highest_package_lpa')} LPA | Avg: {data.get('average_package_lpa')} LPA")
                time.sleep(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
