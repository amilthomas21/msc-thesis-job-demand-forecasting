"""
Skill-to-Course Mapping Pipeline
Maps extracted job market skills to TSI and RTU courses using:
1. Direct keyword matching (course name contains skill keyword)
2. TF-IDF cosine similarity (semantic matching)
"""

import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_TO_TERMS = {
    "Python":               ["python", "programming", "scripting"],
    "Java":                 ["java", "programming", "object-oriented"],
    "JavaScript":           ["javascript", "web", "frontend", "scripting"],
    "TypeScript":           ["typescript", "javascript", "web"],
    "PHP":                  ["php", "web", "server"],
    "C#":                   ["c#", ".net", "programming"],
    "C++":                  ["c++", "programming", "systems"],
    "Kotlin":               ["kotlin", "android", "mobile"],
    "Golang":               ["go", "golang", "systems"],
    "Scala":                ["scala", "functional", "big data"],
    "Bash":                 ["bash", "shell", "linux", "scripting"],
    "HTML":                 ["html", "web", "frontend", "markup"],
    "CSS":                  ["css", "web", "frontend", "styling"],
    "React":                ["react", "frontend", "javascript", "ui"],
    "Angular":              ["angular", "frontend", "javascript"],
    "Vue.js":               ["vue", "frontend", "javascript"],
    "Node.js":              ["node", "backend", "javascript", "server"],
    ".NET":                 [".net", "asp", "microsoft", "c#"],
    "REST API":             ["api", "rest", "web services", "http"],
    "GraphQL":              ["graphql", "api", "query"],
    "Web design":           ["web design", "ux", "ui", "frontend"],
    "SQL":                  ["sql", "database", "query", "relational"],
    "PostgreSQL":           ["postgresql", "postgres", "database"],
    "MySQL":                ["mysql", "database", "sql"],
    "MongoDB":              ["mongodb", "nosql", "document"],
    "Redis":                ["redis", "cache", "nosql"],
    "NoSQL":                ["nosql", "mongodb", "document", "graph"],
    "Database design":      ["database", "data modeling", "schema", "normalization"],
    "ETL":                  ["etl", "data pipeline", "extract", "transform"],
    "Data warehousing":     ["data warehouse", "olap", "data mart", "bi"],
    "Oracle":               ["oracle", "database", "sql"],
    "Elasticsearch":        ["elasticsearch", "search", "indexing"],
    "AWS":                  ["aws", "amazon", "cloud", "s3", "ec2"],
    "Azure":                ["azure", "microsoft cloud", "cloud"],
    "Google Cloud":         ["google cloud", "gcp", "cloud"],
    "Docker":               ["docker", "container", "containerization"],
    "Kubernetes":           ["kubernetes", "k8s", "container orchestration"],
    "CI/CD":                ["ci/cd", "devops", "pipeline", "automation", "jenkins"],
    "Linux":                ["linux", "unix", "operating system", "bash"],
    "DevOps":               ["devops", "automation", "ci/cd", "deployment"],
    "Terraform":            ["terraform", "infrastructure", "iac"],
    "Microservices":        ["microservices", "distributed", "architecture"],
    "Machine learning":     ["machine learning", "ml", "predictive", "model"],
    "Deep learning":        ["deep learning", "neural network", "cnn", "rnn"],
    "Data science":         ["data science", "analytics", "statistics", "ml"],
    "Data analysis":        ["data analysis", "analytics", "statistics", "excel"],
    "Data analytics":       ["data analytics", "business intelligence", "reporting"],
    "TensorFlow":           ["tensorflow", "deep learning", "neural network"],
    "PyTorch":              ["pytorch", "deep learning", "neural network"],
    "Statistics":           ["statistics", "probability", "mathematical", "analysis"],
    "Business Intelligence":["business intelligence", "bi", "analytics", "reporting"],
    "Power BI":             ["power bi", "business intelligence", "reporting", "dashboard"],
    "Tableau":              ["tableau", "visualization", "dashboard", "reporting"],
    "Data visualization":   ["visualization", "dashboard", "reporting", "charts"],
    "NLP":                  ["nlp", "natural language", "text mining", "linguistics"],
    "Computer vision":      ["computer vision", "image processing", "cnn"],
    "Data engineering":     ["data engineering", "pipeline", "etl", "spark"],
    "Apache Spark":         ["spark", "big data", "distributed computing"],
    "Hadoop":               ["hadoop", "big data", "distributed", "mapreduce"],
    "Git":                  ["git", "version control", "github", "gitlab"],
    "Agile":                ["agile", "scrum", "kanban", "sprint"],
    "Scrum":                ["scrum", "agile", "sprint", "backlog"],
    "JIRA":                 ["jira", "project management", "issue tracking"],
    "Software architecture":["software architecture", "design patterns", "systems design"],
    "OOP":                  ["object-oriented", "oop", "classes", "inheritance"],
    "Unit testing":         ["testing", "unit test", "quality assurance", "tdd"],
    "API development":      ["api", "rest", "web services", "backend"],
    "Debugging":            ["debugging", "testing", "quality", "troubleshooting"],
    "Code review":          ["code review", "software quality", "best practices"],
    "Cybersecurity":        ["cybersecurity", "security", "information security", "protection"],
    "Information security": ["information security", "cybersecurity", "data protection"],
    "Network security":     ["network security", "firewall", "vpn", "intrusion"],
    "VPN":                  ["vpn", "network", "security", "remote"],
    "Firewall":             ["firewall", "network security", "protection"],
    "Penetration testing":  ["penetration testing", "ethical hacking", "vulnerability"],
    "DNS":                  ["dns", "network", "domain", "tcp/ip"],
    "GDPR compliance":      ["gdpr", "data protection", "compliance", "privacy"],
    "Encryption":           ["encryption", "cryptography", "security"],
    "Active Directory":     ["active directory", "ldap", "identity", "windows server"],
    "Troubleshooting":      ["troubleshooting", "technical support", "it support"],
    "Technical support":    ["technical support", "helpdesk", "it support"],
    "IT support":           ["it support", "helpdesk", "technical support"],
    "Microsoft 365":        ["microsoft 365", "office 365", "microsoft", "cloud"],
    "ITIL":                 ["itil", "it service", "service management"],
    "Project management":   ["project management", "planning", "scheduling", "delivery"],
    "Risk management":      ["risk management", "risk analysis", "mitigation"],
    "Stakeholder management":["stakeholder", "communication", "project"],
    "Agile methodology":    ["agile", "scrum", "kanban", "iterative"],
    "Accounting":           ["accounting", "financial", "bookkeeping", "audit"],
    "Financial analysis":   ["financial analysis", "finance", "investment", "valuation"],
    "Excel":                ["excel", "spreadsheet", "microsoft office", "data"],
    "ERP":                  ["erp", "enterprise resource", "sap", "business systems"],
    "SAP":                  ["sap", "erp", "enterprise", "business systems"],
    "Business analysis":    ["business analysis", "requirements", "process", "stakeholder"],
    "Compliance":           ["compliance", "regulation", "legal", "audit"],
    "Reporting":            ["reporting", "dashboard", "analytics", "kpi"],
    "KPI":                  ["kpi", "metrics", "performance", "reporting"],
    "Budgeting":            ["budgeting", "financial planning", "cost", "forecast"],
    "Auditing":             ["audit", "compliance", "financial control"],
    "Procurement":          ["procurement", "purchasing", "supply chain", "vendor"],
    "Logistics management": ["logistics", "supply chain", "transportation", "distribution"],
    "Supply chain":         ["supply chain", "logistics", "procurement", "inventory"],
    "Warehouse management": ["warehouse", "inventory", "storage", "logistics"],
    "Inventory management": ["inventory", "stock", "warehouse", "supply chain"],
    "Demand planning":      ["demand planning", "forecasting", "supply chain"],
    "Lean":                 ["lean", "six sigma", "process improvement", "efficiency"],
    "AutoCAD":              ["autocad", "cad", "technical drawing", "design"],
    "BIM":                  ["bim", "revit", "building information", "construction"],
    "Revit":                ["revit", "bim", "architectural", "building"],
    "IoT":                  ["iot", "internet of things", "embedded", "sensors"],
    "Electrical engineering":["electrical", "electronics", "circuit", "power"],
    "Mechanical engineering":["mechanical", "machines", "engineering", "dynamics"],
    "Civil engineering":    ["civil", "structural", "construction", "building"],
    "PLC programming":      ["plc", "automation", "industrial", "scada"],
    "SCADA":                ["scada", "industrial automation", "plc", "control systems"],
    "Embedded systems":     ["embedded", "firmware", "microcontroller", "iot"],
    "Electronics":          ["electronics", "circuit", "electrical", "signals"],
    "UI/UX":                ["ui", "ux", "user interface", "user experience", "design"],
    "Figma":                ["figma", "ui design", "prototyping", "wireframe"],
    "Photoshop":            ["photoshop", "graphic design", "adobe", "image"],
    "Graphic design":       ["graphic design", "visual", "typography", "adobe"],
    "Prototyping":          ["prototyping", "wireframe", "mockup", "ux"],
    "User research":        ["user research", "ux", "usability", "human-computer"],
    "Digital marketing":    ["digital marketing", "seo", "social media", "online"],
    "SEO":                  ["seo", "search engine", "digital marketing", "web"],
    "CRM":                  ["crm", "customer relationship", "salesforce", "customer"],
    "Google Analytics":     ["analytics", "google analytics", "web analytics", "tracking"],
    "Content marketing":    ["content", "marketing", "copywriting", "communication"],
    "Communication skills": ["communication", "presentation", "interpersonal", "teamwork"],
    "Leadership":           ["leadership", "management", "team", "strategy"],
    "Problem solving":      ["problem solving", "analytical", "critical thinking"],
    "Teamwork":             ["teamwork", "collaboration", "team", "communication"],
    "Negotiation":          ["negotiation", "communication", "business", "stakeholder"],
    "Customer service":     ["customer service", "client relations", "support"],
    "Attention to detail":  ["quality", "accuracy", "precision", "detail"],
    "English":              ["english", "language", "communication"],
    "Latvian":              ["latvian", "language", "latvija"],
    "Russian":              ["russian", "language"],
    "German":               ["german", "deutsch", "language"],
}


