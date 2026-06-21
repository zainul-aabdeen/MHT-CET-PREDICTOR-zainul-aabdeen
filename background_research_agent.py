import os
import csv
import json
import time
import pandas as pd
from duckduckgo_search import DDGS

input_file = "unique_colleges.csv"
output_file = "college_packages.csv"
missing_file = "missing_colleges.csv"

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
    5. Confidence Score (Must be number):
       - 95 to 100: Official college portal (.edu.in/.ac.in) or NIRF report.
       - 80 to 94: Explicitly stated by AI Summary or multiple aligning sources.
       - 60 to 79: Found on a single news/educational portal (e.g., Shiksha, Collegedunia).
       - 30 to 59: Unverified or weak data.

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
    try:
        ddgs = DDGS()
        chat_res = ddgs.chat(prompt, model="gpt-4o-mini")
        
        text = chat_res.strip()
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
        print(f"LLM parsing failed: {e}")
        return None

def process_college(college_name):
    query = f"{college_name} placement statistics highest average package site:edu.in OR site:ac.in OR collegedunia OR shiksha"
    
    context = ""
    sources = []
    try:
        ddgs = DDGS()
        # Invisible web search scraping
        results = ddgs.text(query, max_results=8)
        for res in results:
            link = res.get("href", "")
            title = res.get("title", "")
            body = res.get("body", "")
            if link and link not in sources:
                sources.append(link)
            context += f"Source URL: {link}\nTitle: {title}\nText Snippet: {body}\n\n"
    except Exception as e:
        print(f"Search failed: {e}")
        return None

    if not context.strip():
        return None

    return extract_with_llm(college_name, context)

def main():
    if os.path.exists(missing_file):
        df = pd.read_csv(missing_file)
        if len(df) == 0:
            df = pd.read_csv(input_file)
    else:
        df = pd.read_csv(input_file)

    colleges = df['college_name'].tolist()
    total = len(colleges)
    print(f"Starting invisible web scraping execution... {total} colleges to process.")

    fieldnames = [
        "college_name", "highest_package_lpa", "average_package_lpa", 
        "median_package_lpa", "placement_percentage", "placement_year", 
        "top_recruiters", "confidence_score", "sources"
    ]
    
    file_exists = os.path.exists(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as csvfile, \
         open(missing_file, "w", newline="", encoding="utf-8") as missingfile:
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        missing_writer = csv.writer(missingfile)
        missing_writer.writerow(["college_name"])

        if not file_exists:
            writer.writeheader()

        for idx, college in enumerate(colleges, 1):
            print(f"\n[{idx}/{total}] Processing: {college}")
            
            data = None
            for attempt in range(2):
                data = process_college(college)
                if data and (data.get("highest_package_lpa") or data.get("average_package_lpa")):
                    break
                time.sleep(2)
                
            if not data or (not data.get("highest_package_lpa") and not data.get("average_package_lpa")):
                print(f"--> MISSING: No verified placement data found for {college}")
                missing_writer.writerow([college])
                continue

            data["college_name"] = college
            writer.writerow(data)
            csvfile.flush()
            print(f"--> EXTRACTED: Highest: {data.get('highest_package_lpa')} LPA | Avg: {data.get('average_package_lpa')} LPA | Conf: {data.get('confidence_score')}")
            time.sleep(1)

if __name__ == "__main__":
    main()
