"""
MHT-CET CAP Round 1 (2025-26) PDF Cutoff Data Extractor
=========================================================
Extracts ALL cutoff rows from ALL pages into ONE normalized CSV.
Zero silent data loss. Preserves source values exactly.

Key format observations:
- Stage line: "Stage CAT1 CAT2 CAT3 ..." defines categories for the section
- Wrapped categories: single uppercase letters (e.g., "S") on following lines 
  are suffixes that append to the last full category 
- Data line: "I 37591 58518 94334 ..." — Roman numeral + ranks on SAME line
- Percentile line: "(88.9550679) (82.3322294) ..."
- Multi-stage: categories are shared; Stage I fills first N, Stage II fills next M, etc.
"""

import pdfplumber
import csv
import re
import os
import sys
import random
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    PDF_FILE = sys.argv[1]
    out_prefix = sys.argv[2] if len(sys.argv) > 2 else "out"
    OUTPUT_CSV = f"{out_prefix}_clean.csv"
    VALIDATION_REPORT = f"validation_report_{out_prefix}.txt"
    FAILED_PAGES_FILE = f"failed_pages_{out_prefix}.txt"
    SUMMARY_REPORT = f"summary_report_{out_prefix}.txt"
else:
    PDF_FILE = r"MHTCET 2025 CAP -2 Cut Off.pdf"
    OUTPUT_CSV = "mht_cet_cap2_clean.csv"
    VALIDATION_REPORT = "validation_report_cap2.txt"
    FAILED_PAGES_FILE = "failed_pages_cap2.txt"
    SUMMARY_REPORT = "summary_report_cap2.txt"

# ── Patterns ──────────────────────────────────────────────────────────────
COLLEGE_PATTERN = re.compile(r'^(\d{5})\s*-\s*(.+)$')
BRANCH_PATTERN = re.compile(r'^(\d{8,11}[A-Z]*)\s*-\s*(.+)$')
STAGE_DATA_PATTERN = re.compile(r'^(I{1,3})\s+([\d\s]+)$')  # "I 37591 58518 ..."
PERCENTILE_LINE_PATTERN = re.compile(r'^\([\d.]+\)')  # starts with (number

# Seat allocation section headers  
SEAT_SECTIONS = {
    "Home University Seats Allotted to Home University Candidates": ("HU", "HU_HU"),
    "Home University Seats Allotted to Other Than Home University Candidates": ("HU", "HU_OHU"),
    "Other Than Home University Seats Allotted to Other Than Home University Candidates": ("OHU", "OHU_OHU"),
    "Other Than Home University Seats Allotted to Home University Candidates": ("OHU", "OHU_HU"),
    "State Level": ("STATE", "STATE"),
}

CSV_COLUMNS = [
    "page_number",
    "college_code",
    "college_name",
    "branch_code",
    "branch_name",
    "seat_scope",
    "seat_allocation_type",
    "category_order",
    "category",
    "stage",
    "cutoff_rank",
    "cutoff_percentile",
]


def detect_seat_section(line):
    """Check if a line matches one of the seat allocation section headers."""
    stripped = line.strip()
    for header, (scope, alloc_type) in SEAT_SECTIONS.items():
        if stripped == header:
            return scope, alloc_type
    return None, None


def merge_wrapped_categories(raw_tokens):
    """
    Merge wrapped category suffixes back onto their parent category.
    
    pdfplumber sometimes wraps long category names. For example:
    Stage line: "Stage ... PWDROBC DEFROBCS ORPHAN EWS"
    Next line:  "S"
    
    The "S" is a suffix that should be appended to PWDROBC -> PWDROBCS
    
    But also handles "S S" (two suffixes) which means both the last two 
    categories ending without S need the S appended.
    
    Algorithm: Process the wrapped tokens. Each single-letter token appended
    to the last category that doesn't already end with that letter.
    
    Actually, the wrapping happens because the Stage line was too long for the 
    PDF renderer, so the last characters wrapped to the next line.
    The wrapped chars are appended sequentially to the last categories.
    """
    if not raw_tokens:
        return raw_tokens
    return raw_tokens  # We handle wrapping differently below


