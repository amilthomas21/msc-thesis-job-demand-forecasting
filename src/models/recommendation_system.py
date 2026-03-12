"""
Demand-Aware Course Recommendation System
==========================================
Takes a student career goal (typed or selected) and recommends
courses from TSI and RTU using:

  Layer 1 — Content-based filtering (TF-IDF + cosine similarity)
  Layer 2 — Demand-aware re-ranking (boost courses teaching high-demand skills)

Outputs:
  results/recommendations/recommendations_<goal>.csv
  results/recommendations/evaluation_metrics.csv

Run: python src/models/recommendation_system.py
"""

import pandas as pd
import numpy as np
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Career goal profiles ───────────────────────────────────────────────────────
# Each career maps to a set of relevant skills and keywords
CAREER_PROFILES = {
    "Data Engineer": {
        "keywords": "python sql data pipeline etl spark hadoop cloud aws azure "
                    "database data warehouse postgresql mongodb big data linux git",
        "top_skills": ["Python", "SQL", "ETL", "Apache Spark", "AWS", "Data engineering",
                       "Linux", "Git", "PostgreSQL", "Data warehousing"]
    },
    "Data Scientist": {
        "keywords": "python machine learning statistics data science deep learning "
                    "tensorflow pytorch data analysis visualization nlp sql pandas numpy",
        "top_skills": ["Python", "Machine learning", "Statistics", "Data science",
                       "Deep learning", "Data analysis", "TensorFlow", "SQL"]
    },
    "Software Developer": {
        "keywords": "programming java python javascript web development software "
                    "engineering git agile rest api oop unit testing sql backend frontend",
        "top_skills": ["Java", "Python", "JavaScript", "Git", "REST API",
                       "SQL", "OOP", "Unit testing", "Agile", "Web development"]
    },
    "IT Project Manager": {
        "keywords": "project management agile scrum leadership planning risk management "
                    "stakeholder jira communication team budget compliance reporting",
        "top_skills": ["Project management", "Agile", "Scrum", "Risk management",
                       "Leadership", "Communication skills", "Reporting", "ERP"]
    },
    "Cybersecurity Analyst": {
        "keywords": "cybersecurity information security network security penetration "
                    "testing encryption gdpr compliance firewall linux python vulnerability",
        "top_skills": ["Cybersecurity", "Information security", "Network security",
                       "Linux", "Python", "Encryption", "GDPR compliance", "Penetration testing"]
    },
    "Business Analyst": {
        "keywords": "business analysis requirements stakeholder excel sql reporting "
                    "data analysis power bi tableau erp communication project management",
        "top_skills": ["Business analysis", "Excel", "SQL", "Reporting",
                       "Power BI", "ERP", "Data analysis", "Communication skills"]
    },
    "Cloud Engineer": {
        "keywords": "cloud aws azure google cloud docker kubernetes devops terraform "
                    "linux ci/cd microservices infrastructure automation python",
        "top_skills": ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD",
                       "Linux", "DevOps", "Terraform", "Python", "Microservices"]
    },
    "Logistics Manager": {
        "keywords": "logistics supply chain warehouse inventory procurement transportation "
                    "erp sap excel reporting lean planning customs compliance",
        "top_skills": ["Logistics management", "Supply chain", "Warehouse management",
                       "Procurement", "ERP", "SAP", "Excel", "Reporting"]
    },
    "UX/UI Designer": {
        "keywords": "ux ui design figma user research prototyping web design graphic "
                    "design user experience wireframe css html adobe photoshop",
        "top_skills": ["UI/UX", "Figma", "User research", "Prototyping",
                       "Web design", "Graphic design", "HTML", "CSS"]
    },
    "Network Engineer": {
        "keywords": "networking cisco linux tcp/ip vpn firewall dns network security "
                    "wireless infrastructure monitoring troubleshooting administration",
        "top_skills": ["Linux", "Cybersecurity", "Network security", "VPN",
                       "Firewall", "DNS", "IT support", "Troubleshooting"]
    },
}

