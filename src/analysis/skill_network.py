"""
Skill Co-occurrence Network Analysis
=====================================
Uses job_skills_v4.csv — real job-level skill data.
Groups skills by job_id to find which skills appear together.

Run: python src/analysis/skill_network.py
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
from collections import defaultdict
from itertools import combinations
import networkx as nx

matplotlib.rcParams.update({
    'figure.facecolor': '#1e1e2e',
    'axes.facecolor':   '#1e1e2e',
    'axes.edgecolor':   '#45475a',
    'axes.labelcolor':  '#cdd6f4',
    'text.color':       '#cdd6f4',
})

CATEGORY_COLORS = {
    "Programming Languages": "#cba6f7",
    "Web Development":       "#89b4fa",
    "Data & Analytics":      "#a6e3a1",
    "Cloud & DevOps":        "#94e2d5",
    "Business & Management": "#f9e2af",
    "Security":              "#f38ba8",
    "Engineering & Design":  "#fab387",
    "Databases":             "#89dceb",
    "Other":                 "#585b70",
}

def map_category(cat):
    cat_lower = str(cat).lower()
    if "programming" in cat_lower or "language" in cat_lower:
        return "Programming Languages"
    elif "web" in cat_lower or "frontend" in cat_lower:
        return "Web Development"
    elif "data" in cat_lower or "analytic" in cat_lower or "ml" in cat_lower or "ai" in cat_lower:
        return "Data & Analytics"
    elif "cloud" in cat_lower or "devops" in cat_lower or "infra" in cat_lower:
        return "Cloud & DevOps"
    elif "business" in cat_lower or "management" in cat_lower or "project" in cat_lower:
        return "Business & Management"
    elif "security" in cat_lower or "cyber" in cat_lower:
        return "Security"
    elif "engineer" in cat_lower or "design" in cat_lower or "cad" in cat_lower:
        return "Engineering & Design"
    elif "database" in cat_lower or "sql" in cat_lower:
        return "Databases"
    return "Other"

def build_cooccurrence(df, min_cooccurrence=3):
    job_skills = df.groupby("job_id")["skill"].apply(list).reset_index()
    print(f"  Total jobs with skills: {len(job_skills)}")
    print(f"  Avg skills per job:     {job_skills['skill'].apply(len).mean():.1f}")

    cooccur    = defaultdict(int)
    skill_freq = defaultdict(int)

    for _, row in job_skills.iterrows():
        skills = list(set(row["skill"]))
        if len(skills) < 2:
            continue
        for s in skills:
            skill_freq[s] += 1
        for s1, s2 in combinations(skills, 2):
            key = tuple(sorted([s1, s2]))
            cooccur[key] += 1

    filtered = {k: v for k, v in cooccur.items() if v >= min_cooccurrence}
    print(f"  Unique skills:          {len(skill_freq)}")
    print(f"  Co-occurrence pairs:    {len(filtered)}")
    return filtered, dict(skill_freq)

def build_network(cooccur, skill_freq, skill_cat_map, top_n=40, min_cooccur=3):
    G = nx.Graph()
    top_skills = set(sorted(skill_freq, key=lambda x: skill_freq[x], reverse=True)[:top_n])

    for skill in top_skills:
        G.add_node(skill,
                   frequency=skill_freq.get(skill, 1),
                   category=skill_cat_map.get(skill, "Other"))

    for (s1, s2), weight in cooccur.items():
        if s1 in top_skills and s2 in top_skills and weight >= min_cooccur:
            G.add_edge(s1, s2, weight=weight)

    isolated = [n for n in G.nodes() if G.degree(n) == 0]
    G.remove_nodes_from(isolated)
    return G

def plot_network(G, title, filename, figsize=(16, 12)):
    if len(G.nodes()) == 0:
        print("  ⚠ No nodes to plot")
        return

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#1e1e2e")

    pos        = nx.spring_layout(G, k=3.0, iterations=100, seed=42)
    freqs      = [G.nodes[n].get("frequency", 1) for n in G.nodes()]
    max_freq   = max(freqs) if freqs else 1
    node_sizes = [300 + (f / max_freq) * 2500 for f in freqs]
    node_colors = [CATEGORY_COLORS.get(G.nodes[n].get("category", "Other"), "#585b70") for n in G.nodes()]
    weights    = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_w      = max(weights) if weights else 1
    edge_widths = [0.3 + (w / max_w) * 4 for w in weights]

    nx.draw_networkx_edges(G, pos, ax=ax, width=edge_widths, alpha=0.25, edge_color="#6c7086")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color=node_colors,
                           alpha=0.92, linewidths=0.5, edgecolors="#1e1e2e")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="#cdd6f4", font_weight="bold")

    used_cats = set(G.nodes[n].get("category", "Other") for n in G.nodes())
    patches   = [mpatches.Patch(color=CATEGORY_COLORS.get(c, "#585b70"), label=c)
                 for c in CATEGORY_COLORS if c in used_cats]
    ax.legend(handles=patches, loc="lower left", fontsize=9, framealpha=0.4,
              facecolor="#1e1e2e", edgecolor="#45475a",
              title="Skill Category", title_fontsize=9)

    ax.set_title(title, fontsize=13, pad=15, color="#cdd6f4", fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#1e1e2e")
    print(f"✅ Saved: {filename}")
    plt.close()

def main():
    print("=" * 65)
    print("SKILL CO-OCCURRENCE NETWORK ANALYSIS")
    print("=" * 65)

    os.makedirs("results/figures", exist_ok=True)
    os.makedirs("results/evaluation", exist_ok=True)

    # Load data
    df = pd.read_csv("data/processed/job_skills_v4.csv")
    print(f"Loaded: {df.shape[0]} rows | {df['job_id'].nunique()} jobs | {df['skill'].nunique()} skills\n")

    # Build skill → category map
    skill_cat_map = (
        df.drop_duplicates("skill")
        .set_index("skill")["skill_category"]
        .apply(map_category)
        .to_dict()
    )

    # Build co-occurrence
    cooccur, skill_freq = build_cooccurrence(df, min_cooccurrence=3)

    # Full network (top 40)
    print("\nBuilding full network (top 40 skills)...")
    G_full = build_network(cooccur, skill_freq, skill_cat_map, top_n=40, min_cooccur=3)
    print(f"  Nodes: {G_full.number_of_nodes()}, Edges: {G_full.number_of_edges()}")
    plot_network(G_full,
                 "Skill Co-occurrence Network — Top 40 Skills in Riga Job Market",
                 "results/figures/fig_skill_network.png",
                 figsize=(16, 12))

    # Focused network (top 20)
    print("\nBuilding focused network (top 20 skills)...")
    G_small = build_network(cooccur, skill_freq, skill_cat_map, top_n=20, min_cooccur=5)
    print(f"  Nodes: {G_small.number_of_nodes()}, Edges: {G_small.number_of_edges()}")
    plot_network(G_small,
                 "Skill Co-occurrence Network — Top 20 Skills",
                 "results/figures/fig_skill_network_top20.png",
                 figsize=(12, 9))

    # Save matrix
    records = [{"skill_1": k[0], "skill_2": k[1], "cooccurrence": v}
               for k, v in sorted(cooccur.items(), key=lambda x: -x[1])]
    cooccur_df = pd.DataFrame(records)
    cooccur_df.to_csv("results/evaluation/skill_cooccurrence_matrix.csv", index=False)
    print(f"\n✅ Saved: results/evaluation/skill_cooccurrence_matrix.csv")

    # Top pairs
    print("\n" + "=" * 65)
    print("TOP 15 CO-OCCURRING SKILL PAIRS")
    print("=" * 65)
    print(cooccur_df.head(15).to_string(index=False))

    # Network stats
    print("\n" + "=" * 65)
    print("NETWORK STATISTICS")
    print("=" * 65)
    print(f"  Nodes:           {G_full.number_of_nodes()}")
    print(f"  Edges:           {G_full.number_of_edges()}")
    print(f"  Avg degree:      {np.mean([d for _, d in G_full.degree()]):.2f}")
    print(f"  Network density: {nx.density(G_full):.4f}")

    centrality   = nx.degree_centrality(G_full)
    top_central  = sorted(centrality.items(), key=lambda x: -x[1])[:10]
    print("\n  Top hub skills (most connected to others):")
    for skill, score in top_central:
        print(f"    {skill:<35} centrality: {score:.3f}")

    print("\n" + "=" * 65)
    print("Now commit:")
    print("  git add src/analysis/skill_network.py results/figures/fig_skill_network*.png results/evaluation/skill_cooccurrence_matrix.csv")
    print("  git commit -m 'Add skill co-occurrence network - real job data'")
    print("  git push")

if __name__ == "__main__":
    main()