def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.lower().strip()


def keyword_match(text: str, skill: str, terms: list) -> bool:
    t = normalize(text)
    for term in terms:
        if term.lower() in t:
            return True
    return False


def build_course_text(df: pd.DataFrame) -> pd.DataFrame:
    """Build rich matching text for each course"""
    df = df.copy()
    # TSI has topics + description; RTU has programme + faculty
    # Combine everything available
    df['match_text'] = (
        df.get('course_name', pd.Series([''] * len(df))).fillna('') + ' ' +
        df.get('programme', pd.Series([''] * len(df))).fillna('') + ' ' +
        df.get('faculty', pd.Series([''] * len(df))).fillna('') + ' ' +
        df.get('topics', pd.Series([''] * len(df))).fillna('') + ' ' +
        df.get('description', pd.Series([''] * len(df))).fillna('')
    )
    return df


def keyword_matching(courses_df: pd.DataFrame, skills: list) -> pd.DataFrame:
    records = []
    for _, course in courses_df.iterrows():
        for skill in skills:
            terms = SKILL_TO_TERMS.get(skill, [skill.lower()])
            if keyword_match(course['match_text'], skill, terms):
                records.append({
                    'university':   course['university'],
                    'programme':    course.get('programme', ''),
                    'level':        course.get('level', ''),
                    'course_code':  course['course_code'],
                    'course_name':  course['course_name'],
                    'skill':        skill,
                    'match_method': 'keyword',
                    'score':        1.0,
                })
    return pd.DataFrame(records)


