# msc-thesis-job-demand-forecasting
# "Job Market Skill Demand Forecasting and Skill-Based Course Recommendation Framework"

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📚 Master's Thesis Project

**Author:** Amil Thomas  
**Program:** MSc Double Degree - Data Analytics and Artificial Intelligence  
**Institution:** Transport and Telecommunication Institute (TSI), Riga, Latvia  
**Supervisor:** Nadežda Spiridovska  
**Student ID:** st87613  
🎯 Project Overview
This research develops a generalizable AI-based framework that:

Forecasts skill demand trends in regional job markets using time series analysis
Maps job market skills to university course content systematically
Recommends personalized, demand-aware courses to students based on labor market needs
Analyzes curriculum coverage of in-demand skills

Case Study Implementation: TSI (Transport and Telecommunication Institute) using Riga/Latvia job market data
Problem Statement
Universities struggle to align curricula with rapidly evolving job market demands. Traditional curriculum planning relies on historical enrollment trends, making it difficult to respond to changing skill requirements. Students also lack guidance on which courses best prepare them for employment in their regional job market.
Solution
A data-driven framework that combines:

Real-time job market analytics from Riga, Latvia (1,500-2,000 job postings)
NLP-based skill extraction from job descriptions
Time series forecasting of skill demand trends
TF-IDF + cosine similarity for skill-to-course mapping
Demand-aware course recommendation system

Key Innovation: Integrating external labor market signals with educational course planning to create a generalizable framework applicable to any university and regional market.

🔬 Research Questions

RQ1: Which skills show the highest growth in the Riga job market?
RQ2: How can job market skill trends be systematically mapped to university course content?
RQ3: How well does TSI's current curriculum cover in-demand skills?
RQ4: Can a skill-based recommendation framework effectively guide students' course selection?


🛠️ Methodology
Data Sources
Job Market Data:

