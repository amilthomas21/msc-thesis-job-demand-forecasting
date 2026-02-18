"""
SS.lv Page Counter
This script checks how many pages exist for each job category
"""

import requests
from bs4 import BeautifulSoup
import time


class SSLVPageCounter:
    """Check how many pages exist for each category"""

    def __init__(self):
        self.base_url = "https://www.ss.lv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # LIMIT HERE (easy to change later)
        self.max_pages = 7

        self.job_categories = {
            'programmer': 'Programmer',
            'computer-technician': 'Computer Technician',
            'network-administrator': 'Network Administrator',
            'web-designer': 'Web Designer',
            'linux-admin': 'Linux Administrator',
            'engineer': 'Engineer',
            'constructor': 'Constructor',
            'electrician': 'Electrician',
            'mechanics': 'Mechanic',
            'logist': 'Logistician',
            'driver': 'Driver',
            'dispatcher': 'Dispatcher',
            'e-forwarding-agent': 'Forwarding Agent',
            'bookkeeper': 'Accountant',
            'ekonomist': 'Economist',
            'manager': 'Manager',
            'financial-analyst': 'Financial Analyst',
            'architect': 'Architect',
            'designer': 'Designer',
            'administrator': 'Administrator',
            'adviser': 'Consultant',
            'director': 'Director',
            'expert': 'Specialist',
        }

    def count_pages_for_category(self, category_slug):
        """
        Count pages for a category (maximum 7 pages only)
        Stops early if an empty page is found.
        """
        print(f"  Checking...", end=" ")

        pages_with_jobs = 0

        for page_num in range(1, self.max_pages + 1):

            url = f"{self.base_url}/lv/work/are-required/{category_slug}/"
            if page_num > 1:
                url += f"page{page_num}.html"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try multiple selectors
                job_rows = soup.find_all('tr', id=lambda x: x and x.startswith('tr_'))
                if not job_rows:
                    job_rows = soup.find_all('tr', class_='msg2')
                if not job_rows:
                    all_rows = soup.find_all('tr')
                    job_rows = [row for row in all_rows if row.find('a', href=True)]

                # If page has real job listings
                if len(job_rows) > 3:
                    pages_with_jobs += 1
                else:
                    break

                time.sleep(1)

            except Exception as e:
                print(f"[Error: {str(e)[:30]}]", end=" ")
                break

        return pages_with_jobs

    def count_all_categories(self):
        """Count pages for all categories"""
        print("=" * 70)
        print("SS.LV PAGE COUNTER - Finding Available Pages")
        print("=" * 70)
        print()

        results = []
        total_pages = 0

        for i, (slug, name) in enumerate(self.job_categories.items(), 1):
            print(f"[{i}/{len(self.job_categories)}] {name:30}", end=" ")

            page_count = self.count_pages_for_category(slug)

            if page_count > 0:
                print(f"[OK] {page_count} pages")
                results.append({
                    'category': name,
                    'slug': slug,
                    'pages': page_count
                })
                total_pages += page_count
            else:
                print(f"[EMPTY] No jobs found")

            time.sleep(2)

        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\nTotal categories with jobs: {len(results)}")
        print(f"Total pages across all categories: {total_pages}")
        print(f"Estimated total jobs: {total_pages * 15} - {total_pages * 20}")
        print()

        # Show detailed breakdown
        print("CATEGORY BREAKDOWN:")
        print("-" * 70)
        print(f"{'Category':<30} {'Pages':<10} {'Est. Jobs':<15}")
        print("-" * 70)

        for r in sorted(results, key=lambda x: x['pages'], reverse=True):
            est_jobs = f"{r['pages'] * 15}-{r['pages'] * 20}"
            print(f"{r['category']:<30} {r['pages']:<10} {est_jobs:<15}")

        print("-" * 70)
        print()

        # Save results
        with open('ss_lv_page_counts.txt', 'w', encoding='utf-8') as f:
            f.write("SS.LV PAGE COUNT RESULTS\n")
            f.write("=" * 70 + "\n\n")
            for r in results:
                f.write(f"{r['category']}: {r['pages']} pages\n")
            f.write(f"\nTotal pages: {total_pages}\n")
            f.write(f"Estimated jobs: {total_pages * 15} - {total_pages * 20}\n")

        print("[SAVED] Results saved to: ss_lv_page_counts.txt")
        print()

        return results


# Main execution
if __name__ == "__main__":
    counter = SSLVPageCounter()
    results = counter.count_all_categories()

    print("\n[DONE] Page counting complete!")
    print("[NEXT] Use these numbers to set max_pages in your scraper")
