"""
Skill Extraction Script v4 — COVERAGE BOOSTER
Target: 68% → 88%+ coverage

Key improvements over v3:
1. Massively expanded Latvian keyword dictionary (100+ new terms)
2. Russian keyword support (SS.lv Russian postings)
3. Synonym/phrase matching layer
4. Job title skill inference (if description is empty/short, infer from title)
5. Deduplication still applied — no double counting

Run: python src/data_processing/extract_skills_v4.py
"""

import pandas as pd
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill_keywords_v3 import SKILL_DICTIONARY, FALSE_POSITIVES, get_flat_skills
from latvian_skills import LATVIAN_SKILL_MAP

# ── SYNONYM / PHRASE MAP ─────────────────────────────────────────────────────
# Catches natural-language descriptions that aren't single keywords
# Format: "phrase in job description" → ("Canonical skill", "Category")

SYNONYM_MAP = {
    # Accounting / Finance synonyms
    "financial statements":         ("Financial reporting", "Business & Finance"),
    "financial planning":           ("Financial analysis", "Business & Finance"),
    "financial control":            ("Controlling", "Business & Finance"),
    "management accounting":        ("Accounting", "Business & Finance"),
    "general ledger":               ("Accounting", "Business & Finance"),
    "accounts payable":             ("Accounting", "Business & Finance"),
    "accounts receivable":          ("Accounting", "Business & Finance"),
    "annual report":                ("Financial reporting", "Business & Finance"),
    "balance sheet":                ("Financial reporting", "Business & Finance"),
    "cash flow":                    ("Financial analysis", "Business & Finance"),
    "cost accounting":              ("Accounting", "Business & Finance"),
    "tax returns":                  ("Tax", "Business & Finance"),
    "tax accounting":               ("Tax", "Business & Finance"),
    "tax reporting":                ("Tax", "Business & Finance"),
    "tax compliance":               ("Tax", "Business & Finance"),
    "vat reporting":                ("Tax", "Business & Finance"),
    "value added tax":              ("Tax", "Business & Finance"),
    "pievienotās vērtības nodoklis":("Tax", "Business & Finance"),
    "pvn":                          ("Tax", "Business & Finance"),
    "payroll processing":           ("Payroll", "Business & Finance"),
    "payroll management":           ("Payroll", "Business & Finance"),
    "salary calculation":           ("Payroll", "Business & Finance"),

    # Project management synonyms
    "project planning":             ("Project management", "Project Management"),
    "project coordinator":          ("Project management", "Project Management"),
    "project lead":                 ("Project management", "Project Management"),
    "project delivery":             ("Project management", "Project Management"),
    "deadline management":          ("Project management", "Project Management"),

    # Software / Dev synonyms
    "source control":               ("Git", "Software Engineering"),
    "version control":              ("Git", "Software Engineering"),
    "continuous integration":       ("CI/CD", "Cloud & DevOps"),
    "continuous deployment":        ("CI/CD", "Cloud & DevOps"),
    "object oriented":              ("Software development", "Software Engineering"),
    "software testing":             ("Unit testing", "Software Engineering"),
    "quality assurance":            ("Unit testing", "Software Engineering"),
    "qa testing":                   ("Unit testing", "Software Engineering"),
    "test automation":              ("Unit testing", "Software Engineering"),
    "api integration":              ("REST API", "Web Development"),
    "web application":              ("Web development", "Web Development"),
    "mobile application":           ("Web development", "Web Development"),
    "mobile app":                   ("Web development", "Web Development"),
    "full stack":                   ("Software development", "Software Engineering"),
    "fullstack":                    ("Software development", "Software Engineering"),
    "back end":                     ("Software development", "Software Engineering"),
    "backend":                      ("Software development", "Software Engineering"),
    "front end":                    ("Web development", "Web Development"),
    "frontend":                     ("Web development", "Web Development"),

    # Data synonyms
    "data driven":                  ("Data analysis", "Data Science & AI"),
    "data driven decision":         ("Data analysis", "Data Science & AI"),
    "reporting tool":               ("Reporting", "Business & Finance"),
    "reporting and analysis":       ("Data analysis", "Data Science & AI"),
    "bi tool":                      ("Business Intelligence", "Data Science & AI"),
    "business intelligence":        ("Business Intelligence", "Data Science & AI"),
    "data warehouse":               ("Data warehousing", "Databases"),
    "relational database":          ("SQL", "Databases"),
    "relational databases":         ("SQL", "Databases"),
    "database management":          ("Database administration", "Databases"),

    # Cloud synonyms
    "cloud platform":               ("Cloud & DevOps", "Cloud & DevOps"),
    "cloud infrastructure":         ("Cloud & DevOps", "Cloud & DevOps"),
    "cloud services":               ("Cloud & DevOps", "Cloud & DevOps"),
    "container":                    ("Docker", "Cloud & DevOps"),
    "containerization":             ("Docker", "Cloud & DevOps"),
    "container orchestration":      ("Kubernetes", "Cloud & DevOps"),

    # Networking synonyms
    "network protocols":            ("Network administration", "Networking & Security"),
    "network infrastructure":       ("Network administration", "Networking & Security"),
    "it security":                  ("Information security", "Networking & Security"),
    "information security":         ("Information security", "Networking & Security"),
    "data security":                ("Information security", "Networking & Security"),
    "data protection":              ("Information security", "Networking & Security"),
    "gdpr":                         ("GDPR compliance", "Networking & Security"),

    # Logistics synonyms
    "supply chain management":      ("Supply chain", "Logistics & Supply Chain"),
    "warehouse operations":         ("Warehouse management", "Logistics & Supply Chain"),
    "inventory control":            ("Inventory management", "Logistics & Supply Chain"),
    "stock management":             ("Inventory management", "Logistics & Supply Chain"),
    "freight management":           ("Freight", "Logistics & Supply Chain"),
    "customs clearance":            ("Customs", "Logistics & Supply Chain"),

    # Engineering synonyms
    "technical drawing":            ("Technical drawing", "Engineering"),
    "cad software":                 ("AutoCAD", "Engineering"),
    "cad program":                  ("AutoCAD", "Engineering"),
    "cad tools":                    ("AutoCAD", "Engineering"),
    "building information":         ("BIM", "Engineering"),
    "embedded software":            ("Embedded systems", "Engineering"),
    "industrial control":           ("PLC programming", "Engineering"),
    "electrical design":            ("Electrical engineering", "Engineering"),

    # Professional skills synonyms
    "client communication":         ("Communication skills", "Professional Skills"),
    "written communication":        ("Communication skills", "Professional Skills"),
    "verbal communication":         ("Communication skills", "Professional Skills"),
    "communication skills":         ("Communication skills", "Professional Skills"),
    "interpersonal skills":         ("Communication skills", "Professional Skills"),
    "team player":                  ("Teamwork", "Professional Skills"),
    "work in a team":               ("Teamwork", "Professional Skills"),
    "ability to work in a team":    ("Teamwork", "Professional Skills"),
    "customer oriented":            ("Customer service", "Professional Skills"),
    "customer focused":             ("Customer service", "Professional Skills"),
    "client service":               ("Customer service", "Professional Skills"),
    "attention to detail":          ("Attention to detail", "Professional Skills"),
    "detail oriented":              ("Attention to detail", "Professional Skills"),
    "strong analytical":            ("Analytical thinking", "Professional Skills"),
    "analytical skills":            ("Analytical thinking", "Professional Skills"),

    # Language synonyms (common in English-posted CV.lv jobs)
    "latvian language":             ("Latvian", "Languages"),
    "english language":             ("English", "Languages"),
    "russian language":             ("Russian", "Languages"),
    "german language":              ("German", "Languages"),
    "knowledge of latvian":         ("Latvian", "Languages"),
    "knowledge of english":         ("English", "Languages"),
    "knowledge of russian":         ("Russian", "Languages"),
    "fluent in english":            ("English", "Languages"),
    "fluent in latvian":            ("Latvian", "Languages"),
    "fluent in russian":            ("Russian", "Languages"),
    "proficient in english":        ("English", "Languages"),
    "b2 english":                   ("English", "Languages"),
    "c1 english":                   ("English", "Languages"),
}