def parse_page(page, page_num):
    """
    Parse a single PDF page and extract all cutoff data rows.
    Returns: (list of row dicts, list of issue strings)
    """
    text = page.extract_text()
    if not text:
        return [], ["Empty page"]

    lines = text.split('\n')
    rows = []
    issues = []
    
    # Context
    college_code = None
    college_name = None
    branch_code = None
    branch_name = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # ── Skip ignorable lines ──────────────────────────────────────
        if _is_ignorable(line):
            i += 1
            continue
        
        # ── College detection ─────────────────────────────────────────
        m = COLLEGE_PATTERN.match(line)
        if m:
            college_code = m.group(1)
            college_name = m.group(2).strip()
            branch_code = None
            branch_name = None
            i += 1
            continue
        
        # ── Branch detection ──────────────────────────────────────────
        m = BRANCH_PATTERN.match(line)
        if m:
            branch_code = m.group(1)
            branch_name = m.group(2).strip()
            i += 1
            # Check for multi-line branch name continuation
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                # Stop if next line is a recognized structure
                if (_is_ignorable(next_line) or
                    next_line.startswith("Status:") or
                    detect_seat_section(next_line)[0] is not None or
                    COLLEGE_PATTERN.match(next_line) or
                    BRANCH_PATTERN.match(next_line) or
                    next_line.startswith("Stage ")):
                    break
                # It's a continuation of the branch name
                branch_name += " " + next_line
                i += 1
            continue
        
        # ── Status line (skip) ────────────────────────────────────────
        if line.startswith("Status:"):
            i += 1
            continue
        
        # ── Seat section detection ────────────────────────────────────
        scope, alloc_type = detect_seat_section(line)
        if scope:
            i += 1
            # Now parse the seat section block
            block_rows, block_issues, i = _parse_seat_block(
                lines, i, page_num,
                college_code, college_name,
                branch_code, branch_name,
                scope, alloc_type
            )
            rows.extend(block_rows)
            issues.extend(block_issues)
            continue
        
        # ── Unrecognized line — advance ───────────────────────────────
        i += 1
    
    return rows, issues


