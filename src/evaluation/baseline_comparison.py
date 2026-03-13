"""
Baseline Comparison — Recommendation System Evaluation
=======================================================
Compares three models:
  1. Content-Only     (TF-IDF cosine similarity only)
  2. Demand-Only      (job market demand score only)
  3. Hybrid (Ours)    (content + demand + skill coverage)

Metrics: Precision@K, NDCG@K (K = 3, 5, 10)

Output:
  results/evaluation/baseline_comparison.csv
  results/figures/fig_baseline_comparison.png

Run: python src/evaluation/baseline_comparison.py
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models.recommendation_system import (
    load_data,
    get_course_demand_score,
    CAREER_PROFILES,
    DEMAND_TIER_WEIGHTS
)

matplotlib.rcParams.update({
    'figure.facecolor': '#1e1e2e',
    'axes.facecolor':   '#1e1e2e',
    'axes.edgecolor':   '#45475a',
    'axes.labelcolor':  '#cdd6f4',
    'xtick.color':      '#cdd6f4',
    'ytick.color':      '#cdd6f4',
    'text.color':       '#cdd6f4',
    'grid.color':       '#313244',
    'grid.alpha':       0.4,
})

PURPLE = "#cba6f7"
BLUE   = "#89b4fa"
GREEN  = "#a6e3a1"


# ── Relevance function ─────────────────────────────────────────
def is_relevant(row, target_skills):
    covered = set(row["skills_covered"]) if isinstance(row["skills_covered"], list) else set()
    return int(bool(covered & set(target_skills)))


# ── Evaluation metrics ─────────────────────────────────────────
def compute_metrics(results, career_goal, k_values=[3, 5, 10]):
    if career_goal in CAREER_PROFILES:
        target_skills = CAREER_PROFILES[career_goal]["top_skills"]
    else:
        target_skills = []

    results["relevant"] = results.apply(
        lambda row: is_relevant(row, target_skills), axis=1
    )

    metrics = {}
    for k in k_values:
        top_k = results.head(k)
        # Precision@K
        metrics[f"Precision@{k}"] = round(top_k["relevant"].sum() / k, 4)
        # NDCG@K
        rels  = top_k["relevant"].tolist()
        dcg   = sum(r / np.log2(i + 2) for i, r in enumerate(rels))
        idcg  = sum(1 / np.log2(i + 2) for i in range(min(k, sum(rels)))) if sum(rels) > 0 else 0
        metrics[f"NDCG@{k}"] = round(dcg / idcg if idcg > 0 else 0, 4)

    return metrics


# ── Prepare course skill lists ─────────────────────────────────
def attach_skills(filtered, matches_df, target_skills):
    course_skills = (
        matches_df.groupby("course_code")["skill"]
        .apply(list)
        .reset_index()
        .rename(columns={"skill": "skills_covered"})
    )
    filtered = filtered.merge(course_skills, on="course_code", how="left")
    filtered["skills_covered"] = filtered["skills_covered"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    filtered["target_skill_count"] = filtered["skills_covered"].apply(
        lambda skills: len([s for s in skills if s in target_skills])
    )
    filtered["num_skills"] = filtered["skills_covered"].apply(len)
    return filtered


# ── Model 1: Content Only ──────────────────────────────────────
def recommend_content_only(career_goal, courses_df, matches_df, top_k=10):
    query = CAREER_PROFILES[career_goal]["keywords"] if career_goal in CAREER_PROFILES else career_goal
    target_skills = CAREER_PROFILES[career_goal]["top_skills"] if career_goal in CAREER_PROFILES else []

    filtered = courses_df.copy().reset_index(drop=True)

    all_docs = filtered["match_text"].tolist() + [query]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=8000)
    tfidf = vectorizer.fit_transform(all_docs)

    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    filtered["final_score"] = scores / scores.max() if scores.max() > 0 else scores
    filtered = attach_skills(filtered, matches_df, target_skills)

    return filtered.sort_values("final_score", ascending=False).head(top_k).reset_index(drop=True)


# ── Model 2: Demand Only ───────────────────────────────────────
def recommend_demand_only(career_goal, courses_df, matches_df, coverage_df, top_k=10):
    target_skills = CAREER_PROFILES[career_goal]["top_skills"] if career_goal in CAREER_PROFILES else []

    filtered = courses_df.copy().reset_index(drop=True)
    demand_scores = get_course_demand_score(filtered, matches_df, coverage_df)
    filtered = filtered.merge(demand_scores[["course_code", "demand_score_norm"]], on="course_code", how="left")
    filtered["demand_score_norm"] = filtered["demand_score_norm"].fillna(0)
    filtered["final_score"] = filtered["demand_score_norm"]
    filtered = attach_skills(filtered, matches_df, target_skills)

    return filtered.sort_values("final_score", ascending=False).head(top_k).reset_index(drop=True)


# ── Model 3: Hybrid (Your model) ──────────────────────────────
def recommend_hybrid(career_goal, courses_df, matches_df, coverage_df, top_k=10):
    query = CAREER_PROFILES[career_goal]["keywords"] if career_goal in CAREER_PROFILES else career_goal
    target_skills = CAREER_PROFILES[career_goal]["top_skills"] if career_goal in CAREER_PROFILES else []

    filtered = courses_df.copy().reset_index(drop=True)

    # Layer 1 — Content
    all_docs = filtered["match_text"].tolist() + [query]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=8000)
    tfidf = vectorizer.fit_transform(all_docs)
    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    filtered["content_score_norm"] = scores / scores.max() if scores.max() > 0 else scores

    # Layer 2 — Demand
    demand_scores = get_course_demand_score(filtered, matches_df, coverage_df)
    filtered = filtered.merge(demand_scores[["course_code", "demand_score_norm"]], on="course_code", how="left")
    filtered["demand_score_norm"] = filtered["demand_score_norm"].fillna(0)

    # Skills
    filtered = attach_skills(filtered, matches_df, target_skills)

    # Layer 3 — Skill coverage
    max_t = filtered["target_skill_count"].max()
    filtered["skill_coverage_norm"] = filtered["target_skill_count"] / max_t if max_t > 0 else 0

    # Combined
    filtered["final_score"] = (
        0.5 * filtered["content_score_norm"] +
        0.3 * filtered["demand_score_norm"] +
        0.2 * filtered["skill_coverage_norm"]
    )

    return filtered.sort_values("final_score", ascending=False).head(top_k).reset_index(drop=True)


# ── Main comparison ────────────────────────────────────────────
def main():
    print("=" * 65)
    print("BASELINE COMPARISON — 3 MODELS")
    print("=" * 65)

    courses, matches, coverage = load_data()
    os.makedirs("results/evaluation", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)

    all_results = []

    for career in CAREER_PROFILES.keys():
        print(f"\nEvaluating: {career}")

        # Run all 3 models
        r_content = recommend_content_only(career, courses, matches)
        r_demand  = recommend_demand_only(career, courses, matches, coverage)
        r_hybrid  = recommend_hybrid(career, courses, matches, coverage)

        # Compute metrics
        m_content = compute_metrics(r_content, career)
        m_demand  = compute_metrics(r_demand,  career)
        m_hybrid  = compute_metrics(r_hybrid,  career)

        for model_name, metrics in [
            ("Content-Only", m_content),
            ("Demand-Only",  m_demand),
            ("Hybrid (Ours)", m_hybrid)
        ]:
            row = {"career_goal": career, "model": model_name}
            row.update(metrics)
            all_results.append(row)

        print(f"  P@5  → Content: {m_content['Precision@5']:.3f} | "
              f"Demand: {m_demand['Precision@5']:.3f} | "
              f"Hybrid: {m_hybrid['Precision@5']:.3f}")

    # Save results
    df = pd.DataFrame(all_results)
    df.to_csv("results/evaluation/baseline_comparison.csv", index=False)
    print(f"\n✅ Saved: results/evaluation/baseline_comparison.csv")

    # ── Summary table ──────────────────────────────────────────
    print("\n" + "=" * 65)
    print("AVERAGE METRICS BY MODEL")
    print("=" * 65)
    numeric_cols = [c for c in df.columns if c not in ["career_goal", "model"]]
    summary = df.groupby("model")[numeric_cols].mean().round(4)
    print(summary.to_string())

    # ── Plot ───────────────────────────────────────────────────
    models   = ["Content-Only", "Demand-Only", "Hybrid (Ours)"]
    colors   = [BLUE, PURPLE, GREEN]
    metrics  = ["Precision@3", "Precision@5", "Precision@10",
                "NDCG@3",      "NDCG@5",      "NDCG@10"]

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle("Baseline Comparison — Model Performance", fontsize=14, y=1.01)

    for ax, metric in zip(axes.flatten(), metrics):
        vals = [summary.loc[m, metric] if m in summary.index else 0 for m in models]
        bars = ax.bar(models, vals, color=colors, width=0.5)
        ax.set_title(metric, fontsize=11)
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("Score")
        ax.grid(axis="y")
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.3f}",
                ha="center", va="bottom", fontsize=9
            )
        ax.set_xticklabels(models, rotation=15, ha="right", fontsize=8)

    plt.tight_layout()
    plt.savefig("results/figures/fig_baseline_comparison.png", dpi=150, bbox_inches="tight")
    print("✅ Saved: results/figures/fig_baseline_comparison.png")
    plt.close()

    # ── Improvement over best baseline ────────────────────────
    print("\n" + "=" * 65)
    print("HYBRID IMPROVEMENT OVER BEST BASELINE")
    print("=" * 65)
    for metric in ["Precision@5", "Precision@10", "NDCG@5", "NDCG@10"]:
        hybrid_score   = summary.loc["Hybrid (Ours)", metric]
        baseline_best  = max(
            summary.loc["Content-Only", metric],
            summary.loc["Demand-Only",  metric]
        )
        improvement = ((hybrid_score - baseline_best) / baseline_best * 100) if baseline_best > 0 else 0
        print(f"  {metric:<15} Hybrid: {hybrid_score:.4f} | "
              f"Best Baseline: {baseline_best:.4f} | "
              f"Improvement: +{improvement:.1f}%")


if __name__ == "__main__":
    main()