DEMAND_TIER_WEIGHTS = {
    'High Demand':     1.5,
    'Moderate Demand': 1.2,
    'Low Demand':      1.0,
}


def load_data():
    tsi = pd.read_csv('data/processed/tsi_courses.csv')
    tsi = tsi.rename(columns={'code': 'course_code', 'title': 'course_name'})
    tsi['university'] = 'TSI'
    tsi['programme']  = 'Computer Science'
    tsi['match_text'] = (
        tsi['course_name'].fillna('') + ' ' +
        tsi.get('topics', pd.Series([''] * len(tsi))).fillna('') + ' ' +
        tsi.get('description', pd.Series([''] * len(tsi))).fillna('')
    )

    rtu = pd.read_csv('data/processed/rtu_courses_final.csv')
    rtu['match_text'] = (
        rtu['course_name'].fillna('') + ' ' +
        rtu['programme'].fillna('') + ' ' +
        rtu['faculty'].fillna('')
    )

    courses = pd.concat([
        tsi[['university', 'course_code', 'course_name', 'match_text',
             'programme']],
        rtu[['university', 'course_code', 'course_name', 'match_text',
             'programme']]
    ], ignore_index=True)

    matches  = pd.read_csv('data/processed/course_skill_matches.csv')
    coverage = pd.read_csv('data/processed/skill_coverage.csv')

    return courses, matches, coverage


def get_course_demand_score(courses_df, matches_df, coverage_df):
    """
    For each course: compute a demand score based on
    how many high-demand skills it covers and their weights.
    """
    # Merge matches with demand tier
    m = matches_df.merge(
        coverage_df[['skill', 'demand_tier', 'frequency']],
        on='skill', how='left'
    )
    m['weight'] = m['demand_tier'].map(DEMAND_TIER_WEIGHTS).fillna(1.0)
    m['weighted_score'] = m['weight'] * m['frequency'].fillna(1)

    demand_scores = (
        m.groupby('course_code')['weighted_score']
        .sum()
        .reset_index()
        .rename(columns={'weighted_score': 'demand_score'})
    )

    # Normalise to 0-1
    max_score = demand_scores['demand_score'].max()
    if max_score > 0:
        demand_scores['demand_score_norm'] = demand_scores['demand_score'] / max_score
    else:
        demand_scores['demand_score_norm'] = 0

    return demand_scores


