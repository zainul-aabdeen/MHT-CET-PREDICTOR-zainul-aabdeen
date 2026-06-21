import csv
import re
import time
import os
import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress insecure request warnings for colleges with bad SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

input_file = "unique_colleges.csv"
output_file = "college_packages.csv"
missing_file = "missing_colleges.csv"

columns = [
    "college_name",
    "highest_package_lpa",
    "average_package_lpa",
    "median_package_lpa",
    "placement_percentage",
    "placement_year",
    "top_recruiters",
    "confidence_score",
    "sources"
]

def clean_money(text):
    text = text.replace(",", "").replace("₹", "").replace('\n', ' ')
    
    # Highest package
    highest = None
    h_matches = re.findall(r'(?i)(?:highest|maximum|top)\s+(?:package|salary|ctc|offer).*?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac|cr|crore)', text)
    if not h_matches:
        h_matches = re.findall(r'(?i)(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac|cr|crore).*?(?:highest|maximum|top)', text)
    valid_h = []
    for m in h_matches:
        try:
            val = float(m)
            if 'cr' in text.lower() or 'crore' in text.lower():
                idx = text.find(m)
                if idx != -1 and ('cr' in text[idx:idx+20].lower()):
                    val *= 100
            if 1 < val < 500:
                valid_h.append(val)
        except:
            pass
    if valid_h:
        highest = max(valid_h)

    # Average package
    average = None
    a_matches = re.findall(r'(?i)(?:average|mean)\s+(?:package|salary|ctc).*?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac)', text)
    if not a_matches:
        a_matches = re.findall(r'(?i)(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac).*?(?:average|mean)', text)
    valid_a = []
    for m in a_matches:
        try:
            val = float(m)
            if 1 < val < 100: # Average is usually lower
                valid_a.append(val)
        except:
            pass
    if valid_a:
        average = max(valid_a) 

    # Median package
    median = None
    m_matches = re.findall(r'(?i)(?:median)\s+(?:package|salary|ctc).*?(?:rs\.?|inr)?\s*([\d\.]+)\s*(?:lpa|lakh|lac)', text)
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

    # Percentage
    percentage = None
    p_matches = re.findall(r'(?i)([\d\.]+)\s*%\s*(?:students)?\s*(?:placed|placement|got placed)', text)
    if not p_matches:
        p_matches = re.findall(r'(?i)(?:placement|placed)\s*(?:percentage|rate)?\s*(?:of|is|at|stood at)?\s*([\d\.]+)\s*%', text)
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

    return highest, average, median, percentage

def fetch_url_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, timeout=8, verify=False, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for script in soup(["script", "style", "nav", "footer"]):
                script.extract()
            text = soup.get_text(separator=' ')
            text = re.sub(r'\s+', ' ', text)
            return text[:15000]
    except Exception:
        pass
    return ""

def process_college(college_name):
    # Import ddgs locally to avoid global issues if not installed
    try:
        from ddgs import DDGS
    except ImportError:
        return None
        
    queries = [
        f"{college_name} placements highest package average package",
        f"{college_name} placement statistics",
    ]
    
    ddgs = DDGS()
    full_text = ""
    sources = set()
    urls_to_fetch = []
    
    for q in queries:
        try:
            results = ddgs.text(q, max_results=3)
            if results:
                for r in results:
                    full_text += r.get('body', '') + " "
                    href = r.get('href')
                    if href and not href.endswith('.pdf'):
                        urls_to_fetch.append(href)
        except Exception:
            pass
        time.sleep(1.5)
        
    # Open top search results
    for url in urls_to_fetch[:3]:
        text = fetch_url_text(url)
        if text:
            full_text += text + " "
            sources.add(url)
        time.sleep(0.5)
        
    if not full_text.strip():
        return None
        
    highest, average, median, percentage = clean_money(full_text)
    
    # Confidence score calculation
    confidence = 30
    if highest or average:
        confidence = 60
        if len(sources) > 1:
            confidence = 80
        for s in sources:
            if 'nirfindia.org' in s or '.ac.in' in s or '.edu.in' in s:
                confidence = 95
                break
                
    # Validation Rules
    if highest and average and highest < average:
        highest, average = average, highest
        
    if highest and median and highest < median:
        highest, median = median, highest

    # Top Recruiters
    recruiters = []
    companies = ['TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture', 'Capgemini', 'IBM', 'Amazon', 'Microsoft', 'Google', 'Tech Mahindra', 'L&T', 'Reliance', 'HCL', 'Cisco', 'Oracle']
    for c in companies:
        if re.search(r'\b' + re.escape(c) + r'\b', full_text, re.IGNORECASE):
            recruiters.append(c)
            
    # Placement Year
    year = None
    y_matches = re.findall(r'(?i)\b(202[0-5])\b', full_text)
    if y_matches:
        year = max(y_matches)
        
    if not highest and not average and not median and not percentage:
        return None
        
    return {
        "highest_package_lpa": highest if highest else "",
        "average_package_lpa": average if average else "",
        "median_package_lpa": median if median else "",
        "placement_percentage": percentage if percentage else "",
        "placement_year": year if year else "",
        "top_recruiters": ", ".join(recruiters),
        "confidence_score": confidence,
        "sources": ", ".join(list(sources)[:2])
    }

def main():
    processed = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed.add(row["college_name"])

    missing = []
    completed = 0
    failed = 0

    if not os.path.exists(input_file):
        print(f"{input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cname = row["college_name"]
            if cname in processed:
                continue
                
            print(f"Processing: {cname}", flush=True)
            data = None
            for _ in range(2):
                data = process_college(cname)
                if data:
                    break
                time.sleep(3)
                
            if not data:
                print(f"Failed: {cname}", flush=True)
                missing.append(cname)
                failed += 1
                continue
                
            out_row = {
                "college_name": cname,
                "highest_package_lpa": data["highest_package_lpa"],
                "average_package_lpa": data["average_package_lpa"],
                "median_package_lpa": data["median_package_lpa"],
                "placement_percentage": data["placement_percentage"],
                "placement_year": data["placement_year"],
                "top_recruiters": data["top_recruiters"],
                "confidence_score": data["confidence_score"],
                "sources": data["sources"]
            }
            
            file_exists = os.path.exists(output_file)
            with open(output_file, "a", encoding="utf-8", newline="") as out_f:
                writer = csv.DictWriter(out_f, fieldnames=columns)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(out_row)
                
            completed += 1
            processed.add(cname)
            print(f"Success: {cname} (Highest: {data['highest_package_lpa']}, Avg: {data['average_package_lpa']})", flush=True)
            time.sleep(2)

    if missing:
        with open(missing_file, "w", encoding="utf-8", newline="") as mf:
            writer = csv.writer(mf)
            writer.writerow(["college_name"])
            for m in missing:
                writer.writerow([m])

    print("\n--- Final output ---", flush=True)
    print(f"completed: {completed}", flush=True)
    print(f"failed: {failed}", flush=True)
    print(f"missing: {len(missing)}", flush=True)

if __name__ == "__main__":
    main()
