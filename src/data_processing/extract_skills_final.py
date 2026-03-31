"""
Skill Extraction Script v3 — FINAL
Uses validated skill dictionary after diagnostic analysis.

Key fix: Latvian text caused severe false positives for short terms like "Go" and "BI".
Solution: Removed problematic short terms, replaced with full unambiguous names.

Run: python src/data_processing/extract_skills_final.py
"""

import pandas as pd
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill_keywords_v3 import SKILL_DICTIONARY, FALSE_POSITIVES, get_flat_skills

# ── Latvian keyword translations (SS.lv descriptions) ─────────────────────────
LATVIAN_TO_SKILL = {
    "angļu valoda":         ("English", "Languages"),
    "latviešu valoda":      ("Latvian", "Languages"),
    "krievu valoda":        ("Russian", "Languages"),
    "vācu valoda":          ("German", "Languages"),
    "franču valoda":        ("French", "Languages"),
    "datu analīze":         ("Data analysis", "Data Science & AI"),
    "projektu vadība":      ("Project management", "Project Management"),
    "grāmatvedība":         ("Accounting", "Business & Finance"),
    "loģistikas vadība":    ("Logistics management", "Logistics & Supply Chain"),
    "piegādes ķēde":        ("Supply chain", "Logistics & Supply Chain"),
    "noliktavas vadība":    ("Warehouse management", "Logistics & Supply Chain"),
    "iepirkumi":            ("Procurement", "Logistics & Supply Chain"),
    "finanšu analīze":      ("Financial analysis", "Business & Finance"),
    "mākslīgais intelekts": ("Machine learning", "Data Science & AI"),
    "datu zinātne":         ("Data science", "Data Science & AI"),
    "kiberdrošība":         ("Cybersecurity", "Networking & Security"),
    "programmēšana":        ("Software development", "Software Engineering"),
}


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove URLs — critical for avoiding HTTPS false positives
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\./\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills_from_text(text: str, skill_list: list) -> list:
    normalized = normalize_text(text)
    found = []
    seen = set()

    for skill, category in skill_list:
        if skill in FALSE_POSITIVES:
            continue
        skill_lower = skill.lower()
        if skill_lower in seen:
            continue
        try:
            pattern = r'(?<![a-z])' + re.escape(skill_lower) + r'(?![a-z])'
            if re.search(pattern, normalized):
                found.append((skill, category))
                seen.add(skill_lower)
        except re.error:
            if skill_lower in normalized:
                found.append((skill, category))
                seen.add(skill_lower)

    # Latvian keyword detection
    for lv_term, (mapped_skill, mapped_cat) in LATVIAN_TO_SKILL.items():
        if lv_term in normalized and mapped_skill.lower() not in seen:
            found.append((mapped_skill, mapped_cat))
            seen.add(mapped_skill.lower())

    return found


def extract_all_skills(df: pd.DataFrame) -> pd.DataFrame:
    skill_list = get_flat_skills()
    print(f"Dictionary: {len(skill_list)} validated skills | {len(SKILL_DICTIONARY)} categories")
    print(f"Processing {len(df):,} job descriptions...\n")

    records = []
    no_skill_count = 0

    for idx, row in df.iterrows():
        if idx % 500 == 0:
            print(f"  {idx}/{len(df)}...")

        text = str(row.get('title', '')) + ' ' + str(row.get('description', ''))
        found = extract_skills_from_text(text, skill_list)

        if not found:
            no_skill_count += 1

        for skill, category in found:
            records.append({
                'job_id':         idx,
                'source':         row.get('source', ''),
                'job_category':   row.get('category', ''),
                'title':          row.get('title', ''),
                'date':           row.get('posted_date', row.get('scraped_date', '')),
                'skill':          skill,
                'skill_category': category,
            })

    df_out = pd.DataFrame(records)
    total_jobs = len(df)
    covered = df_out['job_id'].nunique()

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total skill mentions:   {len(df_out):,}")
    print(f"Unique skills found:    {df_out['skill'].nunique()}")
    print(f"Jobs with skills:       {covered:,} / {total_jobs:,}  ({covered/total_jobs*100:.1f}%)")
    print(f"Jobs without skills:    {no_skill_count:,} / {total_jobs:,}")
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


def print_final_report(summary: pd.DataFrame):
    cols = ['rank', 'skill', 'skill_category', 'frequency', 'job_coverage_pct', 'demand_tier']

    print(f"\n{'='*70}")
    print("FINAL: TOP 30 IN-DEMAND SKILLS — RIGA JOB MARKET (excl. languages)")
    print(f"{'='*70}")
    tech = summary[summary['skill_category'] != 'Languages']
    print(tech[cols].head(30).to_string(index=False))

    print(f"\n{'='*70}")
    print("LANGUAGE REQUIREMENTS")
    print(f"{'='*70}")
    langs = summary[summary['skill_category'] == 'Languages']
    print(langs[cols].to_string(index=False))

    print(f"\n{'='*70}")
    print("TOP 5 PER TECHNICAL CATEGORY")
    print(f"{'='*70}")
    skip = {'Languages', 'Professional Skills', 'Certifications'}
    for cat in SKILL_DICTIONARY:
        if cat in skip:
            continue
        sub = summary[summary['skill_category'] == cat].head(5)
        if not sub.empty:
            print(f"\n▶ {cat}")
            print(sub[['skill', 'frequency', 'job_coverage_pct', 'demand_tier']].to_string(index=False))

    print(f"\n{'='*70}")
    print("DEMAND TIER DISTRIBUTION")
    print(f"{'='*70}")
    print(summary['demand_tier'].value_counts().to_string())

    print(f"\n{'='*70}")
    print("UNIQUE SKILLS PER CATEGORY")
    print(f"{'='*70}")
    print(summary.groupby('skill_category')['skill'].count()
          .sort_values(ascending=False).to_string())


def main():
    input_path     = 'data/processed/master_jobs_clean.csv'
    out_skills     = 'data/processed/job_skills_final.csv'
    out_summary    = 'data/processed/skill_demand_final.csv'

    print("=" * 70)
    print("SKILL EXTRACTION — FINAL VERSION (v3 validated dictionary)")
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

    print_final_report(summary_df)


if __name__ == "__main__":
    main()