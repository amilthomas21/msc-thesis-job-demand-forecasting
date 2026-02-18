"""
CV.lv Full Scraper - Final Version
Extracts job listings into a clean CSV matching your thesis data format.

Fields extracted:
  id, title, employer, salary_from, salary_to, salary_currency,
  category, remote_work, remote_type, country, publish_date, expiration_date
"""

import requests
import json
import time
import math
import sys
import csv
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cv.lv/",
}

BASE_URL = "https://www.cv.lv"
LIMIT = 20

# CV.lv numeric work time codes
WORK_TIME_MAP = {
    1: "Full-time",
    2: "Full-time with shifts",
    3: "Part-time",
    4: "Freelance",
    5: "Fixed term",
    6: "Internship",
    7: "Work after classes",
    8: "Seasonal",
}

CATEGORIES = {
    "INFORMATION_TECHNOLOGY":    "IT",
    "ADMINISTRATION":            "Administration",
    "SALES":                     "Sales",
    "ORGANISATION_MANAGEMENT":   "Organisation Management",
    "FINANCE_ACCOUNTING":        "Finance & Accounting",
    "TRADE":                     "Trade Sector",
    "TECHNICAL_ENGINEERING":     "Technical Engineering",
    "CONSTRUCTION_REAL_ESTATE":  "Construction & Real Estate",
    "PRODUCTION_MANUFACTURING":  "Production & Manufacturing",
    "SERVICE_INDUSTRY":          "Customer Service",
    "LOGISTICS_TRANSPORT":       "Logistics & Transport",
    "BANKING_INSURANCE":         "Banking & Insurance",
    "MARKETING_ADVERTISING":     "Marketing & Advertising",
    "HUMAN_RESOURCES":           "Human Resources",
    "ELECTRONICS_TELECOM":       "Electronics & Telecom",
    "HEALTH_SOCIAL_CARE":        "Health & Social Care",
    "STATE_PUBLIC_ADMIN":        "State & Public Admin",
    "LAW_LEGAL":                 "Law & Legal",
    "EDUCATION_SCIENCE":         "Education & Science",
    "ENERGETICS_ELECTRICITY":    "Energetics & Electricity",
    "QUALITY_ASSURANCE":         "Quality Assurance",
    "TOURISM_HOTELS_CATERING":   "Tourism, Hotels & Catering",
    "MEDIA_PR":                  "Media & PR",
    "AGRICULTURE_ENVIRONMENTAL": "Agriculture & Environment",
    "SECURITY_RESCUE_DEFENCE":   "Security & Defence",
    "PHARMACY":                  "Pharmacy",
    "FOREST_WOODCUTTING":        "Forest & Woodcutting",
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


def extract_vacancies(next_data):
    try:
        state = next_data["props"]["pageProps"]
        redux = state.get("initialReduxState", {})
        vacancies = (
            redux.get("vacancies", {}).get("list")
            or redux.get("search", {}).get("vacancies")
            or redux.get("search", {}).get("results")
        )
        if vacancies:
            return vacancies
        search = state.get("searchResults", {})
        vacancies = search.get("vacancies") or search.get("results")
        if vacancies:
            return vacancies
        init = state.get("initialState", {})
        vacancies = init.get("vacancies") or init.get("search", {}).get("vacancies")
        if vacancies:
            return vacancies
    except Exception as e:
        print(f"    [Parse error] {e}")
    return []


def get_total_for_category(next_data, category_key):
    try:
        cats = next_data["props"]["pageProps"]["searchResults"]["categories"]
        return cats.get(category_key, 0)
    except Exception:
        return 0


def parse_job(job, category_name):
    """Extract clean fields from a raw vacancy dict."""

    # Work time: list of ints -> readable string
    work_times = job.get("workTimes", [])
    work_time_str = ", ".join(
        WORK_TIME_MAP.get(wt, str(wt)) for wt in work_times
    ) if work_times else ""

    # Salary
    salary_from = job.get("salaryFrom") or ""
    salary_to   = job.get("salaryTo")   or ""
    # CV.lv salaries are in EUR (no explicit currency field, EUR is standard)
    salary_currency = "EUR" if (salary_from or salary_to) else ""

    # Remote
    remote       = job.get("remoteWork", False)
    remote_type  = job.get("remoteWorkType", "") or ""

    # Dates — strip time, keep date only
    publish_date    = (job.get("publishDate")    or "")[:10]
    expiration_date = (job.get("expirationDate") or "")[:10]
    renewed_date    = (job.get("renewedDate")    or "")[:10]

    return {
        "id":               job.get("id", ""),
        "title":            job.get("positionTitle", ""),
        "employer":         job.get("employerName", ""),
        "category":         category_name,
        "salary_from":      salary_from,
        "salary_to":        salary_to,
        "salary_currency":  salary_currency,
        "work_time":        work_time_str,
        "remote":           remote,
        "remote_type":      remote_type,
        "publish_date":     publish_date,
        "renewed_date":     renewed_date,
        "expiration_date":  expiration_date,
        "source":           "cv.lv",
    }


def scrape_category(category_key, display_name, max_pages=None):
    """Scrape all pages for one category, return list of parsed job dicts."""
    all_jobs = []

    # First page
    url = (f"{BASE_URL}/en/search"
           f"?categories[]={category_key}"
           f"&limit={LIMIT}&offset=0&isHourlySalary=false")

    first = get_next_data(url)
    if not first:
        print("FAILED")
        return []

    total     = get_total_for_category(first, category_key)
    vacancies = extract_vacancies(first)

    if total == 0 and not vacancies:
        print("0 jobs")
        return []

    for v in vacancies:
        all_jobs.append(parse_job(v, display_name))

    total_pages = math.ceil(total / LIMIT) if total else 1
    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"total={total}, pages={total_pages}", end=" ", flush=True)

    for page in range(1, total_pages):
        offset = page * LIMIT
        url = (f"{BASE_URL}/en/search"
               f"?categories[]={category_key}"
               f"&limit={LIMIT}&offset={offset}&isHourlySalary=false")

        data = get_next_data(url)
        if not data:
            break

        vacancies = extract_vacancies(data)
        if not vacancies:
            break

        for v in vacancies:
            all_jobs.append(parse_job(v, display_name))

        time.sleep(1.5)

    print(f"-> {len(all_jobs)} jobs")
    return all_jobs


