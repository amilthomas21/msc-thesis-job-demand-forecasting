"""
ESCO-Aligned Skill Keyword Dictionary v3 — FINAL
Validated through diagnostic analysis of actual job descriptions.

Key changes from v2:
- REMOVED "Go" — severe false positive in Latvian text (2033 spurious matches)
- REMOVED "BI" — severe false positive in Latvian text (2458 spurious matches)
  Replaced with full terms: "Business Intelligence", "Power BI"
- REMOVED standalone "CAD" — matches "Cadence" company name
  Kept "AutoCAD" which is specific
- REMOVED standalone "Word" — replaced with "Microsoft Word"  
- REMOVED "DNS" risk: kept but noted as limitation in thesis
- Added "Golang" as the proper way to detect Go language
"""

SKILL_DICTIONARY = {

    # ─── PROGRAMMING LANGUAGES ───────────────────────────────────────────────
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++",
        "Golang",           # Use Golang NOT Go — "Go" is too common in Latvian text
        "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Scala",
        "R programming", "MATLAB", "Perl", "Bash", "Shell scripting",
        "PowerShell", "VBA", "Groovy", "Dart", "Lua", "COBOL",
        "Objective-C", "F#", "Elixir", "Haskell",
    ],

    # ─── WEB DEVELOPMENT ─────────────────────────────────────────────────────
    "Web Development": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Vue",
        "Node.js", "Express.js", "Next.js", "Nuxt.js",
        "Django", "Flask", "FastAPI", "Spring Boot", "Spring",
        "ASP.NET", ".NET", "Laravel", "Symfony", "Ruby on Rails",
        "jQuery", "Bootstrap", "Tailwind CSS", "SASS", "SCSS",
        "Webpack", "Vite", "REST API", "RESTful", "GraphQL",
        "WebSocket", "OAuth", "JWT", "SOAP", "XML", "JSON",
        "Responsive design", "Web accessibility", "PWA",
    ],

    # ─── DATABASES ───────────────────────────────────────────────────────────
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "Microsoft SQL Server", "MSSQL",
        "Oracle Database", "Oracle", "SQLite", "MariaDB", "MongoDB",
        "Redis", "Cassandra", "Elasticsearch", "DynamoDB", "Firebase",
        "Neo4j", "InfluxDB", "Snowflake", "BigQuery", "Redshift",
        "NoSQL", "Database design", "Database administration",
        "Data modeling", "ETL", "Data warehousing",
        "Stored procedures", "Query optimization", "PL/SQL", "T-SQL",
    ],

    # ─── CLOUD & DEVOPS ───────────────────────────────────────────────────────
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure",
        "Google Cloud", "GCP", "Docker", "Kubernetes", "Terraform",
        "Ansible", "Jenkins", "CI/CD", "GitLab CI", "GitHub Actions",
        "CircleCI", "Helm", "ArgoCD", "Prometheus",
        "Grafana", "ELK Stack", "Logstash", "Kibana",
        "Linux", "Ubuntu", "CentOS", "Unix", "Nginx", "Apache",
        "Load balancing", "Microservices", "Serverless",
        "Infrastructure as code", "SRE", "DevOps",
        "CloudFormation", "Pulumi",
    ],

    # ─── DATA SCIENCE & AI ───────────────────────────────────────────────────
    "Data Science & AI": [
        "Machine learning", "Deep learning", "Neural networks",
        "Natural language processing", "NLP", "Computer vision",
        "Data science", "Data analysis", "Data analytics",
        "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Jupyter",
        "Statistical analysis", "Statistics", "Predictive modeling",
        "Feature engineering", "A/B testing",
        "Regression", "Classification", "Clustering",
        "Generative AI", "LLM", "Hugging Face", "BERT",
        "Data visualization",
        "Business Intelligence",    # Full term instead of "BI"
        "Power BI",                 # Specific tool
        "Tableau", "Looker", "Qlik",
        "Apache Spark", "Hadoop", "PySpark", "Databricks", "Airflow",
        "MLOps", "Data pipeline", "Data engineering",
    ],

    # ─── SOFTWARE ENGINEERING ─────────────────────────────────────────────────
    "Software Engineering": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Version control",
        "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "Trello",
        "Software architecture", "Design patterns", "SOLID principles",
        "Object-oriented programming", "OOP", "Functional programming",
        "Unit testing", "Integration testing", "Test-driven development",
        "TDD", "Selenium", "JUnit", "pytest", "Mocha",
        "Code review", "Refactoring", "Debugging", "API development",
        "Microservices architecture", "Event-driven",
        "RabbitMQ", "Kafka", "gRPC", "Message queues",
    ],

    # ─── NETWORKING & SECURITY ────────────────────────────────────────────────
    "Networking & Security": [
        "Cybersecurity", "Information security", "Network security",
        "Penetration testing", "Ethical hacking", "Vulnerability assessment",
        "Firewall", "VPN", "TCP/IP",
        "DNS",          # Kept - mostly legitimate, minor false positive risk noted
        "DHCP",
        "Network administration", "Cisco", "Juniper", "CCNA",
        "CISSP", "CEH", "ISO 27001", "GDPR compliance",
        "Identity management", "Active Directory", "LDAP", "SSO",
        "Encryption", "PKI", "Zero trust", "SOC", "SIEM",
    ],

    # ─── IT ADMINISTRATION ───────────────────────────────────────────────────
    "IT Administration": [
        "Windows Server", "Active Directory", "Office 365", "Microsoft 365",
        "IT support", "Help desk", "ITIL", "ServiceNow",
        "IT infrastructure", "Virtualization", "VMware", "Hyper-V",
        "Backup and recovery", "Disaster recovery", "System monitoring",
        "Troubleshooting", "Technical support",
    ],

    # ─── PROJECT MANAGEMENT ───────────────────────────────────────────────────
    "Project Management": [
        "Project management", "PMP", "Prince2", "Program management",
        "Stakeholder management", "Risk management", "Budget management",
        "Resource planning", "Change management", "Delivery management",
        "Sprint planning", "Roadmap planning", "MS Project",
    ],

    # ─── BUSINESS & FINANCE ───────────────────────────────────────────────────
    "Business & Finance": [
        "Accounting", "Financial analysis", "Financial reporting",
        "Budgeting", "Forecasting", "Auditing", "Tax", "Payroll",
        "IFRS", "GAAP", "SAP", "SAP FI", "SAP CO", "SAP MM",
        "ERP", "Microsoft Dynamics", "Oracle ERP", "1C",
        "Business analysis", "Requirements gathering", "Process improvement",
        "BPMN", "KPI", "Reporting",
        "Excel", "Microsoft Office", "PowerPoint",
        "Microsoft Word",       # Full term instead of "Word"
        "Cost analysis", "Procurement", "Contract management",
        "Compliance", "Internal audit", "Controlling",
    ],

    # ─── LOGISTICS & SUPPLY CHAIN ─────────────────────────────────────────────
    "Logistics & Supply Chain": [
        "Supply chain management", "Supply chain", "Logistics management",
        "Warehouse management", "Inventory management",
        "Import/export", "Customs", "Incoterms", "Freight",
        "Transportation management", "Demand planning",
        "Lean", "Six Sigma", "Kaizen",
        "SAP WM", "SAP EWM", "WMS", "TMS",
    ],

    # ─── ENGINEERING ──────────────────────────────────────────────────────────
    "Engineering": [
        "AutoCAD",              # Keep specific tool, removed generic "CAD"
        "SolidWorks", "CATIA", "Revit", "BIM",
        "Electrical engineering", "Mechanical engineering",
        "Civil engineering", "Structural engineering",
        "PLC programming", "SCADA", "Industrial automation",
        "Embedded systems", "IoT", "Electronics", "Circuit design",
        "PCB design", "CAM", "FEA", "CFD",
        "Technical drawing",
    ],

    # ─── DESIGN & CREATIVE ────────────────────────────────────────────────────
    "Design & Creative": [
        "UI design", "UX design", "UI/UX", "Figma", "Adobe XD",
        "Sketch", "InVision", "Prototyping", "Wireframing",
        "User research", "Usability testing", "Design thinking",
        "Photoshop", "Illustrator", "InDesign", "After Effects",
        "Premiere Pro", "Graphic design", "Motion graphics",
        "Video editing", "3D modeling", "Blender", "Maya",
        "Web design", "Visual design",
    ],

    # ─── MARKETING & COMMUNICATION ────────────────────────────────────────────
    "Marketing & Communication": [
        "Digital marketing", "SEO", "SEM", "Google Ads", "Facebook Ads",
        "Social media marketing", "Content marketing", "Email marketing",
        "Marketing automation", "HubSpot", "Salesforce", "CRM",
        "Google Analytics", "Market research", "Brand management",
        "Copywriting", "Content creation", "Public relations",
    ],

    # ─── PROFESSIONAL SKILLS ──────────────────────────────────────────────────
    "Professional Skills": [
        "Communication skills", "Presentation skills",
        "Teamwork", "Leadership", "Problem solving",
        "Critical thinking", "Analytical thinking", "Attention to detail",
        "Time management", "Customer service", "Customer relations",
        "Negotiation", "Decision making",
    ],

    # ─── LANGUAGES ────────────────────────────────────────────────────────────
    "Languages": [
        "English", "Latvian", "Russian", "German", "French",
        "Lithuanian", "Estonian", "Swedish", "Norwegian", "Finnish",
        "Polish", "Czech", "Ukrainian", "Chinese", "Spanish",
        "Italian", "Dutch", "Portuguese",
    ],

    # ─── CERTIFICATIONS ───────────────────────────────────────────────────────
    "Certifications": [
        "AWS Certified", "Azure Certified", "Google Certified",
        "CISSP", "CISM", "CISA", "CEH", "CompTIA",
        "PMP", "Prince2", "Scrum Master", "Product Owner",
        "ITIL", "CCNA", "CCNP", "Six Sigma", "CPA", "ACCA",
        "CFA", "ISO 9001", "ISO 27001",
    ],
}

