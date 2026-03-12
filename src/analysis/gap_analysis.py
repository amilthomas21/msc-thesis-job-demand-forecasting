"""
Gap Analysis Visualization
Generates publication-ready figures for thesis Chapter 5

Outputs (saved to results/figures/):
  fig1_coverage_overview.png       - Pie chart: Well Covered vs Gap vs Partial
  fig2_critical_gaps.png           - Bar chart: Top critical gap skills
  fig3_tsi_vs_rtu.png             - Grouped bar: TSI vs RTU coverage comparison
  fig4_top_courses.png             - Horizontal bar: Top courses by skill coverage
  fig5_gap_heatmap.png            - Heatmap: Top skills vs universities

Run: python src/analysis/gap_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Style settings ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':  'sans-serif',
    'font.size':    11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'figure.dpi':   150,
})

COLORS = {
    'well':    '#2ecc71',
    'partial': '#f39c12',
    'gap':     '#e74c3c',
    'tsi':     '#3498db',
    'rtu':     '#9b59b6',
    'neutral': '#95a5a6',
}

OUTPUT_DIR = 'results/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    coverage = pd.read_csv('data/processed/skill_coverage.csv')
    matches  = pd.read_csv('data/processed/course_skill_matches.csv')
    return coverage, matches


# ── Figure 1: Coverage Overview Pie Chart ─────────────────────────────────────
def fig1_coverage_overview(coverage):
    # Only high demand skills
    hd = coverage[coverage['demand_tier'] == 'High Demand']
    counts = hd['coverage_status'].value_counts()

    labels, sizes, colors = [], [], []
    mapping = {
        'Well Covered':      ('Well Covered',    COLORS['well']),
        'Partially Covered': ('Partially Covered', COLORS['partial']),
        'GAP — Not Covered': ('Not Covered (GAP)', COLORS['gap']),
    }
    for key, (label, color) in mapping.items():
        if key in counts:
            labels.append(f"{label}\n({counts[key]})")
            sizes.append(counts[key])
            colors.append(color)

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=140,
        pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight('bold')

    ax.set_title('High-Demand Skill Coverage\n(TSI + RTU Combined)', pad=15)
    plt.tight_layout()
    path = f'{OUTPUT_DIR}/fig1_coverage_overview.png'
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


# ── Figure 2: Critical Gaps Bar Chart ─────────────────────────────────────────
def fig2_critical_gaps(coverage):
    gaps = coverage[
        (coverage['coverage_status'] == 'GAP — Not Covered') &
        (coverage['demand_tier'] == 'High Demand')
    ].sort_values('frequency', ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(gaps['skill'], gaps['frequency'],
                   color=COLORS['gap'], edgecolor='white', linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, gaps['frequency']):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=9, color='#333333')

    ax.set_xlabel('Number of Job Postings Mentioning Skill')
    ax.set_title('Critical Skill Gaps\n(High-Demand Skills with Zero Course Coverage)')
    ax.set_xlim(0, gaps['frequency'].max() * 1.18)
    plt.tight_layout()
    path = f'{OUTPUT_DIR}/fig2_critical_gaps.png'
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


# ── Figure 3: TSI vs RTU Coverage Comparison ──────────────────────────────────
def fig3_tsi_vs_rtu(coverage):
    # Top 20 high demand skills
    hd = coverage[coverage['demand_tier'] == 'High Demand'].head(20)
    skills = hd['skill'].tolist()
    tsi    = hd['tsi_courses'].tolist()
    rtu    = hd['rtu_courses'].tolist()

    x = np.arange(len(skills))
    width = 0.38

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(x - width/2, tsi, width, label='TSI', color=COLORS['tsi'],
           edgecolor='white', linewidth=0.5)
    ax.bar(x + width/2, rtu, width, label='RTU', color=COLORS['rtu'],
           edgecolor='white', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(skills, rotation=40, ha='right', fontsize=9)
    ax.set_ylabel('Number of Courses Covering Skill')
    ax.set_title('TSI vs RTU: Course Coverage for Top 20 In-Demand Skills')
    ax.legend(frameon=False)
    plt.tight_layout()
    path = f'{OUTPUT_DIR}/fig3_tsi_vs_rtu.png'
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


# ── Figure 4: Top Courses by Skill Coverage ───────────────────────────────────
def fig4_top_courses(matches):
    top = (
        matches.groupby(['university', 'course_name'])['skill']
        .count()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    top.columns = ['university', 'course_name', 'skills_covered']

    # Truncate long names
    top['label'] = top.apply(
        lambda r: f"[{r['university']}] {r['course_name'][:40]}", axis=1
    )
    top = top.sort_values('skills_covered', ascending=True)

    colors = [COLORS['tsi'] if u == 'TSI' else COLORS['rtu']
              for u in top['university']]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(top['label'], top['skills_covered'],
                   color=colors, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, top['skills_covered']):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=9)

    ax.set_xlabel('Number of Skills Covered')
    ax.set_title('Top 15 Courses by Skill Market Coverage')
    ax.set_xlim(0, top['skills_covered'].max() * 1.15)

    tsi_patch = mpatches.Patch(color=COLORS['tsi'], label='TSI')
    rtu_patch = mpatches.Patch(color=COLORS['rtu'], label='RTU')
    ax.legend(handles=[tsi_patch, rtu_patch], frameon=False)

    plt.tight_layout()
    path = f'{OUTPUT_DIR}/fig4_top_courses.png'
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


# ── Figure 5: Coverage Status by Category ─────────────────────────────────────
def fig5_coverage_by_status(coverage):
    status_order = ['Well Covered', 'Partially Covered', 'GAP — Not Covered']
    tier_order   = ['High Demand', 'Moderate Demand', 'Low Demand']

    data = coverage.groupby(['demand_tier', 'coverage_status']).size().unstack(fill_value=0)
    data = data.reindex(index=tier_order, columns=status_order, fill_value=0)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(tier_order))
    width = 0.25
    bar_colors = [COLORS['well'], COLORS['partial'], COLORS['gap']]

    for i, (status, color) in enumerate(zip(status_order, bar_colors)):
        if status in data.columns:
            vals = data[status].tolist()
            bars = ax.bar(x + i*width, vals, width,
                          label=status, color=color,
                          edgecolor='white', linewidth=0.5)
            for bar, val in zip(bars, vals):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2,
                            bar.get_height() + 0.5,
                            str(val), ha='center', fontsize=9)

    ax.set_xticks(x + width)
    ax.set_xticklabels(tier_order)
    ax.set_ylabel('Number of Skills')
    ax.set_title('Skill Coverage Status by Demand Tier')
    ax.legend(frameon=False)
    plt.tight_layout()
    path = f'{OUTPUT_DIR}/fig5_coverage_by_tier.png'
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("GAP ANALYSIS VISUALIZATION")
    print("=" * 55)

    coverage, matches = load_data()

    print(f"Loaded: {len(coverage)} skills, {len(matches)} matches")
    print(f"Universities: {matches['university'].unique().tolist()}")
    print(f"Demand tiers: {coverage['demand_tier'].unique().tolist()}")
    print()

    fig1_coverage_overview(coverage)
    fig2_critical_gaps(coverage)
    fig3_tsi_vs_rtu(coverage)
    fig4_top_courses(matches)
    fig5_coverage_by_status(coverage)

    print()
    print("=" * 55)
    print("All figures saved to results/figures/")
    print("=" * 55)

    # Print key stats for thesis writeup
    hd = coverage[coverage['demand_tier'] == 'High Demand']
    print(f"\nKey stats for Chapter 5:")
    print(f"  High demand skills total:  {len(hd)}")
    print(f"  Well covered:              {(hd['coverage_status']=='Well Covered').sum()}")
    print(f"  Partially covered:         {(hd['coverage_status']=='Partially Covered').sum()}")
    print(f"  Not covered (GAP):         {(hd['coverage_status']=='GAP — Not Covered').sum()}")
    print(f"  TSI-only gaps:             {((hd['tsi_courses']==0) & (hd['rtu_courses']>0)).sum()}")
    print(f"  Both universities gap:     {((hd['tsi_courses']==0) & (hd['rtu_courses']==0)).sum()}")


if __name__ == "__main__":
    main()