# ── JOB TITLE → SKILL INFERENCE ───────────────────────────────────────────────
# When description is too short (<50 chars), infer skills from job title
# These are the most common job title patterns in Latvian job market

TITLE_SKILL_MAP = {
    "grāmatved":            [("Accounting", "Business & Finance"), ("Excel", "Business & Finance")],
    "accountant":           [("Accounting", "Business & Finance"), ("Excel", "Business & Finance")],
    "finanšu":              [("Financial analysis", "Business & Finance"), ("Excel", "Business & Finance")],
    "financial analyst":    [("Financial analysis", "Business & Finance"), ("Excel", "Business & Finance")],
    "programmētāj":         [("Software development", "Software Engineering"), ("Git", "Software Engineering")],
    "developer":            [("Software development", "Software Engineering"), ("Git", "Software Engineering")],
    "izstrādātāj":          [("Software development", "Software Engineering"), ("Git", "Software Engineering")],
    "loģistiķ":             [("Supply chain", "Logistics & Supply Chain"), ("Excel", "Business & Finance")],
    "logistics":            [("Supply chain", "Logistics & Supply Chain"), ("Excel", "Business & Finance")],
    "noliktav":             [("Warehouse management", "Logistics & Supply Chain")],
    "warehouse":            [("Warehouse management", "Logistics & Supply Chain")],
    "projektu vadītāj":     [("Project management", "Project Management")],
    "project manager":      [("Project management", "Project Management")],
    "sistēmu administrators":  [("IT Administration", "IT Administration"), ("Linux", "Cloud & DevOps")],
    "system administrator": [("IT Administration", "IT Administration"), ("Linux", "Cloud & DevOps")],
    "sysadmin":             [("IT Administration", "IT Administration"), ("Linux", "Cloud & DevOps")],
    "mārketinga":           [("Digital marketing", "Marketing & Communication"), ("CRM", "Marketing & Communication")],
    "marketing":            [("Digital marketing", "Marketing & Communication"), ("CRM", "Marketing & Communication")],
    "dizainer":             [("Graphic design", "Design & Creative"), ("Photoshop", "Design & Creative")],
    "designer":             [("Graphic design", "Design & Creative"), ("Figma", "Design & Creative")],
    "ui/ux":                [("UI/UX", "Design & Creative"), ("Figma", "Design & Creative")],
    "data analyst":         [("Data analysis", "Data Science & AI"), ("SQL", "Databases"), ("Excel", "Business & Finance")],
    "datu analītiķ":        [("Data analysis", "Data Science & AI"), ("SQL", "Databases")],
    "pārdevēj":             [("Customer service", "Professional Skills"), ("CRM", "Marketing & Communication")],
    "sales":                [("Customer service", "Professional Skills"), ("CRM", "Marketing & Communication")],
    "klientu apkalpošan":   [("Customer service", "Professional Skills")],
    "customer service":     [("Customer service", "Professional Skills")],
    "mehāniķ":              [("Mechanical engineering", "Engineering")],
    "mechanic":             [("Mechanical engineering", "Engineering")],
    "elektriķ":             [("Electrical engineering", "Engineering")],
    "electrician":          [("Electrical engineering", "Engineering")],
    "inženier":             [("Civil engineering", "Engineering"), ("AutoCAD", "Engineering")],
    "engineer":             [("Civil engineering", "Engineering")],
    "jurist":               [("Compliance", "Business & Finance")],
    "lawyer":               [("Compliance", "Business & Finance")],
    "hr specialist":        [("Communication skills", "Professional Skills")],
    "personāla":            [("Communication skills", "Professional Skills")],
    "vadītāj":              [("Leadership", "Professional Skills"), ("Project management", "Project Management")],
    "manager":              [("Leadership", "Professional Skills"), ("Project management", "Project Management")],
    "analītiķ":             [("Data analysis", "Data Science & AI"), ("Excel", "Business & Finance")],
    "analyst":              [("Data analysis", "Data Science & AI"), ("Excel", "Business & Finance")],
    "cybersecurity":        [("Cybersecurity", "Networking & Security")],
    "network":              [("Network administration", "Networking & Security")],
    "devops":               [("DevOps", "Cloud & DevOps"), ("Docker", "Cloud & DevOps"), ("CI/CD", "Cloud & DevOps")],
}


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\./\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills_from_text(text: str, title: str, skill_list: list) -> list:
    normalized_text = normalize_text(text)
    normalized_title = normalize_text(title)
    full_text = normalized_title + " " + normalized_text
    
    found = []
    seen = set()

    # ── 1. English keyword matching (existing logic) ───────────────────────
    for skill, category in skill_list:
        if skill in FALSE_POSITIVES:
            continue
        if skill == "Driving License":   # Not a professional skill for thesis analysis
            continue
        if skill in FALSE_POSITIVES:
            continue
        skill_lower = skill.lower()
        if skill_lower in seen:
            continue
        try:
            pattern = r'(?<![a-z0-9])' + re.escape(skill_lower) + r'(?![a-z0-9])'
            if re.search(pattern, full_text):
                found.append((skill, category))
                seen.add(skill_lower)
        except re.error:
            if skill_lower in full_text:
                found.append((skill, category))
                seen.add(skill_lower)

    # ── 2. Latvian + Russian keyword matching ──────────────────────────────
    for lv_term, (mapped_skill, mapped_cat) in LATVIAN_SKILL_MAP.items():
        if mapped_skill == "Driving License":
            continue
        if lv_term in full_text and mapped_skill.lower() not in seen:
            found.append((mapped_skill, mapped_cat))
            seen.add(mapped_skill.lower())

    # ── 3. Synonym / phrase matching ───────────────────────────────────────
    for phrase, (mapped_skill, mapped_cat) in SYNONYM_MAP.items():
        if phrase in full_text and mapped_skill.lower() not in seen:
            found.append((mapped_skill, mapped_cat))
            seen.add(mapped_skill.lower())

    # ── 4. Title inference (for short/empty descriptions) ─────────────────
    desc_len = len(normalized_text.strip())
    if desc_len < 200:  # Description too short — use title to infer skills
        for title_pattern, inferred_skills in TITLE_SKILL_MAP.items():
            if title_pattern in normalized_title:
                for skill, cat in inferred_skills:
                    if skill.lower() not in seen:
                        found.append((skill, cat))
                        seen.add(skill.lower())

    return found