def tfidf_matching(courses_df: pd.DataFrame, skills: list,
                   threshold: float = 0.15) -> pd.DataFrame:
    skill_docs = []
    for skill in skills:
        terms = SKILL_TO_TERMS.get(skill, [skill.lower()])
        skill_docs.append(skill + ' ' + ' '.join(terms))

    course_docs = courses_df['match_text'].tolist()
    all_docs = course_docs + skill_docs

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        stop_words='english',
        max_features=5000,
    )
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    course_vectors = tfidf_matrix[:len(course_docs)]
    skill_vectors  = tfidf_matrix[len(course_docs):]
    sim_matrix = cosine_similarity(course_vectors, skill_vectors)

    records = []
    for row_idx, (_, course) in enumerate(courses_df.iterrows()):
        for s_idx, skill in enumerate(skills):
            score = sim_matrix[row_idx, s_idx]
            if score >= threshold:
                records.append({
                    'university':   course['university'],
                    'programme':    course.get('programme', ''),
                    'level':        course.get('level', ''),
                    'course_code':  course['course_code'],
                    'course_name':  course['course_name'],
                    'skill':        skill,
                    'match_method': 'tfidf',
                    'score':        round(float(score), 4),
                })
    return pd.DataFrame(records)


def merge_matches(kw_df, tfidf_df):
    frames = [df for df in [kw_df, tfidf_df] if not df.empty]
    if not frames:
        return pd.DataFrame(columns=['university','programme','level',
                                     'course_code','course_name','skill',
                                     'match_method','score'])
    combined = pd.concat(frames, ignore_index=True)
    combined = (
        combined
        .sort_values('score', ascending=False)
        .drop_duplicates(subset=['course_code', 'skill'])
        .reset_index(drop=True)
    )
    return combined