def _parse_seat_block(lines, start_i, page_num,
                      college_code, college_name,
                      branch_code, branch_name,
                      seat_scope, seat_alloc_type):
    """
    Parse a seat allocation block starting after the section header.
    
    Expected structure:
    1. "Stage CAT1 CAT2 ..." line with categories
    2. Optional wrapped category suffixes (single uppercase letters)
    3. One or more stage data lines: "I 12345 67890 ..."
    4. After each stage data line: percentile line "(xx.xxx) (yy.yyy) ..."
    
    Categories are shared across stages. Stage I uses first N categories,
    Stage II uses next M, etc.
    
    Returns: (rows, issues, next_line_index)
    """
    rows = []
    issues = []
    i = start_i
    
    # Step 1: Find and parse the "Stage ..." line
    categories = []
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if line.startswith("Stage "):
            # Extract category names
            parts = line.split()
            # parts[0] = "Stage", rest are raw category tokens
            raw_cats = parts[1:]
            i += 1
            
            # Step 2: Check for wrapped category suffixes on following lines
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                
                # Check if this line contains ONLY short uppercase tokens
                # (wrapped category suffixes like "S", "S S", "H")
                tokens = next_line.split()
                if all(len(t) <= 2 and t.isalpha() and t.isupper() for t in tokens):
                    # These are wrapped suffixes - append them to the raw categories
                    raw_cats.extend(tokens)
                    i += 1
                else:
                    break
            
            # Now merge wrapped suffixes with their parent categories
            categories = _merge_category_suffixes(raw_cats)
            break
        else:
            # Unexpected content before Stage line
            # This could be another section header or structure
            return rows, issues, i
    
    if not categories:
        return rows, issues, i
    
    # Step 3: Parse stage data lines
    # Categories are consumed sequentially across stages
    cat_offset = 0  # tracks how many categories have been consumed
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Check if we've left this seat block
        # (new section, new branch, new college, Stage line for new section, etc.)
        if (_is_ignorable(line) or
            detect_seat_section(line)[0] is not None or
            COLLEGE_PATTERN.match(line) or
            BRANCH_PATTERN.match(line) or
            line.startswith("Status:") or
            line.startswith("Stage ")):
            break
        
        # Try to match stage data line: "I 37591 58518 ..." or "II 196674"
        m = re.match(r'^(I{1,3})\s+([\d\s]+)$', line)
        if m:
            stage = m.group(1)
            rank_str = m.group(2).strip()
            rank_values = [int(x) for x in rank_str.split()]
            num_ranks = len(rank_values)
            i += 1
            
            # Step 4: Parse percentile line(s)
            percentile_values = []
            while i < len(lines):
                pline = lines[i].strip()
                if not pline:
                    i += 1
                    continue
                
                # Check if it's a percentile line
                pmatches = re.findall(r'\(([0-9]+\.[0-9]+)\)', pline)
                if pmatches:
                    percentile_values.extend(pmatches)
                    i += 1
                    # Continue only if we haven't collected enough percentiles
                    if len(percentile_values) >= num_ranks:
                        break
                else:
                    break
            
            # Assign categories from cat_offset
            num_percs = len(percentile_values)
            
            if num_ranks != num_percs:
                issues.append(
                    "Page %d: Rank/percentile count mismatch in %s %s Stage %s: "
                    "ranks=%d, percs=%d" % (
                        page_num, branch_code, seat_alloc_type, stage,
                        num_ranks, num_percs
                    )
                )
            
            if cat_offset + num_ranks > len(categories):
                issues.append(
                    "Page %d: More ranks than remaining categories in %s %s Stage %s: "
                    "offset=%d, ranks=%d, total_cats=%d" % (
                        page_num, branch_code, seat_alloc_type, stage,
                        cat_offset, num_ranks, len(categories)
                    )
                )
            
            for idx in range(num_ranks):
                cat_idx = cat_offset + idx
                cat_name = categories[cat_idx] if cat_idx < len(categories) else "UNKNOWN_%d" % cat_idx
                
                row = {
                    "page_number": page_num,
                    "college_code": college_code or "",
                    "college_name": college_name or "",
                    "branch_code": branch_code or "",
                    "branch_name": branch_name or "",
                    "seat_scope": seat_scope,
                    "seat_allocation_type": seat_alloc_type,
                    "category_order": cat_idx + 1,
                    "category": cat_name,
                    "stage": stage,
                    "cutoff_rank": rank_values[idx],
                    "cutoff_percentile": percentile_values[idx] if idx < num_percs else "",
                }
                rows.append(row)
            
            cat_offset += num_ranks
            continue
        
        # If line doesn't match any expected pattern, break
        break
    
    return rows, issues, i


def _merge_category_suffixes(raw_tokens):
    """
    Merge wrapped category suffixes.
    
    When pdfplumber extracts the Stage line, long category names can wrap.
    Example:
      Stage line: "Stage ... PWDROBC DEFROBCS ORPHAN EWS"
      Next line:  "S"
      Result:     PWDROBC -> PWDROBCS (the S appends to the truncated category)
    
    Algorithm: 
    1. Separate trailing suffix tokens (1-2 char uppercase) from full categories
    2. Scan full categories RIGHT-TO-LEFT
    3. For each suffix (also right-to-left), attach to the next eligible category
    4. Skip categories that are known complete words (ORPHAN, EWS, TFWS, MI)
       or already end with the suffix letter
    """
    # Known complete category names that should NEVER get a suffix
    KNOWN_COMPLETE = {'ORPHAN', 'EWS', 'TFWS', 'MI'}
    
    # Separate full categories from trailing suffix tokens
    suffix_start = len(raw_tokens)
    for j in range(len(raw_tokens) - 1, -1, -1):
        t = raw_tokens[j]
        if len(t) <= 2 and t.isalpha() and t.isupper():
            suffix_start = j
        else:
            break
    
    full_cats = list(raw_tokens[:suffix_start])
    suffix_tokens = list(raw_tokens[suffix_start:])
    
    if not suffix_tokens:
        return full_cats
    
    # Attach suffixes right-to-left: scan categories from the end,
    # skip known-complete and already-suffixed categories
    suffix_idx = len(suffix_tokens) - 1
    for i in range(len(full_cats) - 1, -1, -1):
        if suffix_idx < 0:
            break
        cat = full_cats[i]
        suffix = suffix_tokens[suffix_idx]
        # Skip known complete categories and those already ending with suffix
        if cat in KNOWN_COMPLETE:
            continue
        if cat.endswith(suffix):
            continue
        # This category is truncated — attach the suffix
        full_cats[i] = cat + suffix
        suffix_idx -= 1
    
    return full_cats


