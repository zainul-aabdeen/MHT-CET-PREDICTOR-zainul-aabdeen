import csv
import json
import os
import re
import time
from duckduckgo_search import DDGS

# File paths
input_file = "unique_colleges.csv"
output_file = "college_packages.csv"
missing_file = "missing_colleges.csv"

# Output columns
columns = [
    "college_name",
    "highest_package_lpa",
    "average_package_lpa",
    "median_package_lpa",
    "placement_percentage",
    "top_recruiters",
    "placement_year",
    "confidence_score",
    "citations_used"
]

def extract_from_ai(college_name):
    query = f"{college_name} placements highest package average package placement percentage"
    try:
        ddgs = DDGS()
        # 1. Search Web
        results = ddgs.text(query, max_results=7)
        if not results:
            return None
        
        # Format results as context
        context = ""
        for i, res in enumerate(results):
            context += f"Source {i+1}:\nURL: {res.get('href')}\nTitle: {res.get('title')}\nSnippet: {res.get('body')}\n\n"
            
        # 2. Use Chat to extract
        prompt = f"""
        You are a placement data extractor. Based ONLY on the search results provided below, extract the placement details for '{college_name}'.
        
        Search Results:
        {context}
        
        Instructions:
        - highest_package_lpa: number in LPA (e.g. 24). If 1.2 Cr, write 120. Strip text, return just the number.
        - average_package_lpa: number in LPA. Strip text, return just the number.
        - median_package_lpa: number in LPA. Strip text, return just the number.
        - placement_percentage: number only (e.g. 82).
        - top_recruiters: comma-separated string of companies.
        - placement_year: newest year mentioned (e.g. 2023).
        - citations_used: list of URLs from the sources above that you used. Format as comma separated string.
        - confidence_score: 95 if an official college/university URL is used, 80 if multiple trusted sources, 60 if one unofficial source, 30 if weak/conflicting. Number only.

        If multiple numbers appear, choose the newest year, most repeated value, or official value. Normalize ₹24 LPA to 24, ₹1.2 Cr to 120, 82% to 82.

        Return ONLY a valid JSON object. No markdown, no explanation:
        {{
            "highest_package_lpa": "value or empty string",
            "average_package_lpa": "value or empty string",
            "median_package_lpa": "value or empty string",
            "placement_percentage": "value or empty string",
            "top_recruiters": "value or empty string",
            "placement_year": "value or empty string",
            "citations_used": "value or empty string",
            "confidence_score": 0
        }}
        """
        
        chat_res = ddgs.chat(prompt, model="gpt-4o-mini")
        text = chat_res.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Error for {college_name}: {e}")
        return None

def main():
    processed_colleges = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_colleges.add(row["college_name"])

    missing_colleges = []
    
    total_colleges = 0
    completed = len(processed_colleges)

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            college_name = row["college_name"]
            total_colleges += 1
            
            if college_name in processed_colleges:
                continue
                
            print(f"Processing ({total_colleges}): {college_name}")
            
            # Retry logic
            data = None
            for _ in range(3):
                data = extract_from_ai(college_name)
                if data:
                    break
                time.sleep(5)
            
            if not data:
                print(f"Failed to extract for {college_name}")
                missing_colleges.append(college_name)
                time.sleep(2)
                continue
                
            # Prepare row
            out_row = {
                "college_name": college_name,
                "highest_package_lpa": data.get("highest_package_lpa", ""),
                "average_package_lpa": data.get("average_package_lpa", ""),
                "median_package_lpa": data.get("median_package_lpa", ""),
                "placement_percentage": data.get("placement_percentage", ""),
                "top_recruiters": data.get("top_recruiters", ""),
                "placement_year": data.get("placement_year", ""),
                "confidence_score": data.get("confidence_score", ""),
                "citations_used": data.get("citations_used", "")
            }
            
            # Save incrementally
            file_exists = os.path.exists(output_file)
            with open(output_file, "a", encoding="utf-8", newline="") as out_f:
                writer = csv.DictWriter(out_f, fieldnames=columns)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(out_row)
            
            processed_colleges.add(college_name)
            completed += 1
            print(f"Saved {college_name}")
            time.sleep(1) # Be gentle with DDG

    # Save missing
    if missing_colleges:
        with open(missing_file, "w", encoding="utf-8", newline="") as mf:
            writer = csv.writer(mf)
            writer.writerow(["college_name"])
            for mc in missing_colleges:
                writer.writerow([mc])

    # Stats
    total_conf = 0
    count_conf = 0
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    conf = float(row["confidence_score"])
                    total_conf += conf
                    count_conf += 1
                except:
                    pass
    
    avg_conf = total_conf / count_conf if count_conf > 0 else 0
    
    print("\nFinal summary:")
    print(f"total_colleges: {total_colleges}")
    print(f"completed: {completed}")
    print(f"missing: {len(missing_colleges)}")
    print(f"average_confidence: {avg_conf:.2f}")

if __name__ == "__main__":
    main()