def extract_all_skills(df: pd.DataFrame) -> pd.DataFrame:
    skill_list = get_flat_skills()
    print(f"English dictionary:  {len(skill_list)} skills")
    print(f"Latvian/RU keywords: {len(LATVIAN_SKILL_MAP)} terms")
    print(f"Synonym phrases:     {len(SYNONYM_MAP)} phrases")
    print(f"Title inference:     {len(TITLE_SKILL_MAP)} patterns")
    print(f"Processing {len(df):,} job descriptions...\n")

    records = []
    no_skill_count = 0
    title_inferred_count = 0

    for idx, row in df.iterrows():
        if idx % 500 == 0:
            print(f"  {idx}/{len(df)}...")

        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        text = title + ' ' + description

        found = extract_skills_from_text(text, title, skill_list)

        if not found:
            no_skill_count += 1

        # Track title-inferred jobs
        desc_len = len(normalize_text(description).strip())
        if found and desc_len < 100:
            title_inferred_count += 1

        for skill, category in found:
            records.append({
                'job_id':         idx,
                'source':         row.get('source', ''),
                'job_category':   row.get('category', ''),
                'title':          title,
                'date':           row.get('posted_date', row.get('scraped_date', '')),
                'skill':          skill,
                'skill_category': category,
            })

    df_out = pd.DataFrame(records)
    total_jobs = len(df)
    covered = df_out['job_id'].nunique()

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE — v4 COVERAGE BOOSTER")
    print(f"{'='*60}")
    print(f"Total skill mentions:   {len(df_out):,}")
    print(f"Unique skills found:    {df_out['skill'].nunique()}")
    print(f"Jobs with skills:       {covered:,} / {total_jobs:,}  ({covered/total_jobs*100:.1f}%)")
    print(f"Jobs without skills:    {no_skill_count:,} / {total_jobs:,}")
    print(f"Jobs via title inference: ~{title_inferred_count:,}")
    return df_out


