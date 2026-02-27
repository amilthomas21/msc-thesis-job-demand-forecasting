import csv, requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

INPUT = "data/raw/ss_lv_jobs_full.csv"
OUTPUT = "data/raw/ss_lv_jobs_fixed.csv"

def fix(url):
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
        soup = BeautifulSoup(r.content, "html.parser")
        title = ""
        for lab in soup.find_all("td", class_="ads_opt_name"):
            if "Profesija" in lab.get_text():
                val = lab.find_next_sibling("td")
                if val: title = val.get_text(strip=True)
                break
        date = ""
        for td in soup.find_all("td", class_="msg_footer"):
            txt = td.get_text(strip=True)
            if "Datums:" in txt:
                raw = txt.split("Datums:")[-1].strip()
                try: date = datetime.strptime(raw.split()[0], "%d.%m.%Y").date().isoformat()
                except: date = raw
                break
        return title, date
    except: return "", ""

rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
for i, r in enumerate(rows, 1):
    t, d = fix(r.get("url",""))
    if t: r["title"] = t
    if d: r["posted_date"] = d
    if i % 20 == 0: print(f"{i}/{len(rows)} - {t} - {d}")
    sleep(0.5)

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("DONE!", OUTPUT)
```

3. Press **Ctrl+S** and save as `fix_ss_lv_data.py` in your project root folder:
```
G:\OneDrive\Desktop\master thesis\thesis_scraping\msc-thesis-job-demand-forecasting\fix_ss_lv_data.py