SS.lv (Latvia's largest classifieds platform)
CV.lv (Professional job portal)
LikeIT.lv (IT-specific jobs)
VisiDarbi.lv (Job aggregator)
Target: 1,500-2,000 job postings from Riga
Categories: IT, Engineering, Transport, Business, Economics, Design

TSI Course Data:

Course descriptions
Learning outcomes
Syllabi
Program structures

Skill Demand Forecasting

Method: Time series analysis of historical skill frequency data
Techniques: Trend analysis, growth rate calculation
Output: Identification of emerging and declining skills

General Framework Development
Skill-to-Course Mapping:

TF-IDF vectorization of job postings and course descriptions
Cosine similarity for matching skill vocabulary to course content
Skill taxonomy and standardization
Demand-aware ranking mechanisms

TSI Case Study Implementation
Components:

Skill extraction from Riga job postings using keyword dictionaries
Skill demand trend forecasting
Course content parsing and skill identification
Skill-to-course mapping matrix construction
Recommendation system with demand-aware re-ranking
Curriculum coverage analysis

Recommendation System

Method: Content-based filtering using TF-IDF and cosine similarity
Innovation: Demand-aware re-ranking using forecasted skill growth rates
Constraints: Rule-based (prerequisites, academic level requirements)
Evaluation: Precision@K, NDCG@K, user relevance assessment

Skill Extraction

Lightweight NLP methods (keyword-based dictionaries)
Predefined skill taxonomies (Python, SQL, Machine Learning, Project Management, etc.)
Skill-to-course mapping using document similarity techniques


📁 Repository Structure
msc-thesis-job-demand-forecasting/
│
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                  # Files to exclude from git
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Project progress tracking
│
├── data/                       # Data files (not tracked in git)
│   ├── raw/                    # Original scraped job postings
│   ├── processed/              # Cleaned and skill-extracted data
│   └── tsi_courses/            # TSI course descriptions and metadata
│
├── src/                        # Source code
│   ├── data_collection/        # Web scrapers
│   │   ├── ss_lv_scraper.py
│   │   ├── cv_lv_scraper.py
│   │   ├── likeIT_lv.py
│   │   └── VisiDarbi_lv.py
│   │
│   ├── data_processing/        # Data cleaning and feature engineering
│   │   ├── cleaner.py
│   │   ├── skill_extractor.py
│   │   └── skill_mapper.py
│   │
│   ├── models/                 # Forecasting and recommendation models
│   │   ├── skill_forecasting.py
│   │   ├── tfidf_mapper.py
│   │   └── recommendation_system.py
│   │
│   └── visualization/          # Plots and dashboard
│       ├── plots.py
│       └── dashboard.py
│
├── notebooks/                  # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_skill_extraction.ipynb
│   ├── 03_skill_forecasting.ipynb
│   └── 04_recommendations.ipynb
│
├── results/                    # Model outputs and metrics
│   ├── skill_trends/
│   ├── recommendations/
│   ├── curriculum_analysis/
│   └── evaluation_metrics.csv
│
├── docs/                       # Documentation
│   ├── thesis_proposal.pdf
│   ├── conference_abstract.pdf
│   └── methodology.md
│
└── tests/                      # Unit tests
    └── test_scrapers.py

🚀 Installation & Setup
Prerequisites

Python 3.8 or higher
pip package manager
Git

Installation

Clone the repository:

bashgit clone https://github.com/amilthomas21/msc-thesis-job-demand-forecasting.git
cd msc-thesis-job-demand-forecasting

Create virtual environment (recommended):

bashpython -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

Install dependencies:

bashpip install -r requirements.txt

Download NLTK data (for NLP):

pythonpython -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

💻 Usage
1. Data Collection
Scrape job postings from SS.lv:
bashpython src/data_collection/ss_lv_scraper.py
Expected output: data/raw/ss_lv_jobs.csv with ~800-1,000 job postings
Scrape from other sources:
bashpython src/data_collection/cv_lv_scraper.py
python src/data_collection/likeIT_lv.py
python src/data_collection/VisiDarbi_lv.py
2. Data Processing & Skill Extraction
Clean and extract skills:
bashpython src/data_processing/cleaner.py
python src/data_processing/skill_extractor.py
3. Skill Demand Forecasting
Analyze skill trends:
bashpython src/models/skill_forecasting.py
4. Skill-to-Course Mapping
Map job market skills to TSI courses:
bashpython src/models/tfidf_mapper.py
5. Generate Recommendations
Run recommendation system:
bashpython src/models/recommendation_system.py
6. Launch Dashboard
Interactive visualization:
bashstreamlit run src/visualization/dashboard.py

📊 Technologies & Libraries
Data Collection

requests - HTTP requests
beautifulsoup4 - HTML parsing
selenium - Dynamic web scraping (if needed)

Data Processing

pandas - Data manipulation
numpy - Numerical operations

Natural Language Processing

nltk - Text processing
scikit-learn - TF-IDF vectorization, cosine similarity

Forecasting & Analysis

statsmodels - Time series analysis
matplotlib, seaborn - Visualization

Recommendation System

scikit-learn - TF-IDF, cosine similarity
pandas - Data manipulation

Dashboard

streamlit - Interactive web dashboard
plotly - Interactive plots


📈 Expected Results

[Results will be updated as the thesis progresses]

Skill Demand Trends

Top 10 growing skills in Riga job market
Emerging vs. declining skill identification
Temporal skill demand patterns

TSI Curriculum Analysis

Coverage percentage of in-demand skills
Skill gap identification
Course-skill mapping matrix

Recommendation Performance

Precision@K, NDCG@K metrics
User relevance assessment
Comparison with baseline content-based system


📅 Project Timeline

Feb 2026: Data collection, skill extraction
Mar 2026: Skill forecasting, framework development
Apr 2026: TSI implementation, conference presentation (RaTSiF-2026)
May 2026: Evaluation, thesis writing, defense preparation


🎓 Academic Contributions

Generalizable Framework: Institution-independent methodology for skill forecasting and course mapping
Novel Integration: Combining job market analytics with educational course planning
Practical Tool: Skill-based recommendation system applicable across disciplines
Empirical Validation: Evaluation of external labor market signals in curriculum analysis
Decision Support: Insights for both students (course selection) and institutions (planning)


🌍 Scope and Applicability
General Framework
The methodology is designed to be institution-agnostic and adaptable to:

Any university or educational institution
Any regional job market
Students across all academic disciplines

TSI Case Study
TSI serves as proof-of-concept demonstrating framework effectiveness with:

Real-world Riga/Latvia job market data
Actual TSI course catalog
Validation with local context

Future Applicability
Other institutions can adopt this framework by:

Collecting job postings from their regional market
Parsing their course catalog
Applying the skill extraction and mapping methodology
Implementing the recommendation system


📝 Publications & Presentations

RaTSiF-2026 Spring Conference (April 24, 2026)
Abstract deadline: March 16, 2026
Presentation: Job Market Skill Demand Forecasting Framework


📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

Supervisor: Nadežda Spiridovska (TSI)
Institution: Transport and Telecommunication Institute (TSI), Riga
Program: MSc Double Degree - Data Analytics and Artificial Intelligence
Partner: University of the West of England (UWE Bristol)


📧 Contact
Amil Thomas
MSc Student - Data Analytics & AI
Transport and Telecommunication Institute
Riga, Latvia

GitHub: @amilthomas21
Student ID: st87613


📚 Key References
Literature review includes 30 papers covering:

Educational Data Mining and Learning Analytics
Job Market Analytics and Skill Extraction
Time Series Forecasting in Education
Recommendation Systems
TF-IDF and Information Retrieval

Full bibliography available in thesis document.

Last Updated: February 22, 2026
Status: 🚧 Work in Progress - Data Collection Phase

⭐ Project Highlights

✅ 4 web scrapers implemented (SS.lv, CV.lv, LikeIT, VisiDarbi)
✅ Professional repository structure
✅ Comprehensive methodology documentation
✅ 30-paper literature review completed
⏳ Data collection in progress
⏳ Framework implementation ongoing