# ── FALSE POSITIVES (validated through diagnostic analysis) ───────────────────
FALSE_POSITIVES = {
    # Validated false positives — matched Latvian words NOT English skill terms
    "Go",           # Substring of countless Latvian words (augošā, piedāvājam etc.)
    "BI",           # Substring of countless Latvian words (stabila, bijis etc.)
    "CAD",          # Matches "Cadence" company name

    # Context false positives — appear as company descriptions, not requirements
    "Training",     # "we provide training" not "candidate has training skill"
    "Innovation",   # Company culture description
    "HTTPS",        # URL protocol in scraped HTML
    "HTTP",         # URL protocol
    "Communication",# Too generic — use "Communication skills" instead
    "Driving License",
    "Adaptability",
    "Creativity",
    "Initiative",
    "Mentoring",
    "Coaching",
    "Word",         # Replaced by "Microsoft Word"
    "Logistics",    # Replaced by "Logistics management" to avoid company name matches
}


def get_flat_skills():
    """Returns list of (skill, category) tuples, excluding false positives"""
    flat = []
    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            if skill not in FALSE_POSITIVES:
                flat.append((skill, category))
    return flat


def get_skill_count():
    total = sum(len(v) for v in SKILL_DICTIONARY.values())
    print(f"Total skills in dictionary: {total}")
    print(f"False positives excluded:   {len(FALSE_POSITIVES)}")
    print(f"Net skills for extraction:  {total - len(FALSE_POSITIVES)}")
    print(f"\nCategories ({len(SKILL_DICTIONARY)}):")
    for cat, skills in SKILL_DICTIONARY.items():
        active = [s for s in skills if s not in FALSE_POSITIVES]
        print(f"  {cat}: {len(active)} active skills")


if __name__ == "__main__":
    get_skill_count()