def recommend(career_goal: str,
              courses_df: pd.DataFrame,
              matches_df: pd.DataFrame,
              coverage_df: pd.DataFrame,
              university_filter: str = 'Both',
              top_k: int = 10,
              alpha: float = 0.6) -> pd.DataFrame:
    """
    Recommend courses for a given career goal.

    Parameters
    ----------
    career_goal     : free-text or predefined career name
    courses_df      : course catalogue
    matches_df      : skill-course matches
    coverage_df     : skill coverage with demand tiers
    university_filter: 'TSI', 'RTU', or 'Both'
    top_k           : number of recommendations to return
    alpha           : weight for content score (1-alpha = demand weight)
    """

    # ── Get career keywords ────────────────────────────────────────
    if career_goal in CAREER_PROFILES:
        query_text  = CAREER_PROFILES[career_goal]['keywords']
        target_skills = CAREER_PROFILES[career_goal]['top_skills']
    else:
        # Free text input — use as-is
        query_text    = career_goal.lower()
        target_skills = []

    # ── Filter by university ───────────────────────────────────────
    if university_filter != 'Both':
        filtered = courses_df[courses_df['university'] == university_filter].copy()
    else:
        filtered = courses_df.copy()

    if filtered.empty:
        print(f"No courses found for university filter: {university_filter}")
        return pd.DataFrame()

    filtered = filtered.reset_index(drop=True)

    # ── Layer 1: TF-IDF content similarity ────────────────────────
    all_docs  = filtered['match_text'].tolist() + [query_text]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        max_features=8000,
    )
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    course_vecs  = tfidf_matrix[:-1]
    query_vec    = tfidf_matrix[-1]

    content_scores = cosine_similarity(query_vec, course_vecs).flatten()
    filtered['content_score'] = content_scores

    # Normalise
    max_cs = content_scores.max()
    if max_cs > 0:
        filtered['content_score_norm'] = content_scores / max_cs
    else:
        filtered['content_score_norm'] = 0

    # ── Layer 2: Demand-aware re-ranking ──────────────────────────
    demand_scores = get_course_demand_score(filtered, matches_df, coverage_df)
    filtered = filtered.merge(demand_scores[['course_code', 'demand_score_norm']],
                               on='course_code', how='left')
    filtered['demand_score_norm'] = filtered['demand_score_norm'].fillna(0)

    # ── Combined score ─────────────────────────────────────────────
    filtered['final_score'] = (
        alpha       * filtered['content_score_norm'] +
        (1 - alpha) * filtered['demand_score_norm']
    )

    # ── Get skills covered per course ─────────────────────────────
    course_skills = (
        matches_df.groupby('course_code')['skill']
        .apply(list)
        .reset_index()
        .rename(columns={'skill': 'skills_covered'})
    )
    filtered = filtered.merge(course_skills, on='course_code', how='left')
    filtered['skills_covered'] = filtered['skills_covered'].apply(
        lambda x: x if isinstance(x, list) else []
    )
    filtered['num_skills'] = filtered['skills_covered'].apply(len)

    # ── Highlight target skills ────────────────────────────────────
    filtered['matched_target_skills'] = filtered['skills_covered'].apply(
        lambda skills: [s for s in skills if s in target_skills]
    )
    filtered['target_skill_count'] = filtered['matched_target_skills'].apply(len)

    # ── Rank and return top K ──────────────────────────────────────
    results = (
        filtered
        .sort_values('final_score', ascending=False)
        .head(top_k)
        .reset_index(drop=True)
    )
    results.index += 1  # 1-based ranking

    return results


def print_recommendations(results: pd.DataFrame, career_goal: str):
    print(f"\n{'='*65}")
    print(f"TOP RECOMMENDATIONS FOR: {career_goal.upper()}")
    print(f"{'='*65}")
    print(f"{'Rank':<5} {'Uni':<5} {'Course':<42} {'Score':>6} {'Skills':>6}")
    print("-" * 65)

    for rank, row in results.iterrows():
        course = row['course_name'][:40]
        print(f"{rank:<5} {row['university']:<5} {course:<42} "
              f"{row['final_score']:.3f}  {row['num_skills']:>4}")

    print()
    print("Top 3 in detail:")
    for rank, row in results.head(3).iterrows():
        print(f"\n  #{rank} [{row['university']}] {row['course_name']}")
        print(f"     Programme:      {row['programme']}")
        print(f"     Final Score:    {row['final_score']:.4f} "
              f"(content: {row['content_score_norm']:.3f}, "
              f"demand: {row['demand_score_norm']:.3f})")
        print(f"     Skills covered: {row['num_skills']}")
        if row['matched_target_skills']:
            print(f"     Target skills:  {', '.join(row['matched_target_skills'][:5])}")