def build_demand_summary(skills_df: pd.DataFrame) -> pd.DataFrame:
    total_jobs = skills_df['job_id'].nunique()
    summary = (
        skills_df.groupby(['skill', 'skill_category'])
        .agg(frequency=('job_id', 'count'), job_count=('job_id', 'nunique'))
        .reset_index()
    )
    summary['job_coverage_pct'] = (summary['job_count'] / total_jobs * 100).round(2)
    summary = summary.sort_values('frequency', ascending=False).reset_index(drop=True)
    summary['rank'] = summary.index + 1

    p75 = summary['frequency'].quantile(0.75)
    p25 = summary['frequency'].quantile(0.25)

    def tier(f):
        if f >= p75:   return 'High Demand'
        elif f >= p25: return 'Moderate Demand'
        else:          return 'Low Demand'

    summary['demand_tier'] = summary['frequency'].apply(tier)
    return summary


def print_report(summary: pd.DataFrame, total_jobs: int):
    cols = ['rank', 'skill', 'skill_category', 'frequency', 'job_coverage_pct', 'demand_tier']

    print(f"\n{'='*70}")
    print("TOP 30 IN-DEMAND SKILLS — v4 (excl. languages)")
    print(f"{'='*70}")
    tech = summary[summary['skill_category'] != 'Languages']
    print(tech[cols].head(30).to_string(index=False))

    print(f"\n{'='*70}")
    print("LANGUAGE REQUIREMENTS")
    print(f"{'='*70}")
    langs = summary[summary['skill_category'] == 'Languages']
    print(langs[cols].to_string(index=False))

    print(f"\n{'='*70}")
    print("COVERAGE COMPARISON")
    print(f"{'='*70}")
    covered = summary['job_count'].max() if len(summary) > 0 else 0
    jobs_with_skills = summary.groupby('skill')['job_count'].first()
    # Count unique job_ids covered
    print(f"  v3 baseline:   ~2,089 / 3,057  (68.3%)")
    print(f"  v4 result:     see above")


def main():
    input_path  = 'data/processed/master_jobs_clean.csv'
    out_skills  = 'data/processed/job_skills_v4.csv'
    out_summary = 'data/processed/skill_demand_v4.csv'

    print("=" * 70)
    print("SKILL EXTRACTION v4 — COVERAGE BOOSTER")
    print("=" * 70)

    df = pd.read_csv(input_path)
    print(f"Loaded: {len(df):,} jobs | Sources: {df['source'].value_counts().to_dict()}")

    skills_df = extract_all_skills(df)

    os.makedirs('data/processed', exist_ok=True)
    skills_df.to_csv(out_skills, index=False)

    summary_df = build_demand_summary(skills_df)
    summary_df.to_csv(out_summary, index=False)

    print(f"\nSaved → {out_skills}")
    print(f"Saved → {out_summary}")

    print_report(summary_df, len(df))


if __name__ == "__main__":
    main()