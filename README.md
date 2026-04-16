# msc-thesis-job-demand-forecasting
# "Job Market Skill Demand Analysis and Skill-Based Course Recommendation Framework"

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📚 Master's Thesis Project

**Author:** Amil Thomas  
**Program:** MSc Double Degree - Data Analytics and Artificial Intelligence  
**Institution:** Transport and Telecommunication Institute (TSI), Riga, Latvia  
**Supervisor:** Nadežda Spiridovska  
**Student ID:** st87613  
🎯 Project Overview
This research develops a data-driven, demand-aware course recommendation framework for the Riga, Latvia job market. The framework extracts skill demand signals from real job postings, maps them against university course offerings, identifies curriculum gaps, and recommends relevant courses to students based on their career goals and current market demand.
Live Dashboard: https://msc-thesis-job-demand-forecasting-nzbbgbtc4nrdhg2p9wszv5.streamlit.app
Case Study: Two Riga universities — Transport and Telecommunication Institute (TSI) and Riga Technical University (RTU).

📊 Key Results
MetricValueJob postings collected3,057 (CV.lv: 2,416 · SS.lv: 641)Collection periodSeptember 2025 – February 2026Languages processedEnglish, Latvian, RussianUnique skills identified321 across 17 categoriesTotal skill mentions11,159Pipeline coverage rate85.4%TSI courses112RTU courses497Total courses609Skill-course mappings3,205High-demand skills covered77% (63 of 82)Critical gaps identified12 high-demand skills (Docker, Kubernetes, 1C, etc.)Hybrid model Precision@51.000 (+11.1% vs content-only baseline)Hybrid model NDCG@51.000 (+47.1% vs demand-only baseline)Career profiles evaluated10References63

Note on evaluation scores: Precision@5 = 1.000 reflects internal system consistency under a closed evaluation design (relevance labels share the same source as the ranking signal). These scores should be interpreted as relative comparisons between the three models, not as generalised predictive performance. See Section 4.5.3 of the thesis for full discussion.


🔬 Research Questions

RQ1: What skills are most frequently demanded by employers in the Riga labour market, and how do they distribute across demand levels and domains?
RQ2: How do the curricula of TSI and RTU align with Riga labour market skill demands, and which high-demand skills are absent from both institutions?
RQ3: Can a hybrid demand-aware recommendation system incorporating TF-IDF content similarity, market demand scoring, and skill coverage scoring provide more relevant course recommendations than content-based or demand-based approaches alone?


🛠️ Methodology
Data Collection
Job posting data was collected from two major Latvian employment portals:

CV.lv — Latvia's largest professional job portal (2,416 postings)
SS.lv — Latvia's largest classified advertisement platform (641 postings)

Multilingual Skill Extraction Pipeline (4 Layers)
LayerMethodTargetCoverage Added1English keyword matching (438 terms)English postings74.1%2Latvian inflection-aware matching (318 terms)Latvian postings+5.7%3TF-IDF cosine similarityAll postings+3.4%4Fuzzy string matching (85% threshold)Russian/typos+2.2%TotalCombined pipelineAll languages85.4%
Skill Demand Analysis
Skills are classified into 17 categories and assigned to demand tiers (High / Moderate / Low) based on frequency across the 3,057-posting corpus. Top skills: Excel, Communication skills, Customer service, Accounting, Financial analysis.
Skill-to-Course Mapping
Two-layer mapping combining keyword matching and TF-IDF cosine similarity (threshold: 0.15) against 609 courses from TSI and RTU, producing 3,205 skill-course correspondences.
Hybrid Recommendation System
Three-component weighted scoring:
FinalScore = 0.5 × ContentSim + 0.3 × DemandScore + 0.2 × SkillCoverage
Evaluated across 10 career profiles: Data Engineer, Data Scientist, Software Developer, IT Project Manager, Cybersecurity Analyst, Business Analyst, Cloud Engineer, Logistics Manager, UX/UI Designer, Network Engineer.

