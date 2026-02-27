import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import logging
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────

BASE_URL = "https://www.ss.lv"
OUTPUT_FILE = "data/raw/ss_lv_jobs_full.csv"
ERROR_LOG   = "data/raw/ss_lv_errors.log"
MAX_PAGES   = 7          # pages per category (index scrape)
DELAY_INDEX = 1.5        # seconds between index page requests
DELAY_DETAIL = 2.0       # seconds between individual job page requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

JOB_CATEGORIES = {
    "programmer":           "Programmer",
    "computer-technician":  "Computer Technician",
    "network-administrator":"Network Administrator",
    "web-designer":         "Web Designer",
    "linux-admin":          "Linux Administrator",
    "engineer":             "Engineer",
    "constructor":          "Constructor",
    "electrician":          "Electrician",
    "mechanics":            "Mechanic",
    "logist":               "Logistician",
    "driver":               "Driver",
    "dispatcher":           "Dispatcher",
    "e-forwarding-agent":   "Forwarding Agent",
    "bookkeeper":           "Accountant",
    "ekonomist":            "Economist",
    "manager":              "Manager",
    "financial-analyst":    "Financial Analyst",
    "architect":            "Architect",
    "designer":             "Designer",
    "administrator":        "Administrator",
    "adviser":              "Consultant",
    "director":             "Director",
    "expert":               "Specialist",
}

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    filename=ERROR_LOG,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_page(url, retries=3):
    """Fetch a URL with retries. Returns BeautifulSoup or None."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return BeautifulSoup(resp.content, "html.parser")
            elif resp.status_code == 404:
                return None  # listing removed, don't retry
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(3)
    return None


def load_existing_urls(filepath):
    """Load already-scraped URLs so we can skip them (resume support)."""
    seen = set()
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen.add(row["url"])
    return seen


# ── Stage 1: Collect job URLs from listing pages ──────────────────────────────

def collect_urls_for_category(slug, category_name):
    """
    Scrape listing pages for a category and return a list of unique job URLs.
    """
    urls = []
    seen_on_this_run = set()

    for page_num in range(1, MAX_PAGES + 1):
        if page_num == 1:
            page_url = f"{BASE_URL}/lv/work/are-required/{slug}/"
        else:
            page_url = f"{BASE_URL}/lv/work/are-required/{slug}/page{page_num}.html"

        soup = get_page(page_url)
        if soup is None:
            break

        # SS.lv job links are in <a> tags whose href matches /msg/lv/work/...
        links = soup.find_all("a", href=True)
        job_links = [
            a["href"] for a in links
            if "/msg/lv/work/are-required/" in a["href"]
        ]

        if not job_links:
            break  # empty page, stop paginating

        new_found = 0
        for href in job_links:
            full_url = BASE_URL + href if href.startswith("/") else href
            if full_url not in seen_on_this_run:
                seen_on_this_run.add(full_url)
                urls.append(full_url)
                new_found += 1

        print(f"    Page {page_num}: {new_found} new URLs found")

        if new_found == 0:
            break  # all duplicates = we've hit the end

        time.sleep(DELAY_INDEX)

    return urls


# ── Stage 2: Scrape individual job detail pages ───────────────────────────────

def scrape_job_detail(url):
    """
    Visit a single job posting page and extract:
      - title
      - posted_date  (format: YYYY-MM-DD if found, else empty string)
      - description  (cleaned full text)

    Returns a dict or None if the page couldn't be parsed.
    """
    soup = get_page(url)
    if soup is None:
        return None

    # ── Title ──
    # SS.lv puts the job title in <h2 class="headline"> or the <title> tag
    title = ""
    h2 = soup.find("h2", class_="headline")
    if h2:
        title = h2.get_text(strip=True)
    if not title:
        # fallback: page <title> minus " - SS.LV"
        page_title = soup.find("title")
        if page_title:
            title = page_title.get_text(strip=True).replace(" - SS.LV", "").strip()

    # ── Posted date ──
    # SS.lv shows date in a <td> that contains text like "12.02.2025"
    # It appears inside a table with class "options_list" or near "Datums"
    posted_date = ""
    date_label = soup.find(string=lambda t: t and "Datums" in t)  # "Datums" = Date in Latvian
    if date_label:
        # The date value is usually in the next <td>
        parent_td = date_label.find_parent("td")
        if parent_td:
            next_td = parent_td.find_next_sibling("td")
            if next_td:
                raw_date = next_td.get_text(strip=True)
                # Convert DD.MM.YYYY → YYYY-MM-DD
                try:
                    parsed = datetime.strptime(raw_date, "%d.%m.%Y")
                    posted_date = parsed.strftime("%Y-%m-%d")
                except ValueError:
                    posted_date = raw_date  # keep raw if format differs

    # ── Description ──
    # Main job text is usually in <div id="msg_div_msg"> or <div class="msg_div_msg">
    description = ""
    msg_div = soup.find("div", id="msg_div_msg")
    if not msg_div:
        msg_div = soup.find("div", class_="msg_div_msg")
    if msg_div:
        description = msg_div.get_text(separator=" ", strip=True)
    
    # Clean up whitespace
    description = " ".join(description.split())

    return {
        "title": title,
        "posted_date": posted_date,
        "description": description,
    }


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_scraper():
    os.makedirs("data/raw", exist_ok=True)

    # Load already-scraped URLs for resume support
    existing_urls = load_existing_urls(OUTPUT_FILE)
    print(f"[RESUME] {len(existing_urls)} URLs already in dataset — will skip these.\n")

    # Open CSV for appending
    file_exists = os.path.exists(OUTPUT_FILE)
    csv_file = open(OUTPUT_FILE, "a", newline="", encoding="utf-8")
    fieldnames = ["category", "title", "url", "posted_date", "scraped_date", "description"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()

    scraped_date = datetime.now().strftime("%Y-%m-%d")
    total_new = 0

    print("=" * 65)
    print("SS.LV FULL SCRAPER - Collecting job details")
    print("=" * 65)

    for i, (slug, category_name) in enumerate(JOB_CATEGORIES.items(), 1):
        print(f"\n[{i}/{len(JOB_CATEGORIES)}] {category_name}")
        print(f"  Stage 1: Collecting URLs from listing pages...")

        all_urls = collect_urls_for_category(slug, category_name)
        new_urls = [u for u in all_urls if u not in existing_urls]

        print(f"  Found {len(all_urls)} URLs total, {len(new_urls)} are new.")

        if not new_urls:
            print(f"  [SKIP] All URLs already scraped.")
            continue

        print(f"  Stage 2: Scraping {len(new_urls)} job detail pages...")

        cat_success = 0
        cat_failed  = 0

        for j, url in enumerate(new_urls, 1):
            detail = scrape_job_detail(url)

            if detail is None:
                logging.error(f"Failed to scrape: {url}")
                cat_failed += 1
            else:
                writer.writerow({
                    "category":     category_name,
                    "title":        detail["title"],
                    "url":          url,
                    "posted_date":  detail["posted_date"],
                    "scraped_date": scraped_date,
                    "description":  detail["description"],
                })
                csv_file.flush()  # write to disk immediately
                existing_urls.add(url)
                cat_success += 1
                total_new += 1

            # Progress update every 10 jobs
            if j % 10 == 0:
                print(f"    ... {j}/{len(new_urls)} done ({cat_success} OK, {cat_failed} failed)")

            time.sleep(DELAY_DETAIL)

        print(f"  [DONE] {cat_success} jobs scraped, {cat_failed} failed for {category_name}")

    csv_file.close()

    print("\n" + "=" * 65)
    print(f"SCRAPING COMPLETE")
    print(f"  New jobs added this run : {total_new}")
    print(f"  Total in dataset        : {len(existing_urls)}")
    print(f"  Output file             : {OUTPUT_FILE}")
    print(f"  Error log               : {ERROR_LOG}")
    print("=" * 65)


if __name__ == "__main__":
    run_scraper()