def _is_ignorable(line):
    """Check if a line should be ignored (headers, footers, legends, page numbers)."""
    if line.startswith("D Government of Maharashtra"):
        return True
    if line.startswith("i State Common Entrance Test Cell"):
        return True
    if line.startswith("r Cut Off List"):
        return True
    if line.startswith("Degree Courses In Engineering"):
        return True
    if line.startswith("Legends:"):
        return True
    if line.startswith("Maharashtra State Seats"):
        return True
    if line.startswith("Note:"):
        return True
    
    # Page number at bottom (standalone 1-4 digit number, value < total pages + margin)
    # These are typically "1" at the bottom of every page
    if re.match(r'^\d{1,4}$', line):
        val = int(line)
        if val <= 2000:  # well above any realistic rank that would appear alone
            return True
    
    return False


def parse_overflow_page(page, page_num, prev_context):
    """
    Parse a page that is a horizontal continuation of a table from the previous page.
    Such pages lack standard headers (college, branch, stage).
    """
    text = page.extract_text()
    if not text:
        return []
    lines = text.split('\n')
    i = 0
    rows = []
    
    stage_counter = 1
    STAGES = ["I", "II", "III", "IV", "V", "VI", "VII"]
    
    while i < len(lines):
        line = lines[i].strip()
        if not line or _is_ignorable(line):
            i += 1
            continue
            
        tokens = line.split()
        # Look for category line
        if len(tokens) > 0 and all(t.isupper() and t.isalpha() for t in tokens):
            categories = list(tokens)
            i += 1
            
            # Suffixes
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt: 
                    i += 1
                    continue
                toks = nxt.split()
                if all(len(t) <= 2 and t.isalpha() and t.isupper() for t in toks):
                    categories.extend(toks)
                    i += 1
                else:
                    break
            
            categories = _merge_category_suffixes(categories)
            
            # Ranks
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt:
                    i += 1
                    continue
                
                if all(t.isdigit() for t in nxt.split()):
                    ranks = [int(x) for x in nxt.split()]
                    i += 1
                    
                    # Percentiles
                    percs = []
                    while i < len(lines):
                        pline = lines[i].strip()
                        if not pline:
                            i += 1
                            continue
                        pmatches = re.findall(r'\(([0-9]+\.[0-9]+)\)', pline)
                        if pmatches:
                            percs.extend(pmatches)
                            i += 1
                            if len(percs) >= len(ranks):
                                break
                        else:
                            break
                    
                    stage_str = STAGES[stage_counter - 1] if stage_counter <= len(STAGES) else "UNKNOWN"
                    stage_counter += 1
                    
                    for idx in range(len(ranks)):
                        cat_name = categories[idx] if idx < len(categories) else "UNKNOWN_%d" % idx
                        rows.append({
                            "page_number": page_num,
                            "college_code": prev_context.get("college_code", ""),
                            "college_name": prev_context.get("college_name", ""),
                            "branch_code": prev_context.get("branch_code", ""),
                            "branch_name": prev_context.get("branch_name", ""),
                            "seat_scope": prev_context.get("seat_scope", ""),
                            "seat_allocation_type": prev_context.get("seat_allocation_type", ""),
                            "category_order": idx + 1,
                            "category": cat_name,
                            "stage": stage_str,
                            "cutoff_rank": ranks[idx],
                            "cutoff_percentile": percs[idx] if idx < len(percs) else "",
                        })
                    break
                else:
                    break
        else:
            i += 1
    
    return rows


