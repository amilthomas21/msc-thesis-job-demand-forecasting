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
**Conference:** RaTSiF-2026 Spring (April 24, 2026)

---

## 🎯 Project Overview

This research develops an AI-based system that:
1. **Forecasts** short-term university course demand using Riga job market indicators
2. **Recommends** personalized, demand-aware courses to students based on labor market needs

### Problem Statement
Traditional academic curriculum planning relies on historical enrollment trends, making it difficult to respond to rapidly changing skill demands in the labor market. Students also struggle to choose courses that align with both their interests and employability prospects.

### Solution
A data-driven approach that combines:
- Real-time job market analytics from Riga, Latvia
- Historical course enrollment data from TSI
- Machine learning forecasting models
- Demand-aware recommendation system

---

## 🔬 Research Questions

1. **RQ1:** Does including job market skill indicators as course demand forecasting factors increase forecast accuracy relative to forecasts that depend on course enrollments alone?

2. **RQ2:** Are demand-aware recommendations better than traditional content-based recommendations in terms of their relevance?

3. **RQ3:** What limitations and biases are there in the job ads method for determining the demand for skills?

---

## 🛠️ Methodology

### Data Sources
- **Job Market Data:** 
  - SS.lv (Latvia's largest classifieds)
  - CV.lv
  - LinkedIn
  - Target: 1,500-2,000 job postings from Riga
  - Categories: IT, Engineering, Transport, Business, Economics, Design

- **Enrollment Data:** 
  - TSI historical course enrollment (2-3 years)
  - Course descriptions and metadata

### Forecasting Models
- **Baseline:** ARIMA (enrollment-only)
- **Enhanced:** Random Forest (enrollment + job market features)
- **Comparison:** MAE, RMSE metrics

### Recommendation System
- **Method:** Content-based filtering using TF-IDF and cosine similarity
- **Innovation:** Demand-aware re-ranking using forecasted skill demand weights
- **Constraints:** Rule-based (prerequisites, academic level)
- **Evaluation:** Precision@K, NDCG@K

### Skill Extraction
- Lightweight NLP methods
- Keyword-based extraction from job descriptions
- Skill-to-course mapping

---

## 📁 Repository Structure

```
msc-thesis-job-demand-forecasting/
│
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                  # Files to exclude from git
├── LICENSE                     # MIT License
│
├── data/                       # Data files (not tracked in git)
│   ├── raw/                    # Original scraped data
│   ├── processed/              # Cleaned and transformed data
│   └── enrollment/             # TSI enrollment data
│
├── src/                        # Source code
│   ├── data_collection/        # Web scrapers
│   │   ├── ss_lv_scraper.py
│   │   ├── cv_lv_scraper.py
│   │   └── linkedin_scraper.py
│   │
│   ├── data_processing/        # Data cleaning and feature engineering
│   │   ├── cleaner.py
│   │   ├── skill_extractor.py
│   │   └── feature_engineering.py
│   │
│   ├── models/                 # ML models
│   │   ├── arima_model.py
│   │   ├── random_forest_model.py
│   │   └── recommendation_system.py
│   │
│   └── visualization/          # Plots and dashboard
│       ├── plots.py
│       └── dashboard.py
│
├── notebooks/                  # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_skill_extraction.ipynb
│   ├── 03_forecasting_models.ipynb
│   └── 04_recommendations.ipynb
│
├── results/                    # Model outputs and metrics
│   ├── forecasts/
│   ├── recommendations/
│   └── evaluation_metrics.csv
│
├── docs/                       # Documentation
│   ├── thesis_proposal.pdf
│   ├── conference_abstract.pdf
│   └── methodology.md
│
└── tests/                      # Unit tests
    └── test_scrapers.py
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/amilthomas21/msc-thesis-job-demand-forecasting.git
cd msc-thesis-job-demand-forecasting
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data (for NLP):**
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 💻 Usage

### 1. Data Collection

**Scrape job postings from SS.lv:**
```bash
python src/data_collection/ss_lv_scraper.py
```

**Expected output:** `data/raw/ss_lv_jobs.csv` with ~1,500-2,000 job postings

**Scrape from other sources:**
```bash
python src/data_collection/cv_lv_scraper.py
python src/data_collection/linkedin_scraper.py
```

### 2. Data Processing

**Clean and extract skills:**
```bash
python src/data_processing/cleaner.py
python src/data_processing/skill_extractor.py
```

### 3. Train Forecasting Models

**ARIMA baseline:**
```bash
python src/models/arima_model.py
```

**Random Forest with job market features:**
```bash
python src/models/random_forest_model.py
```

### 4. Generate Recommendations

**Run recommendation system:**
```bash
python src/models/recommendation_system.py
```

### 5. Launch Dashboard

**Interactive visualization:**
```bash
streamlit run src/visualization/dashboard.py
```

---

## 📊 Technologies & Libraries

### Data Collection
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `selenium` - Dynamic web scraping

### Data Processing
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `openpyxl` - Excel file handling

### Natural Language Processing
- `nltk` - Text processing
- `spacy` - Advanced NLP

### Machine Learning
- `scikit-learn` - ML algorithms and metrics
- `statsmodels` - Time series (ARIMA)
- `xgboost` - Gradient boosting (optional)

### Visualization
- `matplotlib` - Static plots
- `seaborn` - Statistical visualizations
- `plotly` - Interactive plots
- `streamlit` - Web dashboard

---

## 📈 Key Results

> [Results will be updated as the thesis progresses]

### Forecasting Performance
- ARIMA (Baseline): MAE = ?, RMSE = ?
- Random Forest (Enhanced): MAE = ?, RMSE = ?
- Improvement: ?%

### Recommendation Evaluation
- Content-based only: Precision@5 = ?, NDCG@5 = ?
- Demand-aware: Precision@5 = ?, NDCG@5 = ?
- Improvement: ?%

---

## 📅 Project Timeline

- **Feb 2026:** Data collection, literature review
- **Mar 2026:** Data processing, skill extraction
- **Apr 2026:** Model development, conference presentation
- **May 2026:** Evaluation, thesis writing, defense preparation

---

## 🎓 Academic Contributions

1. **Novel Framework:** Integration of job market analytics with course demand forecasting
2. **Practical Application:** Demand-aware course recommendation system
3. **Empirical Validation:** Evaluation of external labor market signals in educational analytics
4. **Decision Support Tool:** Interactive dashboard for academic planning

---

## 📝 Publications & Presentations

- **RaTSiF-2026 Spring Conference** (April 24, 2026)  
  *Presentation:* AI-Driven Course Demand Forecasting Using Job Market Indicators

---

## 🤝 Contributing

This is an academic research project. If you have suggestions or find issues, please:
1. Open an issue on GitHub
2. Contact: [Your email if you want to share]

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Supervisor:** Nadežda Spiridovska (TSI)
- **Institution:** Transport and Telecommunication Institute (TSI)
- **Program:** MSc Double Degree - Data Analytics and Artificial Intelligence
- **Partner:** University of the West of England (UWE Bristol)

---

## 📧 Contact

**Amil Thomas**  
MSc Student - Data Analytics & AI  
Transport and Telecommunication Institute  
Riga, Latvia

- GitHub: [@amilthomas21](https://github.com/amilthomas21)
- LinkedIn: [Your LinkedIn if you want to add]

---

## 📚 References

> [Will be populated from thesis bibliography]

Key papers cited in this research:
- Educational Data Mining techniques
- Job market analytics methodologies  
- Time series forecasting in education
- Recommendation systems in learning environments

---

**Last Updated:** February 18, 2026  
**Status:** 🚧 Work in Progress - Data Collection Phase
