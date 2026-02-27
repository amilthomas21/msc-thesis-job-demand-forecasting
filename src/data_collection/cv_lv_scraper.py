"""
CV.lv Full Scraper - Fixed Version
MSc Thesis: Job Market Skill Demand Forecasting
Author: Amil Thomas
"""

import requests
import json
import time
import math
import sys
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cv.lv/",
}

BASE_URL    = "https://www.cv.lv"
OUTPUT_FILE = "data/raw/cv_lv_jobs.csv"
LIMIT       = 20
DELAY_LIST  = 1.5
DELAY_DETAIL= 2.0

CATEGORIES = {
    "INFORMATION_TECHNOLOGY":    "IT",
    "ADMINISTRATION":            "Administration",
    "SALES":                     "Sales",
    "ORGANISATION_MANAGEMENT":   "Organisation Management",
    "FINANCE_ACCOUNTING":        "Finance & Accounting",
    "TECHNICAL_ENGINEERING":     "Technical Engineering",
    "CONSTRUCTION_REAL_ESTATE":  "Construction & Real Estate",
    "PRODUCTION_MANUFACTURING":  "Production & Manufacturing",
    "LOGISTICS_TRANSPORT":       "Logistics & Transport",
    "MARKETING_ADVERTISING":     "Marketing & Advertising",
    "ELECTRONICS_TELECOM":       "Electronics & Telecom",
    "HEALTH_SOCIAL_CARE":        "Health & Social Care",
    "EDUCATION_SCIENCE":         "Education & Science",
    "ENERGETICS_ELECTRICITY":    "Energetics & Electricity",
    "QUALITY_ASSURANCE":         "Quality Assurance",
}


def get_next_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.content, "html.parser")
        tag = soup.find("script", id="__NEXT_DATA__")
        if not tag:
            return None
        return json.loads(tag.string)
    except Exception as e:
        print(f"    [Error] {e}")
        return None


def get_description(job_url):
    try:
        r = requests.get(job_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.content, "html.parser")
        el = soup.find("div", class_="vacancy-content")
        if el:
            for tag in el.find_all(["script", "style", "button", "a"]):
                tag.decompose()
            text = el.get_text(separator=" ", strip=True)
            return " ".join(text.split())
    except Exception:
        pass
    return ""


def load_existing_ids(filepath):
    seen = set()
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("url", "")
                if url:
                    seen.add(url.split("/")[-1])
    return seen


def scrape_category(category_key, display_name, existing_ids, writer, csv_file, scraped_date):
    url = (f"{BASE_URL}/en/search"
           f"?categories[]={category_key}"
           f"&limit={LIMIT}&offset=0&isHourlySalary=false")

    first = get_next_data(url)
    if not first:
        print("FAILED")
        return 0

    try:
        sr = first["props"]["pageProps"]["searchResults"]
        total = sr.get("total", 0)
        vacancies = sr.get("vacancies", [])
    except Exception:
        print("PARSE ERROR")
        return 0

    if not vacancies:
        print("0 jobs")
        return 0

    total_pages = math.ceil(total / LIMIT) if total else 1
    print(f"total={total}, pages={total_pages}", end=" ", flush=True)

    all_vacancies = list(vacancies)

    for page in range(1, total_pages):
        offset = page * LIMIT
        url = (f"{BASE_URL}/en/search"
               f"?categories[]={category_key}"
               f"&limit={LIMIT}&offset={offset}&isHourlySalary=false")
        data = get_next_data(url)
        if not data:
            break
        try:
            page_vacancies = data["props"]["pageProps"]["searchResults"]["vacancies"]
            if not page_vacancies:
                break
            all_vacancies.extend(page_vacancies)
        except Exception:
            break
        time.sleep(DELAY_LIST)

    new_count = 0
    for job in all_vacancies:
        job_id = str(job.get("id", ""))
        if job_id in existing_ids:
            continue

        job_url = f"{BASE_URL}/en/vacancy/{job_id}"
        description = get_description(job_url)
        raw_date = job.get("publishDate", "") or ""
        posted_date = raw_date[:10]

        row = {
            "category":     display_name,
            "title":        job.get("positionTitle", ""),
            "url":          job_url,
            "posted_date":  posted_date,
            "scraped_date": scraped_date,
            "description":  description,
            "employer":     job.get("employerName", ""),
            "salary_from":  job.get("salaryFrom", "") or "",
            "salary_to":    job.get("salaryTo", "") or "",
            "remote":       job.get("remoteWork", ""),
            "source":       "cv.lv",
        }

        writer.writerow(row)
        csv_file.flush()
        existing_ids.add(job_id)
        new_count += 1
        time.sleep(DELAY_DETAIL)

    print(f"-> {new_count} new jobs")
    return new_count


def run_scraper():
    os.makedirs("data/raw", exist_ok=True)
    existing_ids = load_existing_ids(OUTPUT_FILE)
    print(f"[RESUME] {len(existing_ids)} jobs already in dataset.\n")

    file_exists = os.path.exists(OUTPUT_FILE)
    csv_file = open(OUTPUT_FILE, "a", newline="", encoding="utf-8")
    fieldnames = ["category", "title", "url", "posted_date", "scraped_date",
                  "description", "employer", "salary_from", "salary_to", "remote", "source"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()

    scraped_date = datetime.now().strftime("%Y-%m-%d")
    total_new = 0

    print("=" * 65)
    print("CV.LV FULL SCRAPER - Fixed Version with Descriptions")
    print("=" * 65)

    for i, (key, name) in enumerate(CATEGORIES.items(), 1):
        print(f"\n[{i:02}/{len(CATEGORIES)}] {name:<40}", end=" ")
        new = scrape_category(key, name, existing_ids, writer, csv_file, scraped_date)
        total_new += new
        time.sleep(2)

    csv_file.close()

    print("\n" + "=" * 65)
    print(f"SCRAPING COMPLETE")
    print(f"  New jobs added : {total_new}")
    print(f"  Output file    : {OUTPUT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    run_scraper()
