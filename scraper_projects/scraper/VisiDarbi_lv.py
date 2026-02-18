"""
VisiDarbi.lv Scraper - v4 Final
Correct pagination: ?page=N (not /page:N)
9,400+ jobs from 12 sources.
"""

import requests
import json
import time
import csv
import sys
import re
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.visidarbi.lv"
JOBS_URL = f"{BASE_URL}/en/job-ads/where:all-latvia"
PER_PAGE = 17

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.visidarbi.lv/en/",
}


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def fetch_soup(session, url):
    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            print(f"[HTTP {r.status_code}]")
            return None
        return BeautifulSoup(r.content.decode('utf-8', errors='replace'), "html.parser")
    except Exception as e:
        print(f"[Error] {e}")
        return None


def get_total(soup):
    """Get total job count from page text."""
    text = soup.get_text(separator=' ')
    m = re.search(r'(\d{2,6})\s+(?:great\s+)?job', text, re.I)
    return int(m.group(1)) if m else 0


def parse_card(card):
    # Title — remove Save button junk first
    title = ""
    title_div = card.find(class_="title")
    if title_div:
        for junk in title_div.find_all(class_=["save", "vd-btn-2", "badge",
                                                "delete-select", "premium-label"]):
            junk.decompose()
        title = title_div.get_text(strip=True)
        title = re.sub(r'\s*Save\s*$', '', title, flags=re.I).strip()

    # URL
    job_url = ""
    link = card.find("a", class_="long-title") or card.find("a", href=re.compile(r'/job-ad/'))
    if link:
        href = link.get("href", "")
        job_url = href if href.startswith("http") else BASE_URL + href

    # ID = last URL segment
    job_id = job_url.rstrip("/").split("/")[-1] if job_url else ""

    # Employer
    employer = ""
    co = card.find("li", class_="company")
    if co:
        employer = co.get_text(strip=True)

    # Location
    location = ""
    loc = card.find("li", class_="location")
    if loc:
        location = loc.get_text(strip=True)

    # Salary
    salary_from = salary_to = salary_currency = ""
    sal = card.find("li", class_="salary")
    if sal:
        t = sal.get_text(strip=True)
        m = re.search(r'(\d[\d\s]*)\s*[-–]\s*(\d[\d\s]*)', t)
        if m:
            salary_from     = m.group(1).replace(" ", "")
            salary_to       = m.group(2).replace(" ", "")
            salary_currency = "EUR"
        else:
            m2 = re.search(r'(\d[\d\s]+)', t)
            if m2:
                salary_from     = m2.group(1).replace(" ", "")
                salary_currency = "EUR"

    # Date added
    publish_date = ""
    added = card.find("li", class_="added")
    if added:
        publish_date = added.get_text(strip=True)

    # Expiration
    expiration_date = ""
    due = card.find("li", class_="duedate") or card.find("li", class_="deadline")
    if due:
        raw = due.get_text(strip=True)
        raw = re.sub(r'(?i)(deadline|until|due)[:\s]*', '', raw).strip()
        if re.match(r'^\d{2}\.\d{2}$', raw):
            raw += ".2026"
        expiration_date = raw

    return {
        "id":              job_id,
        "title":           title,
        "employer":        employer,
        "location":        location,
        "salary_from":     salary_from,
        "salary_to":       salary_to,
        "salary_currency": salary_currency,
        "publish_date":    publish_date,
        "expiration_date": expiration_date,
        "job_url":         job_url,
        "source":          "visidarbi.lv",
    }


def scrape_all(max_pages=None):
    print("=" * 65)
    print("VISIDARBI.LV SCRAPER")
    print("=" * 65)

    session = make_session()
    session.get(f"{BASE_URL}/en/", timeout=15)
    time.sleep(1)

    print("Fetching page 1...")
    first_soup = fetch_soup(session, JOBS_URL)
    if not first_soup:
        print("[FAILED]")
        return []

    total = get_total(first_soup)
    last_page = max(1, (total // PER_PAGE) + 1)
    if max_pages:
        last_page = min(last_page, max_pages)

    print(f"Total jobs on site:  {total}")
    print(f"Pages to scrape:     {last_page}")
    print()

    all_jobs = []
    seen_ids = set()

    for page in range(1, last_page + 1):
        print(f"  [{page:03}/{last_page}]", end=" ", flush=True)

        if page == 1:
            page_soup = first_soup
        else:
            # Use ?page=N — confirmed working (17 cards per page)
            page_soup = fetch_soup(session, f"{JOBS_URL}?page={page}")

        if not page_soup:
            print("FAILED - skipping")
            continue

        cards = page_soup.find_all("div", class_="item")
        if not cards:
            print("0 cards - stopping")
            break

        new = 0
        for card in cards:
            job = parse_card(card)
            jid = job["id"] or job["job_url"]
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(job)
                new += 1

        print(f"{new} jobs  (total: {len(all_jobs)})")

        if page < last_page:
            time.sleep(1.5)

    # ── Save ──────────────────────────────────────────────────────────────
    print()
    if all_jobs:
        with open("visidarbi_jobs.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_jobs[0].keys()))
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"[SAVED] {len(all_jobs)} jobs -> visidarbi_jobs.csv")

        with open("visidarbi_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        print(f"[SAVED] JSON -> visidarbi_jobs.json")
        print(f"\nTOTAL: {len(all_jobs)} jobs")
    else:
        print("[WARNING] No jobs collected.")

    return all_jobs


if __name__ == "__main__":
    # Test 5 pages first
    scrape_all(max_pages=5)

    # Full run — uncomment when test passes:
    # scrape_all()