📁 Repository Structure
msc-thesis-job-demand-forecasting/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── CHANGELOG.md
│
├── data/                          # Data files (excluded from git)
│   ├── raw/                       # Original scraped job postings
│   └── processed/                 # Cleaned and skill-extracted data
│       ├── master_jobs_clean.csv
│       ├── job_skills_v4.csv
│       ├── skill_demand_v4.csv
│       ├── tsi_courses.csv
│       ├── rtu_courses_final.csv
│       └── course_skill_matches.csv
│
├── src/
│   ├── data_collection/           # Web scrapers
│   │   ├── ss_lv_scraper.py
│   │   └── cv_lv_scraper.py
│   ├── data_processing/           # Cleaning and skill extraction
│   │   ├── clean_data.py
│   │   ├── extract_skills_v4.py
│   │   ├── skill_keywords_v3.py
│   │   └── latvian_skills.py
│   ├── analysis/                  # Gap analysis and network
│   │   ├── frequency_analysis.py
│   │   ├── course_skill_mapping.py
│   │   ├── gap_analysis.py
│   │   └── skill_network.py
│   ├── models/                    # Recommendation system
│   │   └── recommendation_system.py
│   └── evaluation/                # Baseline comparison
│       └── baseline_comparison.py
│
├── dashboard/                     # Streamlit dashboard
│   └── app.py
│
├── results/
│   ├── figures/                   # All generated figures
│   ├── tables/                    # CSV outputs
│   ├── recommendations/           # Per-profile recommendation CSVs
│   └── evaluation/                # Evaluation metrics
│
└── docs/
    └── thesis_proposal.pdf

🚀 Installation and Setup
Prerequisites

Python 3.11+
pip

Install
bashgit clone https://github.com/amilthomas21/msc-thesis-job-demand-forecasting.git
cd msc-thesis-job-demand-forecasting
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
Run the Dashboard
bashstreamlit run dashboard/app.py
Or access the live version: https://msc-thesis-job-demand-forecasting-nzbbgbtc4nrdhg2p9wszv5.streamlit.app

📦 Libraries Used
ComponentLibraryVersionWeb scrapingBeautifulSoup4, Requests4.12, 2.31Language detectionlangdetect1.0.9Text processingNLTK, spaCy3.8, 3.6Fuzzy matchingfuzzywuzzy0.18TF-IDF and similarityscikit-learn1.3Network analysisNetworkX3.1DashboardStreamlit1.28Data manipulationpandas, numpy2.0, 1.24Visualisationmatplotlib, seaborn3.7, 0.12
Full dependency list: requirements.txt

🔑 Key Findings

Top demanded skills in Riga: Excel (15.4%), Communication skills (11.7%), Customer service (10.7%), Accounting (9.7%), Financial analysis (8.1%)
Language requirements: 67.4% require Latvian, 57.3% English, 9.1% Russian
77% of high-demand skills are well covered by the combined TSI–RTU curriculum
12 critical gaps exist in both curricula: Docker, Kubernetes, 1C, Microsoft Office, Technical support, Network administration, Troubleshooting, Microsoft Word, IT infrastructure, Contract management, PowerPoint, Technical drawing
Hybrid model outperforms content-only baseline by 11.1% and demand-only baseline by 47.1% on Precision@5


⚠️ Scope and Limitations
This study is an applied case study conducted within the Riga, Latvia context. Both institutions (TSI and RTU) operate within the same city, labour market, and national educational system. While the methodology is designed to be institution-independent, broader generalisation to other regions or educational systems would require recalibration of the skill dictionary and revalidation of pipeline thresholds. This study should be understood as a regional proof-of-concept rather than a proven cross-regional system.

📝 Publication
RaTSiF-2026 Spring Conference, April 24, 2026, TSI Riga
"Job Market Skill Demand Analysis and Skill-Based Course Recommendation Framework"

📄 License
MIT License — see LICENSE for details.

🙏 Acknowledgements
Supervisor: Nadežda Spiridovska, TSI Riga
Institution: Transport and Telecommunication Institute (TSI), Riga, Latvia

Last updated: April 2026 · Status: ✅ Complete
