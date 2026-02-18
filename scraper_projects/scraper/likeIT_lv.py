"""
LikeIT.lv Scraper v6
Fixes the stuck keyword filter by using requests.Session() with cookies.
The site stores filters server-side in a session — we need to:
1. Start a fresh session
2. POST to clear filters OR visit with keyword="" to reset
3. Then scrape normally
"""

import requests
import json
import time
import csv
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.likeit.lv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CATEGORIES = {
    "programming":           "Programming",
    "system-administration": "System Administration",
    "system-analysis":       "System Analysis",
    "web-design":            "Web Design",
    "testing":               "Testing",
    "support":               "Support",
    "leading-management":    "Leading & Management",
    "sales-marketing":       "Sales & Marketing",
    "other":                 "Other",
}


def make_session():
    """Create a fresh requests session."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def get_next_data(session, url, params=None):
    try:
        r = session.get(url, params=params, timeout=15)
        if r.status_code != 200:
            print(f"[HTTP {r.status_code}]")
            return None
        soup = BeautifulSoup(r.content, "html.parser")
        tag = soup.find("script", id="__NEXT_DATA__")
        if not tag:
            return None
        return json.loads(tag.string)
    except Exception as e:
        print(f"[Error] {e}")
        return None


def extract_jobs_and_pagination(next_data):
    try:
        jobs_obj = next_data["props"]["pageProps"]["jobs"]
        if isinstance(jobs_obj, dict):
            return (
                jobs_obj.get("data", []),
                jobs_obj.get("current_page", 1),
                jobs_obj.get("last_page", 1),
                jobs_obj.get("total", 0),
            )
        if isinstance(jobs_obj, list):
            return jobs_obj, 1, 1, len(jobs_obj)
    except Exception as e:
        print(f"[Parse error] {e}")
    return [], 1, 1, 0


def parse_job(job, category_name=""):
    employer = job.get("company") or job.get("employer") or job.get("employerName") or ""
    if isinstance(employer, dict):
        employer = employer.get("name") or employer.get("company_name") or ""

    category = category_name or job.get("category") or ""
    if isinstance(category, dict):
        category = category.get("name") or ""

    work_type = job.get("work_type") or job.get("workType") or job.get("type") or ""
    if isinstance(work_type, dict):
        work_type = work_type.get("name") or ""
    if isinstance(work_type, list):
        work_type = ", ".join(
            w.get("name") if isinstance(w, dict) else str(w) for w in work_type
        )

    remote = job.get("work_from") or job.get("remote") or job.get("remoteWork") or ""
    if isinstance(remote, dict):
        remote = remote.get("name") or ""

    slug   = job.get("slug") or ""
    job_id = job.get("id") or ""
    job_url = f"{BASE_URL}/job/{slug}" if slug else (f"{BASE_URL}/job/{job_id}" if job_id else "")

    return {
        "id":              job_id,
        "title":           job.get("job_position") or job.get("title") or "",
        "employer":        employer,
        "category":        category,
        "location":        job.get("location") or "",
        "salary_from":     job.get("salary_min") or job.get("salaryFrom") or "",
        "salary_to":       job.get("salary_max") or job.get("salaryTo") or "",
        "salary_currency": "EUR" if (job.get("salary_min") or job.get("salary_max")) else "",
        "work_type":       work_type,
        "remote":          remote,
        "publish_date":    (job.get("created_at") or job.get("publishDate") or "")[:10],
        "expiration_date": (job.get("deadline") or job.get("expirationDate") or "")[:10],
        "job_url":         job_url,
        "source":          "likeit.lv",
    }


def scrape_category(session, slug, name):
    """Scrape one category using a fresh session with no keyword filter."""
    jobs_out = []
    seen     = set()
    page     = 1

    while True:
        # Use a fresh session per category to avoid any cached filter state
        params = {
            "keyword":    "",       # explicitly empty keyword
            "category":   slug,
            "work_from":  "",
            "type":       "",
            "salary_min": "",
            "sort":       "date",
            "page":       page,
        }

        data = get_next_data(session, f"{BASE_URL}/jobs", params=params)
        if not data:
            print(f"    Page {page}: FAILED")
            break

        jobs_list, cur, last, total = extract_jobs_and_pagination(data)

        if page == 1:
            print(f"    total={total}, pages={last}", end=" ", flush=True)

        if not jobs_list:
            break

        for j in jobs_list:
            p = parse_job(j, name)
            jid = str(p["id"]) or p["job_url"]
            if jid not in seen:
                seen.add(jid)
                jobs_out.append(p)

        if page >= last:
            break
        page += 1
        time.sleep(1)

    return jobs_out


def scrape_all():
    print("=" * 60)
    print("LIKEIT.LV SCRAPER v6")
    print("=" * 60)
    print()

    all_jobs = []
    seen_ids = set()

    for i, (slug, name) in enumerate(CATEGORIES.items(), 1):
        print(f"[{i:02}/{len(CATEGORIES)}] {name:<30}", end=" ")

        # Fresh session per category — avoids any session filter carryover
        session = make_session()

        jobs = scrape_category(session, slug, name)

        # Deduplicate across categories (some jobs appear in multiple)
        new = 0
        for j in jobs:
            jid = str(j["id"]) or j["job_url"]
            if jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(j)
                new += 1

        print(f"-> {new} jobs")
        time.sleep(2)

    # ── Save ──────────────────────────────────────────────────────────────
    print()
    if all_jobs:
        csv_file = "likeit_jobs.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_jobs[0].keys()))
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"[SAVED] {len(all_jobs)} jobs -> {csv_file}")

        with open("likeit_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        print(f"[SAVED] JSON backup -> likeit_jobs.json")

        from collections import Counter
        cats = Counter(j["category"] for j in all_jobs if j["category"])
        print("\nCATEGORY BREAKDOWN:")
        print("-" * 42)
        for cat, count in cats.most_common():
            print(f"  {cat:<32} {count:>4}")
        print("-" * 42)
        print(f"  {'TOTAL':<32} {len(all_jobs):>4}")
    else:
        print("[WARNING] No jobs collected.")
        print()
        print("NEXT STEP: Open likeit.lv in your browser,")
        print("click 'Clear Filters', then open likeit_sample_job.json")
        print("to confirm the keyword filter is gone.")

    return all_jobs


if __name__ == "__main__":
    scrape_all()