# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### 2026-02-18 - Initial Setup
#### Added
- Created GitHub repository
- Implemented SS.lv multi-category web scraper
  - Supports 21+ job categories (IT, Engineering, Transport, Business, etc.)
  - Configurable pages per category
  - Automatic rate limiting and error handling
- Created page counter utility to determine data availability
  - Discovered ~6,300-8,400 jobs available across 21 categories
  - Planning to collect ~1,500-2,000 jobs (representative sample)
- Set up project documentation
  - README.md with comprehensive project overview
  - requirements.txt with all dependencies
  - .gitignore for version control
  - MIT License

#### In Progress
- Data collection from SS.lv (first 5 pages per category)
- Validation sampling strategy (pages 10-15 for 3 categories)
- Waiting for TSI enrollment data from supervisor

#### Planned
- CV.lv scraper implementation
- LinkedIn scraper implementation
- Data cleaning and preprocessing pipeline
- Skill extraction from job descriptions
- ARIMA baseline forecasting model
- Random Forest enhanced forecasting model
- Content-based recommendation system
- Demand-aware re-ranking algorithm
- Interactive dashboard (Streamlit)

### Current Status
**Phase:** Data Collection (Week 1-2)  
**Progress:** 30%  
**Next Milestone:** Complete job market data collection by Feb 25, 2026

---

## Project Milestones

### ✅ Completed
- [x] Thesis proposal approved
- [x] Literature review (24 papers collected)
- [x] GitHub repository setup
- [x] SS.lv web scraper developed
- [x] Data availability assessment

### 🔄 In Progress
- [ ] Job market data collection (~1,500-2,000 jobs)
- [ ] TSI enrollment data acquisition
- [ ] Conference abstract draft (due March 16)

### 📅 Upcoming
- [ ] Data cleaning and preprocessing (Week 3-4)
- [ ] Skill extraction and mapping (Week 4)
- [ ] Feature engineering (Week 5)
- [ ] ARIMA baseline model (Week 5)
- [ ] Random Forest enhanced model (Week 6)
- [ ] Recommendation system (Week 6-7)
- [ ] Dashboard development (Week 7)
- [ ] Conference presentation preparation (Week 8)
- [ ] RaTSiF-2026 presentation (April 24)
- [ ] Thesis writing (Week 9-12)
- [ ] Thesis defense (May 2026)

---

## Notes

### Sampling Strategy Decision
After discovering 420 pages (6,300-8,400 jobs) available on SS.lv, decided to use stratified sampling:
- **Rationale:** Temporal relevance (recent postings = current demand)
- **Sample size:** 5 pages per category = ~1,800 jobs (28% of population)
- **Validation:** Will scrape pages 10-15 for 3 random categories to verify representativeness

### Technologies Stack
- **Language:** Python 3.8+
- **Web Scraping:** requests, BeautifulSoup
- **Data Processing:** pandas, numpy
- **NLP:** nltk, spacy
- **ML:** scikit-learn, statsmodels
- **Visualization:** matplotlib, seaborn, plotly
- **Dashboard:** Streamlit

---

## Future Updates

This changelog will be updated regularly as the project progresses. Each significant milestone, code commit, or decision will be documented here.

**Last Updated:** February 18, 2026  
**Updated By:** Amil Thomas