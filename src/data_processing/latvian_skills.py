"""
Latvian Skill Keyword Expansion
Covers SS.lv (Latvian) and Russian job descriptions.
Mapped to (English skill name, category) tuples.

Strategy:
- Latvian job descriptions use declined forms — we match stems/roots
- Russian job descriptions also included (SS.lv has both)
- Each entry maps to the same English canonical skill used in SKILL_DICTIONARY
"""

# ── LATVIAN KEYWORDS → (English skill, Category) ─────────────────────────────
# Format: "latvian_term": ("Canonical English Skill", "Category")
# Terms are lowercase; matching is done on normalized lowercase text

LATVIAN_SKILL_MAP = {

    # ── Programming Languages ─────────────────────────────────────────────────
    "python":               ("Python", "Programming Languages"),
    "java ":                ("Java", "Programming Languages"),  # space prevents "javascript"
    "javascript":           ("JavaScript", "Programming Languages"),
    "typescript":           ("TypeScript", "Programming Languages"),
    "php":                  ("PHP", "Programming Languages"),
    "golang":               ("Golang", "Programming Languages"),
    "programmēšana":        ("Software development", "Software Engineering"),
    "programmētājs":        ("Software development", "Software Engineering"),
    "izstrādātājs":         ("Software development", "Software Engineering"),
    "programmatūras":       ("Software development", "Software Engineering"),
    # "koda" removed — too broad, matches non-skill Latvian words

    # ── Web Development ───────────────────────────────────────────────────────
    "mājaslapa":            ("Web development", "Web Development"),
    "mājaslapu":            ("Web development", "Web Development"),
    "tīmekļa":              ("Web development", "Web Development"),
    "wordpress":            ("Web development", "Web Development"),
    "html":                 ("HTML", "Web Development"),
    "css":                  ("CSS", "Web Development"),
    "react":                ("React", "Web Development"),
    "angular":              ("Angular", "Web Development"),

    # ── Databases ─────────────────────────────────────────────────────────────
    "datu bāze":            ("SQL", "Databases"),
    "datu bāzēs":           ("SQL", "Databases"),
    "datu bāžu":            ("SQL", "Databases"),
    "sql":                  ("SQL", "Databases"),
    "mysql":                ("MySQL", "Databases"),
    "postgresql":           ("PostgreSQL", "Databases"),
    "mongodb":              ("MongoDB", "Databases"),

    # ── Cloud & DevOps ────────────────────────────────────────────────────────
    "mākoņdatošana":        ("Cloud & DevOps", "Cloud & DevOps"),
    "mākoņ":                ("Cloud & DevOps", "Cloud & DevOps"),
    "docker":               ("Docker", "Cloud & DevOps"),
    "kubernetes":           ("Kubernetes", "Cloud & DevOps"),
    "linux":                ("Linux", "Cloud & DevOps"),
    "aws":                  ("AWS", "Cloud & DevOps"),
    "azure":                ("Azure", "Cloud & DevOps"),
    "devops":               ("DevOps", "Cloud & DevOps"),
    "ci/cd":                ("CI/CD", "Cloud & DevOps"),
    # git itself handled by English keyword matching with word boundaries
    "github":               ("Git", "Software Engineering"),
    "gitlab":               ("Git", "Software Engineering"),

    # ── Data Science & AI ─────────────────────────────────────────────────────
    "datu analīze":         ("Data analysis", "Data Science & AI"),
    "datu analīzē":         ("Data analysis", "Data Science & AI"),
    "datu analīzi":         ("Data analysis", "Data Science & AI"),
    "datu zinātne":         ("Data science", "Data Science & AI"),
    "mašīnmācīšanās":       ("Machine learning", "Data Science & AI"),
    "mākslīgais intelekts": ("Machine learning", "Data Science & AI"),
    "mākslīgā intelekta":   ("Machine learning", "Data Science & AI"),
    "mākslīgā intelekts":   ("Machine learning", "Data Science & AI"),
    "power bi":             ("Power BI", "Data Science & AI"),
    "datu vizualizācija":   ("Data visualization", "Data Science & AI"),
    "statistika":           ("Statistics", "Data Science & AI"),
    "statistiskā":          ("Statistics", "Data Science & AI"),
    "prognoze":             ("Forecasting", "Business & Finance"),
    "prognozēšana":         ("Forecasting", "Business & Finance"),

    # ── Software Engineering ──────────────────────────────────────────────────
    "agile":                ("Agile", "Software Engineering"),
    "scrum":                ("Scrum", "Software Engineering"),
    "jira":                 ("JIRA", "Software Engineering"),
    "testēšana":            ("Unit testing", "Software Engineering"),
    "programmatūras testēšana": ("Unit testing", "Software Engineering"),
    "koda pārskatīšana":    ("Code review", "Software Engineering"),
    "versiju kontrole":     ("Version control", "Software Engineering"),

    # ── Project Management ────────────────────────────────────────────────────
    "projektu vadība":      ("Project management", "Project Management"),
    "projektu vadīšana":    ("Project management", "Project Management"),
    "projektu vadītājs":    ("Project management", "Project Management"),
    "projektu vadītāja":    ("Project management", "Project Management"),
    "projekta vadība":      ("Project management", "Project Management"),
    "projektu koordinācija":("Project management", "Project Management"),
    "risku vadība":         ("Risk management", "Project Management"),
    "risku pārvaldība":     ("Risk management", "Project Management"),
    "ieinteresēto pušu":    ("Stakeholder management", "Project Management"),
    "budžeta plānošana":    ("Budgeting", "Business & Finance"),
    "budžeta vadība":       ("Budgeting", "Business & Finance"),
    "budžeta pārvaldība":   ("Budgeting", "Business & Finance"),

    # ── SS.lv common job description patterns (high coverage recovery) ────────
    # These appear in requirements sections, not company descriptions
    "datorprasmes":         ("Excel", "Business & Finance"),          # Computer skills → implies Office
    "ms word":              ("Microsoft Word", "Business & Finance"),
    "ms outlook":           ("Microsoft Office", "Business & Finance"),
    "microsoft office":     ("Microsoft Office", "Business & Finance"),
    "biroja programmas":    ("Microsoft Office", "Business & Finance"),  # Office programs
    "datora prasmes":       ("Excel", "Business & Finance"),
    "datorprogrammas":      ("Software development", "Software Engineering"),  # computer programs
    "lietotāja līmenī":     ("Microsoft Office", "Business & Finance"),  # user level (implies office)
    "tehniskās prasmes":    ("Technical support", "IT Administration"),
    "tehniskās zināšanas":  ("Technical support", "IT Administration"),
    "tehniskā izglītība":   ("Civil engineering", "Engineering"),
    "inženiertehniskā":     ("Civil engineering", "Engineering"),
    "inženieru":            ("Civil engineering", "Engineering"),
    "elektroinstalācijas":  ("Electrical engineering", "Engineering"),
    "elektrisko":           ("Electrical engineering", "Engineering"),
    "mehānisko":            ("Mechanical engineering", "Engineering"),
    "mehāniskā":            ("Mechanical engineering", "Engineering"),
    "autovadītāja apliecība": ("Driving License", "Certifications"),   # Driver's license
    "b kategorija":         ("Driving License", "Certifications"),     # Category B license
    "vadītāja apliecība":   ("Driving License", "Certifications"),
    "ce kategorija":        ("Driving License", "Certifications"),     # Truck license
    "finansu":              ("Financial analysis", "Business & Finance"),  # Finance (alt spelling)
    "finanšu":              ("Financial analysis", "Business & Finance"),
    "juridisku":            ("Compliance", "Business & Finance"),
    "juridiskās zināšanas": ("Compliance", "Business & Finance"),
    "personāla vadība":     ("Leadership", "Professional Skills"),
    "personāla vadītājs":   ("Leadership", "Professional Skills"),
    "komandas vadība":      ("Leadership", "Professional Skills"),
    "komandas vadītājs":    ("Leadership", "Professional Skills"),
    "darba tiesības":       ("Compliance", "Business & Finance"),
    "darba likums":         ("Compliance", "Business & Finance"),
    "lietvedība":           ("Reporting", "Business & Finance"),       # Records management
    "dokumentu pārvaldība": ("Reporting", "Business & Finance"),
    "dokumentu vadība":     ("Reporting", "Business & Finance"),
    "preču uzskaite":       ("Inventory management", "Logistics & Supply Chain"),
    "krājumu":              ("Inventory management", "Logistics & Supply Chain"),
    "krājumu vadība":       ("Inventory management", "Logistics & Supply Chain"),
    "klientu apkalpošana":  ("Customer service", "Professional Skills"),
    "klientu apkalpošanu":  ("Customer service", "Professional Skills"),
    "klientu serviss":      ("Customer service", "Professional Skills"),
    "klientu piesaiste":    ("Customer service", "Professional Skills"),
    "klientu attiecības":   ("Customer service", "Professional Skills"),
    "pārdošanas pieredze":  ("Customer service", "Professional Skills"),  # Sales experience
    "pārdošanas prasmes":   ("Customer service", "Professional Skills"),  # Sales skills
    "aktīvā pārdošana":     ("Customer service", "Professional Skills"),  # Active sales
    "tirdzniecības pārstāvis": ("Customer service", "Professional Skills"), # Sales rep
    "celtniecības projekts": ("Civil engineering", "Engineering"),     # Construction project
    "būvprojekts":          ("Civil engineering", "Engineering"),
    "būvniecības vadība":   ("Civil engineering", "Engineering"),      # Construction management
    "inženierprojekti":     ("Civil engineering", "Engineering"),
    "inženiertīkli":        ("Civil engineering", "Engineering"),      # Engineering networks
    "konstrukciju":         ("Civil engineering", "Engineering"),      # Structural
    "siltumapgādes sistēma":("Civil engineering", "Engineering"),
    "ventilācijas sistēma": ("Civil engineering", "Engineering"),
    "elektroinstalācijas darbi": ("Electrical engineering", "Engineering"),

    # ── Business & Finance ────────────────────────────────────────────────────
    "grāmatvedība":         ("Accounting", "Business & Finance"),
    "grāmatvedis":          ("Accounting", "Business & Finance"),
    "grāmatvede":           ("Accounting", "Business & Finance"),
    "grāmatveža":           ("Accounting", "Business & Finance"),
    "grāmatvedības":        ("Accounting", "Business & Finance"),
    "finanšu analīze":      ("Financial analysis", "Business & Finance"),
    "finanšu analīzi":      ("Financial analysis", "Business & Finance"),
    "finanšu pārskati":     ("Financial reporting", "Business & Finance"),
    "finanšu pārskata":     ("Financial reporting", "Business & Finance"),
    "finanšu pārskatu":     ("Financial reporting", "Business & Finance"),
    "nodokļu uzskaite":     ("Tax", "Business & Finance"),        # Specific: tax accounting
    "nodokļu deklarācija":  ("Tax", "Business & Finance"),        # Specific: tax return
    "nodokļu aprēķins":     ("Tax", "Business & Finance"),        # Specific: tax calculation
    "nodokļu konsultants":  ("Tax", "Business & Finance"),        # Specific: tax consultant
    "algas aprēķins":       ("Payroll", "Business & Finance"),    # Specific: payroll calculation
    "algu aprēķināšana":    ("Payroll", "Business & Finance"),    # Specific: payroll processing
    "atbilstība":           ("Compliance", "Business & Finance"),
    "atbilstības":          ("Compliance", "Business & Finance"),
    "iekšējā audita":       ("Internal audit", "Business & Finance"),
    "iekšējais audits":     ("Internal audit", "Business & Finance"),
    "excel":                ("Excel", "Business & Finance"),
    "ms excel":             ("Excel", "Business & Finance"),
    "1c":                   ("1C", "Business & Finance"),
    "erp":                  ("ERP", "Business & Finance"),
    "sap sistēma":          ("SAP", "Business & Finance"),        # Specific: SAP system
    "sap programma":        ("SAP", "Business & Finance"),        # Specific: SAP program
    "sap zināšanas":        ("SAP", "Business & Finance"),        # SAP knowledge
    "sap pieredze":         ("SAP", "Business & Finance"),        # SAP experience
    "kpi":                  ("KPI", "Business & Finance"),
    "pārskatu sagatavošana":("Reporting", "Business & Finance"),
    "uzskaite":             ("Accounting", "Business & Finance"),
    "finanšu uzskaite":     ("Accounting", "Business & Finance"),
    "ekonomiskā analīze":   ("Financial analysis", "Business & Finance"),
    "iepirkumu":            ("Procurement", "Business & Finance"),
    "iepirkumi":            ("Procurement", "Business & Finance"),
    "līgumu slēgšana":      ("Contract management", "Business & Finance"),
    "līgumu pārvaldība":    ("Contract management", "Business & Finance"),
    "biznesa analīze":      ("Business analysis", "Business & Finance"),
    "biznesa analītiķis":   ("Business analysis", "Business & Finance"),

    # ── Logistics & Supply Chain ──────────────────────────────────────────────
    "loģistika":            ("Supply chain", "Logistics & Supply Chain"),
    "loģistikas":           ("Supply chain", "Logistics & Supply Chain"),
    "loģistiķis":           ("Supply chain", "Logistics & Supply Chain"),
    "noliktava":            ("Warehouse management", "Logistics & Supply Chain"),
    "noliktavas":           ("Warehouse management", "Logistics & Supply Chain"),
    "noliktavas vadība":    ("Warehouse management", "Logistics & Supply Chain"),
    "noliktavas pārvaldība":("Warehouse management", "Logistics & Supply Chain"),
    "piegādes ķēde":        ("Supply chain", "Logistics & Supply Chain"),
    "piegādes ķēdes":       ("Supply chain", "Logistics & Supply Chain"),
    "kravas pārvadājumi":   ("Freight", "Logistics & Supply Chain"),   # Specific: freight transport
    "kravas ekspedīcija":   ("Freight", "Logistics & Supply Chain"),   # Specific: freight forwarding
    "transporta vadība":    ("Supply chain", "Logistics & Supply Chain"),
    "muita":                ("Customs", "Logistics & Supply Chain"),
    "muitas":               ("Customs", "Logistics & Supply Chain"),
    "inventāra vadība":     ("Inventory management", "Logistics & Supply Chain"),
    "inventāra pārvaldība": ("Inventory management", "Logistics & Supply Chain"),

    # ── Engineering ───────────────────────────────────────────────────────────
    "autocad":              ("AutoCAD", "Engineering"),
    "autocad":              ("AutoCAD", "Engineering"),
    "revit":                ("Revit", "Engineering"),
    "bim":                  ("BIM", "Engineering"),
    "elektriķis":           ("Electrical engineering", "Engineering"),
    "elektromontieris":     ("Electrical engineering", "Engineering"),
    "elektromehāniķis":     ("Electrical engineering", "Engineering"),
    "elektromontāža":       ("Electrical engineering", "Engineering"),
    "elektroinstalāciju":   ("Electrical engineering", "Engineering"),
    "elektroapgādes":       ("Electrical engineering", "Engineering"),
    "elektrokabeļu":        ("Electrical engineering", "Engineering"),
    "elektroiekārtu":       ("Electrical engineering", "Engineering"),
    "elektroinstalācija":   ("Electrical engineering", "Engineering"),
    "elektronikas":         ("Electronics", "Engineering"),
    "elektronika":          ("Electronics", "Engineering"),
    "vājstrāvas":           ("Electronics", "Engineering"),
    "telekomunikāciju":     ("Network administration", "Networking & Security"),
    "datortehniķis":        ("Troubleshooting", "IT Administration"),
    "datora speciālistu":   ("Troubleshooting", "IT Administration"),
    "datorprogrammās":      ("Software development", "Software Engineering"),
    "mehānikas":            ("Mechanical engineering", "Engineering"),
    "mehāniķis":            ("Mechanical engineering", "Engineering"),
    "metālapstrādes":       ("Mechanical engineering", "Engineering"),
    "kuģu":                 ("Mechanical engineering", "Engineering"),
    "gāzes apkures":        ("Civil engineering", "Engineering"),
    "inženierprojekti":     ("Civil engineering", "Engineering"),
    "inženiertīkli":        ("Civil engineering", "Engineering"),
    "konstruktors":         ("Technical drawing", "Engineering"),
    "mēbeļu inženier":      ("Technical drawing", "Engineering"),
    "šūšanas izstrādājumu": ("Technical drawing", "Engineering"),
    "projektēšana":         ("Technical drawing", "Engineering"),
    "rasējumi":             ("Technical drawing", "Engineering"),
    "rasējumu":             ("Technical drawing", "Engineering"),
    "iot":                  ("IoT", "Engineering"),
    "plc":                  ("PLC programming", "Engineering"),
    "automatizācija":       ("Industrial automation", "Engineering"),
    "ražošanas iekārtu":    ("Industrial automation", "Engineering"),
    "automātiskās":         ("Industrial automation", "Engineering"),

    # ── Networking & Security ─────────────────────────────────────────────────
    "kiberdrošība":         ("Cybersecurity", "Networking & Security"),
    "kiberdrošību":         ("Cybersecurity", "Networking & Security"),
    "informācijas drošība": ("Information security", "Networking & Security"),
    "informācijas drošību": ("Information security", "Networking & Security"),
    "tīkla administrēšana": ("Network administration", "Networking & Security"),
    "tīklu administrēšana": ("Network administration", "Networking & Security"),
    "vpn":                  ("VPN", "Networking & Security"),
    "ugunsmūris":           ("Firewall", "Networking & Security"),

    # ── IT Administration ─────────────────────────────────────────────────────
    "it atbalsts":          ("IT support", "IT Administration"),
    "tehniskais atbalsts":  ("Technical support", "IT Administration"),
    "it infrastruktūra":    ("IT infrastructure", "IT Administration"),
    "sistēmas administrators": ("IT Administration", "IT Administration"),
    "sistēmu administrēšana": ("IT Administration", "IT Administration"),
    "microsoft 365":        ("Microsoft 365", "IT Administration"),
    "office 365":           ("Office 365", "IT Administration"),
    "vmware":               ("VMware", "IT Administration"),
    "hyper-v":              ("Hyper-V", "IT Administration"),
    "active directory":     ("Active Directory", "IT Administration"),
    "traucējummeklēšana":   ("Troubleshooting", "IT Administration"),

    # ── Design & Creative ─────────────────────────────────────────────────────
    "dizains":              ("Graphic design", "Design & Creative"),
    "grafiskais dizains":   ("Graphic design", "Design & Creative"),
    "lietotāja saskarne":   ("UI/UX", "Design & Creative"),
    "lietotāja pieredze":   ("UI/UX", "Design & Creative"),
    "lietotāja pieredzes":  ("UI/UX", "Design & Creative"),
    "figma":                ("Figma", "Design & Creative"),
    "photoshop":            ("Photoshop", "Design & Creative"),
    "illustrator":          ("Illustrator", "Design & Creative"),
    "video montāža":        ("Video editing", "Design & Creative"),
    "video rediģēšana":     ("Video editing", "Design & Creative"),
    "ux":                   ("UX design", "Design & Creative"),

    # ── Marketing & Communication ─────────────────────────────────────────────
    "mārketings":           ("Digital marketing", "Marketing & Communication"),
    "mārketinga":           ("Digital marketing", "Marketing & Communication"),
    "digitālais mārketings":("Digital marketing", "Marketing & Communication"),
    "sociālie mediji":      ("Social media marketing", "Marketing & Communication"),
    "sociālo mediju":       ("Social media marketing", "Marketing & Communication"),
    "seo":                  ("SEO", "Marketing & Communication"),
    "crm":                  ("CRM", "Marketing & Communication"),
    "satura veidošana":     ("Content creation", "Marketing & Communication"),
    "copywriting":          ("Copywriting", "Marketing & Communication"),
    "google analytics":     ("Google Analytics", "Marketing & Communication"),
    "e-pasta mārketings":   ("Email marketing", "Marketing & Communication"),

    # ── Professional Skills ───────────────────────────────────────────────────
    "komunikācijas prasmes":("Communication skills", "Professional Skills"),
    "komunikāciju prasmes": ("Communication skills", "Professional Skills"),
    "komandas darbs":       ("Teamwork", "Professional Skills"),
    "komandas spēlētājs":   ("Teamwork", "Professional Skills"),
    "darbs komandā":        ("Teamwork", "Professional Skills"),
    "spēja strādāt komandā":("Teamwork", "Professional Skills"),
    "vadības prasmes":      ("Leadership", "Professional Skills"),
    "līderības prasmes":    ("Leadership", "Professional Skills"),
    "problēmu risināšana":  ("Problem solving", "Professional Skills"),
    "problēmu risināšanu":  ("Problem solving", "Professional Skills"),
    "klientu apkalpošana":  ("Customer service", "Professional Skills"),
    "klientu apkalpošanu":  ("Customer service", "Professional Skills"),
    "klientu serviss":      ("Customer service", "Professional Skills"),
    "prezentācijas prasmes":("Presentation skills", "Professional Skills"),
    "laika plānošana":      ("Time management", "Professional Skills"),
    "uzmanība detaļām":     ("Attention to detail", "Professional Skills"),
    "precizitāte un":       ("Attention to detail", "Professional Skills"),
    "sarunu prasmes":       ("Negotiation", "Professional Skills"),
    "analītiskā domāšana":  ("Analytical thinking", "Professional Skills"),

    # ── Languages ─────────────────────────────────────────────────────────────
    "angļu valoda":         ("English", "Languages"),
    "angļu valodas":        ("English", "Languages"),
    "angļu val":            ("English", "Languages"),
    "latviešu valoda":      ("Latvian", "Languages"),
    "latviešu valodas":     ("Latvian", "Languages"),
    "latviešu val":         ("Latvian", "Languages"),
    "krievu valoda":        ("Russian", "Languages"),
    "krievu valodas":       ("Russian", "Languages"),
    "krievu val":           ("Russian", "Languages"),
    "vācu valoda":          ("German", "Languages"),
    "vācu valodas":         ("German", "Languages"),
    "franču valoda":        ("French", "Languages"),
    "spāņu valoda":         ("Spanish", "Languages"),
    "lietuviešu valoda":    ("Lithuanian", "Languages"),
    "igauņu valoda":        ("Estonian", "Languages"),
    "zviedru valoda":       ("Swedish", "Languages"),

    # ── Russian Keywords (SS.lv Russian postings) ─────────────────────────────
    "программирование":     ("Software development", "Software Engineering"),
    "разработчик":          ("Software development", "Software Engineering"),
    "разработка":           ("Software development", "Software Engineering"),
    "бухгалтерия":          ("Accounting", "Business & Finance"),
    "бухгалтер":            ("Accounting", "Business & Finance"),
    "бухгалтерского":       ("Accounting", "Business & Finance"),
    "логистика":            ("Supply chain", "Logistics & Supply Chain"),
    "логистики":            ("Supply chain", "Logistics & Supply Chain"),
    "склад":                ("Warehouse management", "Logistics & Supply Chain"),
    "складской":            ("Warehouse management", "Logistics & Supply Chain"),
    "налог":                ("Tax", "Business & Finance"),
    "налогов":              ("Tax", "Business & Finance"),
    "финансовый анализ":    ("Financial analysis", "Business & Finance"),
    "финансовая отчетность":("Financial reporting", "Business & Finance"),
    "управление проектами": ("Project management", "Project Management"),
    "кибербезопасность":    ("Cybersecurity", "Networking & Security"),
    "маркетинг":            ("Digital marketing", "Marketing & Communication"),
    "клиентский сервис":    ("Customer service", "Professional Skills"),
    "обслуживание клиентов":("Customer service", "Professional Skills"),
    "английский язык":      ("English", "Languages"),
    "латышский язык":       ("Latvian", "Languages"),
    "русский язык":         ("Russian", "Languages"),
    "немецкий язык":        ("German", "Languages"),
    "проектирование":       ("Technical drawing", "Engineering"),
    "автокад":              ("AutoCAD", "Engineering"),
    "администрирование":    ("IT Administration", "IT Administration"),
    "техническая поддержка":("Technical support", "IT Administration"),
    "анализ данных":        ("Data analysis", "Data Science & AI"),
    "машинное обучение":    ("Machine learning", "Data Science & AI"),
    "база данных":          ("SQL", "Databases"),
    "баз данных":           ("SQL", "Databases"),
}


def get_latvian_skills():
    """Returns list of (lv_term, english_skill, category) tuples"""
    return [(term, skill, cat) for term, (skill, cat) in LATVIAN_SKILL_MAP.items()]