def scrape_all_categories(max_pages_per_category=None):
    print("=" * 70)
    print("CV.LV SCRAPER - Full Run")
    print("=" * 70)
    print()

    all_jobs = []
    summary  = []

    for i, (key, name) in enumerate(CATEGORIES.items(), 1):
        print(f"[{i:02}/{len(CATEGORIES)}] {name:<40}", end=" ")
        jobs = scrape_category(key, name, max_pages=max_pages_per_category)
        all_jobs.extend(jobs)
        summary.append({"category": name, "jobs": len(jobs)})
        time.sleep(2)

    # ── Save CSV ──────────────────────────────────────────────────────────
    csv_file = "cvlv_jobs.csv"
    if all_jobs:
        fieldnames = list(all_jobs[0].keys())
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"\n[SAVED] {len(all_jobs)} jobs saved to {csv_file}")

    # ── Save JSON ─────────────────────────────────────────────────────────
    with open("cvlv_jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    print(f"[SAVED] JSON backup saved to cvlv_jobs.json")

    # ── Summary ───────────────────────────────────────────────────────────
    total = sum(s["jobs"] for s in summary)
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n{'Category':<40} {'Jobs':>6}")
    print("-" * 50)
    for s in sorted(summary, key=lambda x: x["jobs"], reverse=True):
        print(f"{s['category']:<40} {s['jobs']:>6}")
    print("-" * 50)
    print(f"{'TOTAL':<40} {total:>6}")

    with open("cvlv_summary.txt", "w", encoding="utf-8") as f:
        f.write("CV.LV SCRAPE SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        for s in sorted(summary, key=lambda x: x["jobs"], reverse=True):
            f.write(f"{s['category']:<40} {s['jobs']:>6} jobs\n")
        f.write(f"\nTOTAL: {total} jobs\n")
    print("\n[SAVED] Summary saved to cvlv_summary.txt")

    return all_jobs


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # TEST RUN — 2 pages per category (~40 jobs each), fast check
    # scrape_all_categories(max_pages_per_category=2)

    # FULL RUN — all pages, all categories
    scrape_all_categories()