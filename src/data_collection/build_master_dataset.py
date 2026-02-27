"""
Master Dataset Builder
MSc Thesis: Job Market Skill Demand Forecasting
Author: Amil Thomas

This script:
1. Fixes SS.lv titles and dates by re-fetching each job page
2. Merges SS.lv + CV.lv into one master CSV
3. Saves to data/processed/master_jobs.csv
"""

import csv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

# ── File paths ────────────────────────────────────────────────────────────────
SS_LV_FILE  = "data/raw/ss_lv_jobs_full.csv"
CV_LV_FILE  = "data/raw/cv_lv_jobs.csv"
OUTPUT_FILE = "data/processed/master_jobs.csv"

# ── Output columns ────────────────────────────────────────────────────────────
FIELDNAMES = [
    "source", "category", "title", "url",
    "posted_date", "scraped_date", "description"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


# ── SS.lv title/date fixer ────────────────────────────────────────────────────

def fix_ss_lv_row(url):
    """Re-fetch SS.lv job page and extract correct title and date."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.content, "html.parser")

        # Title from Profesija row
        title = ""
        for lab in soup.find_all("td", class_="ads_opt_name"):
            if "Profesija" in lab.get_text():
                val = lab.find_next_sibling("td")
                if val:
                    title = val.get_text(strip=True)
                break

        # Date from footer
        date = ""
        for td in soup.find_all("td", class_="msg_footer"):
            txt = td.get_text(strip=True)
            if "Datums:" in txt:
                raw = txt.split("Datums:")[-1].strip()
                try:
                    date = datetime.strptime(raw.split()[0], "%d.%m.%Y").date().isoformat()
                except Exception:
                    date = raw
                break

        return title, date
    except Exception:
        return "", ""


# ── Load and process SS.lv ────────────────────────────────────────────────────

def process_ss_lv():
    print("\n" + "=" * 60)
    print("STEP 1: Processing SS.lv data")
    print("=" * 60)

    rows = list(csv.DictReader(open(SS_LV_FILE, encoding="utf-8")))
    print(f"Loaded {len(rows)} rows from {SS_LV_FILE}")
    print("Fixing titles and dates...\n")

    processed = []
    for i, row in enumerate(rows, 1):
        url = row.get("url", "")
        title, date = fix_ss_lv_row(url)

        processed.append({
            "source":       "ss.lv",
            "category":     row.get("category", ""),
            "title":        title or row.get("title", ""),
            "url":          url,
            "posted_date":  date or row.get("posted_date", ""),
            "scraped_date": row.get("scraped_date", ""),
            "description":  row.get("description", ""),
        })

        if i % 20 == 0 or i == len(rows):
            print(f"  {i}/{len(rows)} fixed | Last: {title} | {date}")

        sleep(0.5)

    print(f"\n✓ SS.lv: {len(processed)} rows processed")
    return processed


# ── Load and process CV.lv ────────────────────────────────────────────────────

def process_cv_lv():
    print("\n" + "=" * 60)
    print("STEP 2: Processing CV.lv data")
    print("=" * 60)

    rows = list(csv.DictReader(open(CV_LV_FILE, encoding="utf-8")))
    print(f"Loaded {len(rows)} rows from {CV_LV_FILE}")

    processed = []
    for row in rows:
        processed.append({
            "source":       "cv.lv",
            "category":     row.get("category", ""),
            "title":        row.get("title", ""),
            "url":          row.get("url", ""),
            "posted_date":  row.get("posted_date", ""),
            "scraped_date": row.get("scraped_date", ""),
            "description":  row.get("description", ""),
        })

    print(f"✓ CV.lv: {len(processed)} rows processed")
    return processed


# ── Merge and save ────────────────────────────────────────────────────────────

def merge_and_save(ss_rows, cv_rows):
    print("\n" + "=" * 60)
    print("STEP 3: Merging and saving master dataset")
    print("=" * 60)

    os.makedirs("data/processed", exist_ok=True)

    all_rows = ss_rows + cv_rows

    # Deduplicate by URL
    seen_urls = set()
    unique_rows = []
    for row in all_rows:
        url = row.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_rows.append(row)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"\n{'=' * 60}")
    print(f"MASTER DATASET COMPLETE")
    print(f"{'=' * 60}")
    print(f"  SS.lv jobs    : {len(ss_rows)}")
    print(f"  CV.lv jobs    : {len(cv_rows)}")
    print(f"  Total unique  : {len(unique_rows)}")
    print(f"  Output file   : {OUTPUT_FILE}")
    print(f"{'=' * 60}")

    # Quick stats
    from collections import Counter
    sources = Counter(r["source"] for r in unique_rows)
    dates = [r["posted_date"] for r in unique_rows if r["posted_date"]]
    titles = [r["title"] for r in unique_rows if r["title"]]
    descs = [r["description"] for r in unique_rows if r["description"]]

    print(f"\nQUALITY CHECK:")
    print(f"  Jobs with title       : {len(titles)}/{len(unique_rows)}")
    print(f"  Jobs with date        : {len(dates)}/{len(unique_rows)}")
    print(f"  Jobs with description : {len(descs)}/{len(unique_rows)}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("MASTER DATASET BUILDER")
    print("MSc Thesis: Job Market Skill Demand Forecasting")
    print("=" * 60)

    ss_rows = process_ss_lv()
    cv_rows = process_cv_lv()
    merge_and_save(ss_rows, cv_rows)