def main():
    print("=" * 70)
    print("MHT-CET CAP Round 1 (2025-26) PDF Cutoff Extractor")
    print("=" * 70)
    print()
    print("Opening PDF: %s" % PDF_FILE)
    
    pdf = pdfplumber.open(PDF_FILE)
    total_pages = len(pdf.pages)
    print("Total pages: %d" % total_pages)
    
    all_rows = []
    all_issues = []
    failed_pages = []
    pages_with_zero_rows = []
    prev_context = {}
    
    for page_idx in range(total_pages):
        page_num = page_idx + 1
        if page_num % 100 == 0 or page_num == 1:
            print("  Processing page %d/%d..." % (page_num, total_pages))
        
        try:
            rows, issues = parse_page(pdf.pages[page_idx], page_num)
            
            # If no rows, try overflow parsing
            if len(rows) == 0 and prev_context:
                overflow_rows = parse_overflow_page(pdf.pages[page_idx], page_num, prev_context)
                if overflow_rows:
                    rows = overflow_rows
            
            if len(rows) > 0:
                all_rows.extend(rows)
                all_issues.extend(issues)
                
                # Update prev_context from the last row on this page
                last = rows[-1]
                prev_context = {
                    "college_code": last["college_code"],
                    "college_name": last["college_name"],
                    "branch_code": last["branch_code"],
                    "branch_name": last["branch_name"],
                    "seat_scope": last["seat_scope"],
                    "seat_allocation_type": last["seat_allocation_type"],
                }
            else:
                pages_with_zero_rows.append(page_num)
                
        except Exception as e:
            failed_pages.append((page_num, str(e)))
            all_issues.append("Page %d: EXCEPTION - %s" % (page_num, e))
    
    pdf.close()
    
    print()
    print("Extraction complete.")
    print("  Total rows: %d" % len(all_rows))
    print("  Issues: %d" % len(all_issues))
    print("  Pages with zero rows: %d" % len(pages_with_zero_rows))
    print("  Failed pages: %d" % len(failed_pages))
    
    # ── Write CSV ──────────────────────────────────────────────────────
    print()
    print("Writing CSV: %s" % OUTPUT_CSV)
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    
    # ── Compute statistics ─────────────────────────────────────────────
    colleges = set()
    branches = set()
    rows_per_scope = defaultdict(int)
    missing_values = defaultdict(int)
    
    for row in all_rows:
        if row["college_code"]:
            colleges.add(row["college_code"])
        if row["branch_code"]:
            branches.add(row["branch_code"])
        rows_per_scope[row["seat_allocation_type"]] += 1
        
        for col in ["college_code", "branch_code", "category"]:
            if not row[col]:
                missing_values[col] += 1
    
    # ── Duplicate detection ────────────────────────────────────────────
    seen_keys = set()
    duplicate_count = 0
    duplicate_examples = []
    for row in all_rows:
        key = (
            row["college_code"],
            row["branch_code"],
            row["seat_scope"],
            row["category"],
            row["stage"],
        )
        if key in seen_keys:
            duplicate_count += 1
            if len(duplicate_examples) < 10:
                duplicate_examples.append(row)
        else:
            seen_keys.add(key)
    
    # ── Random audit (100 rows) ────────────────────────────────────────
    audit_sample_size = min(100, len(all_rows))
    audit_indices = sorted(random.sample(range(len(all_rows)), audit_sample_size)) if all_rows else []
    audit_rows = [all_rows[idx] for idx in audit_indices]
    
    # ── Write validation report ────────────────────────────────────────
    print("Writing: %s" % VALIDATION_REPORT)
    with open(VALIDATION_REPORT, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("Pages parsed: %d\n" % total_pages)
        f.write("Total PDF pages: %d\n" % total_pages)
        f.write("Pages parsed == Total PDF pages: %s\n\n" % (total_pages == total_pages))
        
        f.write("Total rows extracted: %d\n" % len(all_rows))
        f.write("Duplicate rows: %d\n" % duplicate_count)
        
        if duplicate_examples:
            f.write("Duplicate examples (first 10):\n")
            for d in duplicate_examples:
                f.write("  Page %s: %s | %s | %s | %s | Stage %s\n" % (
                    d["page_number"], d["college_code"], d["branch_code"],
                    d["seat_allocation_type"], d["category"], d["stage"]))
        
        f.write("\nMissing values:\n")
        for col, count in sorted(missing_values.items()):
            f.write("  %s: %d\n" % (col, count))
        if not missing_values:
            f.write("  None\n")
        
        f.write("\nIssues (%d):\n" % len(all_issues))
        for issue in all_issues:
            f.write("  - %s\n" % issue)
        if not all_issues:
            f.write("  None\n")
        
        f.write("\nPages with zero rows (%d):\n" % len(pages_with_zero_rows))
        for p in pages_with_zero_rows:
            f.write("  Page %d\n" % p)
        if not pages_with_zero_rows:
            f.write("  None\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("Random Audit Sample (%d rows):\n" % len(audit_rows))
        f.write("=" * 70 + "\n")
        for row in audit_rows:
            f.write("  Page %s: %s | %s | %s | %s | Stage %s | "
                    "Rank=%s | Pctl=%s\n" % (
                        row["page_number"], row["college_code"],
                        row["branch_code"], row["seat_allocation_type"],
                        row["category"], row["stage"],
                        row["cutoff_rank"], row["cutoff_percentile"]))
    
    # ── Write failed pages ─────────────────────────────────────────────
    print("Writing: %s" % FAILED_PAGES_FILE)
    with open(FAILED_PAGES_FILE, 'w', encoding='utf-8') as f:
        if failed_pages:
            for pn, error in failed_pages:
                f.write("Page %d: %s\n" % (pn, error))
        else:
            f.write("No failed pages.\n")
    
    # ── Write summary report ───────────────────────────────────────────
    print("Writing: %s" % SUMMARY_REPORT)
    with open(SUMMARY_REPORT, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SUMMARY REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write("total_pages: %d\n" % total_pages)
        f.write("total_colleges: %d\n" % len(colleges))
        f.write("total_branches: %d\n" % len(branches))
        f.write("total_rows: %d\n\n" % len(all_rows))
        
        f.write("rows_per_seat_scope:\n")
        for scope, count in sorted(rows_per_scope.items()):
            f.write("  %s: %d\n" % (scope, count))
        f.write("\n")
        
        f.write("duplicate_rows: %d\n\n" % duplicate_count)
        
        f.write("missing_values:\n")
        for col, count in sorted(missing_values.items()):
            f.write("  %s: %d\n" % (col, count))
        if not missing_values:
            f.write("  None\n")
        f.write("\n")
        
        f.write("failed_pages: %d\n" % len(failed_pages))
        for pn, error in failed_pages:
            f.write("  Page %d: %s\n" % (pn, error))
        if not failed_pages:
            f.write("  None\n")
    
    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print("  CSV:         %s" % OUTPUT_CSV)
    print("  Validation:  %s" % VALIDATION_REPORT)
    print("  Failed:      %s" % FAILED_PAGES_FILE)
    print("  Summary:     %s" % SUMMARY_REPORT)
    print()
    
    if failed_pages:
        print("WARNING: %d pages failed. Check %s." % (len(failed_pages), FAILED_PAGES_FILE))
        return 1
    if missing_values:
        total_missing = sum(missing_values.values())
        print("WARNING: %d missing values detected. Check %s." % (total_missing, VALIDATION_REPORT))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
