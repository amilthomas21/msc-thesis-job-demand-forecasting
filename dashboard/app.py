import sys
import os

# ── Absolute base path (works locally AND on Streamlit Cloud) ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from src.models.recommendation_system import (
    load_data, recommend, CAREER_PROFILES
)

st.set_page_config(
    page_title="Course Recommendation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .metric-card { background-color:#1e1e2e; border:1px solid #313244; border-radius:10px; padding:16px 20px; text-align:center; }
    .metric-value { font-size:2rem; font-weight:bold; color:#cba6f7; }
    .metric-label { font-size:0.85rem; color:#a6adc8; margin-top:4px; }
    .course-card { background-color:#1e1e2e; border-left:4px solid #cba6f7; border-radius:8px; padding:14px 18px; margin-bottom:10px; }
    .gap-card { background-color:#1e1e2e; border-left:4px solid #f38ba8; border-radius:8px; padding:12px 16px; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

matplotlib.rcParams.update({
    'figure.facecolor':'#1e1e2e','axes.facecolor':'#1e1e2e','axes.edgecolor':'#45475a',
    'axes.labelcolor':'#cdd6f4','xtick.color':'#cdd6f4','ytick.color':'#cdd6f4',
    'text.color':'#cdd6f4','grid.color':'#313244','grid.alpha':0.4,
})

PURPLE="#cba6f7"; BLUE="#89b4fa"; GREEN="#a6e3a1"; RED="#f38ba8"; YELLOW="#f9e2af"

def abs_path(*parts):
    return os.path.join(BASE_DIR, *parts)

@st.cache_data
def get_data():
    return load_data()

@st.cache_data
def get_coverage():
    return pd.read_csv(abs_path("data","processed","skill_coverage.csv"))

@st.cache_data
def get_eval():
    p = abs_path("results","recommendations","evaluation_metrics.csv")
    return pd.read_csv(p) if os.path.exists(p) else None

@st.cache_data
def get_baseline():
    p = abs_path("results","evaluation","baseline_comparison.csv")
    return pd.read_csv(p) if os.path.exists(p) else None

@st.cache_data
def get_job_skills():
    p = abs_path("data","processed","job_skills_v4.csv")
    return pd.read_csv(p) if os.path.exists(p) else None

courses, matches, coverage = get_data()
skill_coverage = get_coverage()
eval_df        = get_eval()
baseline_df    = get_baseline()
job_skills_df  = get_job_skills()

# ── Header ────────────────────────────────────────────────────
st.markdown("## Demand-Aware Course Recommendation System")
st.markdown("*Aligning university curricula with Riga job market skill demand · TSI & RTU · 2026*")
st.divider()

c1,c2,c3,c4,c5 = st.columns(5)
for col,val,lbl in zip([c1,c2,c3,c4,c5],
    ["3,057","321","112","497","3,205"],
    ["Job Postings","Skills Identified","TSI Courses","RTU Courses","Skill Mappings"]):
    col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>',unsafe_allow_html=True)

st.markdown(""); st.divider()

tab1,tab2,tab3,tab4 = st.tabs(["Job Market Overview","Course Recommender","Curriculum Gap Analysis","Evaluation Metrics"])

# ══════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Job Market Skill Demand Analysis")
    st.markdown("Based on **3,057 job postings** from SS.lv and CV.lv (Riga, Latvia)")
    col_a,col_b = st.columns(2)
    with col_a:
        st.markdown("#### Top 20 Most Demanded Skills")
        top20  = skill_coverage.sort_values("frequency",ascending=False).head(20)
        colors = [RED if t=="High Demand" else YELLOW if t=="Moderate Demand" else GREEN for t in top20["demand_tier"]]
        fig,ax = plt.subplots(figsize=(7,6))
        ax.barh(top20["skill"][::-1],top20["frequency"][::-1],color=colors[::-1])
        ax.set_xlabel("Job Mentions"); ax.set_title("Top 20 Skills in Riga Job Market"); ax.grid(axis="x")
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()
    with col_b:
        st.markdown("#### Demand Tier Distribution")
        tier_counts = skill_coverage["demand_tier"].value_counts()
        fig2,ax2 = plt.subplots(figsize=(5,5))
        _,_,autotexts = ax2.pie(tier_counts.values,labels=tier_counts.index,autopct="%1.1f%%",
            colors=[RED,YELLOW,GREEN],startangle=90,wedgeprops={"edgecolor":"#1e1e2e","linewidth":2})
        for t in autotexts: t.set_color("#1e1e2e"); t.set_fontweight("bold")
        ax2.set_title("Skills by Demand Tier"); plt.tight_layout(); st.pyplot(fig2,use_container_width=True); plt.close()
        t1,t2,t3 = st.columns(3)
        t1.metric("High Demand", len(skill_coverage[skill_coverage["demand_tier"]=="High Demand"]))
        t2.metric("Moderate",    len(skill_coverage[skill_coverage["demand_tier"]=="Moderate Demand"]))
        t3.metric("Low",         len(skill_coverage[skill_coverage["demand_tier"]=="Low Demand"]))
    st.divider()
    st.markdown("#### Skill Co-occurrence Network")
    if job_skills_df is not None:
        try:
            import networkx as nx
            job_groups = job_skills_df.groupby("job_id")["skill"].apply(list)
            pairs = {}
            for sl in job_groups:
                us = list(set(sl))
                for i in range(len(us)):
                    for j in range(i+1,len(us)):
                        p = tuple(sorted([us[i],us[j]])); pairs[p] = pairs.get(p,0)+1
            top_skills = skill_coverage.sort_values("frequency",ascending=False).head(25)["skill"].tolist()
            fp = {k:v for k,v in pairs.items() if k[0] in top_skills and k[1] in top_skills and v>=5}
            G = nx.Graph()
            for (s1,s2),w in fp.items(): G.add_edge(s1,s2,weight=w)
            node_sizes = [max(300,min(3000,skill_coverage[skill_coverage["skill"]==n]["frequency"].values[0]*5
                if len(skill_coverage[skill_coverage["skill"]==n])>0 else 300)) for n in G.nodes()]
            fig_net,ax_net = plt.subplots(figsize=(12,8))
            ax_net.set_facecolor("#1e1e2e"); fig_net.patch.set_facecolor("#1e1e2e")
            pos = nx.spring_layout(G,k=2.5,seed=42)
            ew = [G[u][v]["weight"] for u,v in G.edges()]; mw = max(ew) if ew else 1
            nx.draw_networkx_edges(G,pos,ax=ax_net,width=[0.5+2.5*w/mw for w in ew],alpha=0.4,edge_color="#45475a")
            nx.draw_networkx_nodes(G,pos,ax=ax_net,node_color=PURPLE,node_size=node_sizes,alpha=0.9)
            nx.draw_networkx_labels(G,pos,ax=ax_net,font_size=8,font_color="#cdd6f4",font_weight="bold")
            ax_net.set_title("Skill Co-occurrence Network — Top 25 Skills",fontsize=13,pad=15); ax_net.axis("off")
            plt.tight_layout(); st.pyplot(fig_net,use_container_width=True); plt.close()
            top_pairs = sorted(fp.items(),key=lambda x:x[1],reverse=True)[:15]
            pairs_df = pd.DataFrame([(s1,s2,w) for (s1,s2),w in top_pairs],columns=["Skill 1","Skill 2","Co-occurrences"])
            pairs_df.index = range(1,len(pairs_df)+1); st.dataframe(pairs_df,use_container_width=True)
        except ImportError:
            st.warning("Install networkx: `pip install networkx`")
    st.divider()
    s1,s2,s3 = st.columns(3)
    s1.markdown('<div class="metric-card"><div class="metric-value">2,416</div><div class="metric-label">CV.lv Postings</div></div>',unsafe_allow_html=True)
    s2.markdown('<div class="metric-card"><div class="metric-value">641</div><div class="metric-label">SS.lv Postings</div></div>',unsafe_allow_html=True)
    s3.markdown('<div class="metric-card"><div class="metric-value">85.4%</div><div class="metric-label">Skill Coverage Rate</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Career-Based Course Recommender")
    r1,r2,r3 = st.columns([2,1,1])
    with r1:
        mode = st.radio("Input Mode",["Select career","Type custom goal"],horizontal=True)
        career_goal = st.selectbox("Career Goal",list(CAREER_PROFILES.keys())) if mode=="Select career" else st.text_input("Type career goal",placeholder="e.g. AI Engineer")
    with r2: university_filter = st.selectbox("University",["Both","TSI","RTU"])
    with r3: top_k = st.slider("Top N",5,15,10)
    if st.button("Generate Recommendations",type="primary") and career_goal:
        with st.spinner("Finding best courses..."):
            results = recommend(career_goal=career_goal,courses_df=courses,matches_df=matches,coverage_df=coverage,university_filter=university_filter,top_k=top_k)
        st.markdown(f"#### Results for: **{career_goal}** · {university_filter}")
        card_cols = st.columns(3)
        for col,(_,row) in zip(card_cols,results.head(3).iterrows()):
            with col:
                st.markdown(f'<div class="course-card"><strong>{row["course_name"]}</strong><br>{row["university"]} | {row["programme"]}<br>Score: <strong>{row["final_score"]:.3f}</strong><br>Skills: <strong>{row["num_skills"]}</strong></div>',unsafe_allow_html=True)
        display = results[["university","course_name","programme","final_score","content_score_norm","demand_score_norm","skill_coverage_norm","num_skills","target_skill_count"]].copy()
        display.columns=["University","Course","Programme","Final Score","Content","Demand","Skill Coverage","Skills","Target Matches"]
        display.index=range(1,len(display)+1); st.dataframe(display,use_container_width=True)
        left,right=st.columns(2)
        with left:
            top5=results.head(5); x=np.arange(len(top5)); w=0.25
            fig,ax=plt.subplots(figsize=(7,4))
            ax.bar(x-w,top5["content_score_norm"],w,label="Content",color=BLUE)
            ax.bar(x,top5["demand_score_norm"],w,label="Demand",color=PURPLE)
            ax.bar(x+w,top5["skill_coverage_norm"],w,label="Coverage",color=GREEN)
            ax.set_xticks(x); ax.set_xticklabels([c[:18] for c in top5["course_name"]],rotation=30,ha="right",fontsize=8)
            ax.set_ylabel("Score"); ax.set_title("Score Components"); ax.legend(fontsize=8); ax.grid(axis="y")
            plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()
        with right:
            uc=results["university"].value_counts(); fig2,ax2=plt.subplots(figsize=(4,4))
            ax2.pie(uc.values,labels=uc.index,autopct="%1.0f%%",colors=[BLUE,PURPLE],startangle=90,wedgeprops={"edgecolor":"#1e1e2e","linewidth":2})
            ax2.set_title("TSI vs RTU"); plt.tight_layout(); st.pyplot(fig2,use_container_width=True); plt.close()
    else:
        st.info("Select a career goal above and click **Generate Recommendations**")

# ══════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Curriculum Gap Analysis")
    total=len(skill_coverage)
    covered=len(skill_coverage[skill_coverage["coverage_status"]=="Well Covered"])
    partial=len(skill_coverage[skill_coverage["coverage_status"]=="Partially Covered"])
    gap=len(skill_coverage[skill_coverage["coverage_status"].str.contains("Not Covered",na=False)])
    g1,g2,g3,g4=st.columns(4)
    g1.metric("Total Skills",total); g2.metric("Well Covered",covered); g3.metric("Partial",partial); g4.metric("Gap",gap)
    left,right=st.columns(2)
    with left:
        fig,ax=plt.subplots(figsize=(5,5))
        _,_,autotexts=ax.pie([covered,partial,gap],labels=["Well Covered","Partially Covered","Not Covered"],
            autopct="%1.1f%%",colors=[GREEN,YELLOW,RED],startangle=90,wedgeprops={"edgecolor":"#1e1e2e","linewidth":2})
        for t in autotexts: t.set_color("#1e1e2e"); t.set_fontweight("bold")
        ax.set_title("Skill Coverage Status"); plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()
    with right:
        st.markdown("#### Critical Gaps — High Demand, Not Covered")
        critical=skill_coverage[(skill_coverage["demand_tier"]=="High Demand")&(skill_coverage["coverage_status"].str.contains("Not Covered",na=False))].sort_values("frequency",ascending=False).head(12)
        for _,row in critical.iterrows():
            st.markdown(f'<div class="gap-card"><strong>{row["skill"]}</strong> &nbsp; <span style="color:#f38ba8">{row["frequency"]} job mentions</span></div>',unsafe_allow_html=True)
    st.divider()
    tsi_s=matches[matches["university"]=="TSI"]["skill"].nunique(); rtu_s=matches[matches["university"]=="RTU"]["skill"].nunique()
    fig,ax=plt.subplots(figsize=(6,2.5))
    bars=ax.barh(["RTU (497 courses)","TSI (112 courses)"],[rtu_s,tsi_s],color=[BLUE,PURPLE],height=0.4)
    for bar,val in zip(bars,[rtu_s,tsi_s]): ax.text(bar.get_width()+1,bar.get_y()+bar.get_height()/2,str(val),va="center",fontsize=11)
    ax.set_xlabel("Unique Skills Covered"); ax.set_title("Skills Covered by University"); ax.grid(axis="x")
    plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()
    top_courses=matches.groupby(["university","course_name"])["skill"].nunique().reset_index().rename(columns={"skill":"skills_covered"}).sort_values("skills_covered",ascending=False).head(10)
    fig2,ax2=plt.subplots(figsize=(10,4))
    colors_bar=[BLUE if u=="RTU" else PURPLE for u in top_courses["university"]]
    ax2.barh([f"[{u}] {c[:35]}" for u,c in zip(top_courses["university"],top_courses["course_name"])][::-1],top_courses["skills_covered"].tolist()[::-1],color=colors_bar[::-1])
    ax2.set_xlabel("Skills Covered"); ax2.set_title("Top Courses by Skill Coverage"); ax2.grid(axis="x")
    plt.tight_layout(); st.pyplot(fig2,use_container_width=True); plt.close()

# ══════════════════════════════════════════════════════════════
# TAB 4
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Recommendation System Evaluation")
    st.markdown("Evaluation using **Precision@K** and **NDCG@K** across 10 career goals.")

    if eval_df is not None:
        numeric_cols=[c for c in eval_df.columns if c!="career_goal"]
        avg=eval_df[numeric_cols].mean().round(4)
        e1,e2,e3,e4,e5,e6=st.columns(6)
        for col,metric in zip([e1,e2,e3,e4,e5,e6],numeric_cols):
            col.metric(metric,f"{avg[metric]:.3f}")
        display_eval=eval_df.copy(); display_eval.index=range(1,len(display_eval)+1)
        st.dataframe(display_eval,use_container_width=True)
        left,right=st.columns(2); x=np.arange(len(eval_df)); w=0.25
        with left:
            fig,ax=plt.subplots(figsize=(7,4))
            ax.bar(x-w,eval_df["Precision@3"],w,label="P@3",color=PURPLE)
            ax.bar(x,eval_df["Precision@5"],w,label="P@5",color=BLUE)
            ax.bar(x+w,eval_df["Precision@10"],w,label="P@10",color=GREEN)
            ax.set_xticks(x); ax.set_xticklabels([c[:12] for c in eval_df["career_goal"]],rotation=30,ha="right",fontsize=8)
            ax.set_ylabel("Precision"); ax.set_title("Precision@K by Career Goal"); ax.set_ylim(0,1.2); ax.legend(fontsize=8); ax.grid(axis="y")
            plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()
        with right:
            fig2,ax2=plt.subplots(figsize=(7,4))
            ax2.bar(x-w,eval_df["NDCG@3"],w,label="NDCG@3",color=PURPLE)
            ax2.bar(x,eval_df["NDCG@5"],w,label="NDCG@5",color=BLUE)
            ax2.bar(x+w,eval_df["NDCG@10"],w,label="NDCG@10",color=GREEN)
            ax2.set_xticks(x); ax2.set_xticklabels([c[:12] for c in eval_df["career_goal"]],rotation=30,ha="right",fontsize=8)
            ax2.set_ylabel("NDCG"); ax2.set_title("NDCG@K by Career Goal"); ax2.set_ylim(0,1.2); ax2.legend(fontsize=8); ax2.grid(axis="y")
            plt.tight_layout(); st.pyplot(fig2,use_container_width=True); plt.close()
    else:
        st.warning("⚠️ evaluation_metrics.csv not found. Run `python src/models/recommendation_system.py` first.")

    st.divider()
    st.markdown("### Model Comparison — Hybrid vs Baselines")
    if baseline_df is not None:
        numeric_cols_b=[c for c in baseline_df.columns if c not in ("model","career_goal") and pd.api.types.is_numeric_dtype(baseline_df[c])]
        avg_baseline=baseline_df.groupby("model")[numeric_cols_b].mean().round(4)
        st.markdown("#### Average Metrics by Model")
        st.dataframe(avg_baseline,use_container_width=True)
        models=avg_baseline.index.tolist(); x=np.arange(len(models)); w=0.25
        left2,right2=st.columns(2)
        with left2:
            fig3,ax3=plt.subplots(figsize=(7,4))
            ax3.bar(x-w,avg_baseline["Precision@3"].values,w,label="P@3",color=PURPLE)
            ax3.bar(x,avg_baseline["Precision@5"].values,w,label="P@5",color=BLUE)
            ax3.bar(x+w,avg_baseline["Precision@10"].values,w,label="P@10",color=GREEN)
            ax3.set_xticks(x); ax3.set_xticklabels(models,rotation=15,ha="right",fontsize=9)
            ax3.set_ylabel("Precision"); ax3.set_title("Precision@K: Hybrid vs Baselines"); ax3.set_ylim(0,1.2); ax3.legend(fontsize=8); ax3.grid(axis="y")
            plt.tight_layout(); st.pyplot(fig3,use_container_width=True); plt.close()
        with right2:
            fig4,ax4=plt.subplots(figsize=(7,4))
            ax4.bar(x-w,avg_baseline["NDCG@3"].values,w,label="NDCG@3",color=PURPLE)
            ax4.bar(x,avg_baseline["NDCG@5"].values,w,label="NDCG@5",color=BLUE)
            ax4.bar(x+w,avg_baseline["NDCG@10"].values,w,label="NDCG@10",color=GREEN)
            ax4.set_xticks(x); ax4.set_xticklabels(models,rotation=15,ha="right",fontsize=9)
            ax4.set_ylabel("NDCG"); ax4.set_title("NDCG@K: Hybrid vs Baselines"); ax4.set_ylim(0,1.2); ax4.legend(fontsize=8); ax4.grid(axis="y")
            plt.tight_layout(); st.pyplot(fig4,use_container_width=True); plt.close()
        try:
            hybrid_p5=avg_baseline.loc["Hybrid (Ours)","Precision@5"]
            best_base=avg_baseline[avg_baseline.index!="Hybrid (Ours)"]["Precision@5"].max()
            improvement=((hybrid_p5-best_base)/best_base)*100
            i1,i2,i3=st.columns(3)
            i1.metric("Hybrid Precision@5",f"{hybrid_p5:.3f}")
            i2.metric("Best Baseline P@5",f"{best_base:.3f}")
            i3.metric("Improvement",f"+{improvement:.1f}%",delta=f"+{improvement:.1f}%")
        except Exception: pass
    else:
        st.info("⚠️ baseline_comparison.csv not found. Run `python src/evaluation/baseline_comparison.py`.")

    st.divider()
    st.markdown("#### Metric Explanation")
    m1,m2=st.columns(2)
    with m1: st.markdown("**Precision@K**\nMeasures how many of the top-K recommended courses are relevant.\nScore of 1.0 = all K courses are relevant.")
    with m2: st.markdown("**NDCG@K** (Normalised Discounted Cumulative Gain)\nMeasures ranking quality — relevant courses ranked higher score better.\nScore of 1.0 = perfect ranking order.")