def evaluate_recommendations(results: pd.DataFrame,
                               career_goal: str,
                               coverage_df: pd.DataFrame,
                               k_values=[3, 5, 10]) -> dict:
    """
    Compute Precision@K and NDCG@K.
    Relevance = course covers at least one High Demand skill
    related to the career goal.
    """
    if career_goal in CAREER_PROFILES:
        target_skills = set(CAREER_PROFILES[career_goal]['top_skills'])
    else:
        target_skills = set()

    high_demand = set(
        coverage_df[coverage_df['demand_tier'] == 'High Demand']['skill']
    )

    def is_relevant(row):
        covered = set(row['skills_covered'])
        return bool(covered & target_skills) or bool(covered & high_demand)

    results['relevant'] = results.apply(is_relevant, axis=1).astype(int)

    metrics = {'career_goal': career_goal}

    for k in k_values:
        top_k = results.head(k)
        # Precision@K
        precision = top_k['relevant'].sum() / k
        metrics[f'Precision@{k}'] = round(precision, 4)

        # NDCG@K
        rels = top_k['relevant'].tolist()
        dcg  = sum(r / np.log2(i + 2) for i, r in enumerate(rels))
        ideal_rels = sorted(rels, reverse=True)
        idcg = sum(r / np.log2(i + 2) for i, r in enumerate(ideal_rels))
        ndcg = dcg / idcg if idcg > 0 else 0
        metrics[f'NDCG@{k}'] = round(ndcg, 4)

    return metrics


def main():
    print("=" * 65)
    print("DEMAND-AWARE COURSE RECOMMENDATION SYSTEM")
    print("=" * 65)

    courses, matches, coverage = load_data()
    print(f"Courses loaded: {len(courses)} "
          f"({courses['university'].value_counts().to_dict()})")

    os.makedirs('results/recommendations', exist_ok=True)

    all_metrics = []

    # ── Run for all predefined careers ────────────────────────────
    for career in CAREER_PROFILES.keys():
        results = recommend(
            career_goal=career,
            courses_df=courses,
            matches_df=matches,
            coverage_df=coverage,
            university_filter='Both',
            top_k=10,
            alpha=0.6
        )

        if results.empty:
            continue

        print_recommendations(results, career)

        # Save recommendations
        save_cols = ['university', 'course_code', 'course_name', 'programme',
                     'content_score_norm', 'demand_score_norm', 'final_score',
                     'num_skills', 'target_skill_count']
        results[save_cols].to_csv(
            f"results/recommendations/rec_{re.sub(r'[^\w\s]', '', career).strip().replace(' ', '_').lower()}.csv",
            index_label='rank'
        )

        # Evaluate
        metrics = evaluate_recommendations(results, career, coverage)
        all_metrics.append(metrics)

    # ── Evaluation summary ─────────────────────────────────────────
    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv('results/recommendations/evaluation_metrics.csv', index=False)

    print("\n" + "=" * 65)
    print("EVALUATION METRICS SUMMARY")
    print("=" * 65)
    print(metrics_df.to_string(index=False))

    print("\n" + "=" * 65)
    print("AVERAGE METRICS ACROSS ALL CAREER GOALS")
    print("=" * 65)
    numeric_cols = [c for c in metrics_df.columns if c != 'career_goal']
    print(metrics_df[numeric_cols].mean().round(4).to_string())

    # ── Interactive mode ───────────────────────────────────────────
    print("\n" + "=" * 65)
    print("INTERACTIVE MODE — Try your own career goal")
    print("=" * 65)
    print("Available careers:")
    for i, c in enumerate(CAREER_PROFILES.keys(), 1):
        print(f"  {i}. {c}")
    print(f"  {len(CAREER_PROFILES)+1}. Type a custom goal")

    try:
        choice = input("\nEnter number or type goal (or 'skip' to exit): ").strip()
        if choice.lower() == 'skip' or not choice:
            return

        if choice.isdigit():
            idx = int(choice) - 1
            careers = list(CAREER_PROFILES.keys())
            if 0 <= idx < len(careers):
                goal = careers[idx]
            else:
                goal = choice
        else:
            goal = choice

        uni = input("Filter by university? (TSI / RTU / Both) [Both]: ").strip()
        if uni not in ['TSI', 'RTU', 'Both']:
            uni = 'Both'

        results = recommend(
            career_goal=goal,
            courses_df=courses,
            matches_df=matches,
            coverage_df=coverage,
            university_filter=uni,
            top_k=10,
            alpha=0.6
        )
        print_recommendations(results, goal)

    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()