def build_skill_coverage(matches_df, all_skills, demand_df):
    if matches_df.empty:
        coverage = demand_df[['skill','frequency','job_coverage_pct','demand_tier']].copy()
        coverage['total_courses'] = 0
        coverage['tsi_courses'] = 0
        coverage['rtu_courses'] = 0
        coverage['coverage_status'] = 'GAP — Not Covered'
        return coverage

    tsi_counts = (matches_df[matches_df['university']=='TSI']
                  .groupby('skill')['course_name'].nunique()
                  .rename('tsi_courses'))
    rtu_counts = (matches_df[matches_df['university']=='RTU']
                  .groupby('skill')['course_name'].nunique()
                  .rename('rtu_courses'))
    total_counts = (matches_df
                    .groupby('skill')['course_name'].nunique()
                    .rename('total_courses'))

    coverage = (demand_df[['skill','frequency','job_coverage_pct','demand_tier']]
                .join(total_counts, on='skill')
                .join(tsi_counts, on='skill')
                .join(rtu_counts, on='skill'))

    coverage['total_courses'] = coverage['total_courses'].fillna(0).astype(int)
    coverage['tsi_courses']   = coverage['tsi_courses'].fillna(0).astype(int)
    coverage['rtu_courses']   = coverage['rtu_courses'].fillna(0).astype(int)

    def status(row):
        if row['total_courses'] == 0 and row['frequency'] > 0:
            return 'GAP — Not Covered'
        elif row['total_courses'] == 0:
            return 'Not in demand'
        elif row['total_courses'] >= 3:
            return 'Well Covered'
        else:
            return 'Partially Covered'

    coverage['coverage_status'] = coverage.apply(status, axis=1)
    coverage = coverage.sort_values('frequency', ascending=False).reset_index(drop=True)
    coverage['rank'] = coverage.index + 1
    return coverage


def main():
    print("=" * 65)
    print("SKILL-TO-COURSE MAPPING PIPELINE")
    print("=" * 65)

    tsi_path    = 'data/processed/tsi_courses.csv'
    rtu_path    = 'data/processed/rtu_courses_final.csv'
    demand_path = 'data/processed/skill_demand_v4.csv'

    # ── Load TSI ───────────────────────────────────────────────────
    if os.path.exists(tsi_path):
        tsi_df = pd.read_csv(tsi_path)
        tsi_df = tsi_df.rename(columns={'code': 'course_code', 'title': 'course_name'})
        tsi_df['university'] = 'TSI'
        tsi_df['programme']  = 'Computer Science'
        tsi_df['faculty']    = 'TSI'
        if 'level' not in tsi_df.columns:
            tsi_df['level'] = 'Mixed'
        print(f"TSI courses loaded: {len(tsi_df)}")
    else:
        print(f"WARNING: {tsi_path} not found")
        tsi_df = pd.DataFrame()

    # ── Load RTU ───────────────────────────────────────────────────
    if os.path.exists(rtu_path):
        rtu_df = pd.read_csv(rtu_path)
        if 'level' not in rtu_df.columns:
            rtu_df['level'] = 'Mixed'
        print(f"RTU courses loaded: {len(rtu_df)}")
    else:
        print(f"WARNING: {rtu_path} not found")
        rtu_df = pd.DataFrame()

    # ── Combine ────────────────────────────────────────────────────
    frames = [df for df in [tsi_df, rtu_df] if not df.empty]
    if not frames:
        print("ERROR: No course data found.")
        return

    courses_df = pd.concat(frames, ignore_index=True)
    courses_df = build_course_text(courses_df)

    print(f"Total courses: {len(courses_df)} "
          f"({courses_df['university'].value_counts().to_dict()})")

    # Quick check on text quality
    print("\nSample match_text per university:")
    for uni in courses_df['university'].unique():
        sample = courses_df[courses_df['university']==uni]['match_text'].iloc[0]
        print(f"  [{uni}] {sample[:120]}...")

    # ── Load demand data ───────────────────────────────────────────
    demand_df = pd.read_csv(demand_path)
    skip_cats = {'Languages', 'Certifications'}
    if 'skill_category' in demand_df.columns:
        demand_df = demand_df[~demand_df['skill_category'].isin(skip_cats)]
    skills = demand_df['skill'].tolist()
    print(f"\nSkills to map: {len(skills)}")

    # ── Layer 1: Keyword matching ──────────────────────────────────
    print("\nLayer 1: Keyword matching...")
    kw_matches = keyword_matching(courses_df, skills)
    print(f"  Keyword matches: {len(kw_matches)}")
    if not kw_matches.empty:
        print(kw_matches.groupby('university')['skill'].count().to_string())

    # ── Layer 2: TF-IDF matching ───────────────────────────────────
    print("Layer 2: TF-IDF semantic matching...")
    tfidf_matches = tfidf_matching(courses_df.reset_index(drop=True),
                                   skills, threshold=0.15)
    print(f"  TF-IDF matches: {len(tfidf_matches)}")
    if not tfidf_matches.empty:
        print(tfidf_matches.groupby('university')['skill'].count().to_string())

    # ── Merge ──────────────────────────────────────────────────────
    print("Merging and deduplicating...")
    all_matches = merge_matches(kw_matches, tfidf_matches)
    print(f"  Final unique matches: {len(all_matches)}")
    if not all_matches.empty:
        print(all_matches.groupby('university')['skill'].count().to_string())

    # ── Skill coverage ─────────────────────────────────────────────
    coverage_df = build_skill_coverage(all_matches, skills, demand_df)

    # ── Save ───────────────────────────────────────────────────────
    os.makedirs('data/processed', exist_ok=True)
    all_matches.to_csv('data/processed/course_skill_matches.csv', index=False)
    coverage_df.to_csv('data/processed/skill_coverage.csv', index=False)
    print(f"\nSaved → data/processed/course_skill_matches.csv")
    print(f"Saved → data/processed/skill_coverage.csv")

    # ── Print results ──────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("SKILL COVERAGE SUMMARY")
    print("=" * 65)
    print(coverage_df['coverage_status'].value_counts().to_string())

    print("\n" + "=" * 65)
    print("HIGH DEMAND SKILLS — COVERAGE STATUS")
    print("=" * 65)
    high = coverage_df[coverage_df['demand_tier'] == 'High Demand']
    cols = ['rank','skill','frequency','total_courses','tsi_courses','rtu_courses','coverage_status']
    print(high[cols].head(30).to_string(index=False))

    print("\n" + "=" * 65)
    print("CRITICAL GAPS — High Demand Skills NOT Covered")
    print("=" * 65)
    gaps = coverage_df[
        (coverage_df['coverage_status'] == 'GAP — Not Covered') &
        (coverage_df['demand_tier'] == 'High Demand')
    ]
    print(gaps[['skill','frequency','job_coverage_pct']].to_string(index=False))

    print("\n" + "=" * 65)
    print("TOP COURSES BY SKILL COVERAGE")
    print("=" * 65)
    top_courses = (
        all_matches.groupby(['university','course_name'])['skill']
        .count()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    top_courses.columns = ['university','course_name','skills_covered']
    print(top_courses.to_string(index=False))


if __name__ == "__main__":
    main()