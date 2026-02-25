# taxonomy.py

# --- 1. ROLES & FUNCTIONS MAPPING ---
# We use a Dictionary so we can look up the Function if we know the Role
ROLES_CONFIG = {
    "Chief Technology Officer (CTO)": "Engineering",
    "Chief Information Officer (CIO)": "Engineering",
    "Engineering Manager": "Engineering",
    "Head of Engineering": "Engineering",
    "Head of Platform Engineering": "Engineering",
    "Principal Engineer": "Engineering",
    "VP of Engineering": "Engineering",
    "Chief Marketing Officer (CMO)": "Marketing",
    "Director of Marketing": "Marketing",
    "Head of Marketing": "Marketing",
    "VP of Growth": "Marketing",
    "Lead - Growth": "Marketing",
    "VP of Marketing": "Marketing",
    "VP of Partnerships": "Partnerships",
    "Chief Product Officer (CPO)": "Product",
    "Head of Product": "Product",
    "Product Marketing Manager": "Marketing",
    "Product Manager": "Product",
    "Associate Product Manager": "Product",
    "Senior Product Manager": "Product",
    "VP of Product": "Product",
    "Head of Sales": "Sales",
    "SVP of Sales": "Sales",
    "VP of Sales": "Sales",
    "Chief Financial Officer (CFO)": "Finance",
    "Chief of Staff": "Generalist",
    "Entrepreneur in Residence (EIR)": "Generalist",
    "Founders Office": "Generalist",
    "Business Head / P&L": "Business",
    "Chief Operations Officer (COO)": "Operations",
    "Head of Operations": "Operations",
    "Head of Partnerships": "Partnerships",
    "Head of Customer Success": "Customer Success",
    "Pre-Sales Manager": "Sales",
    "Market Strategist": "Strategy",
    "Chief Evangelist": "Marketing",
    "Delivery Manager": "Engineering",
    "Program Manager": "Generalist",
    "Category Head": "Business",
    "VP of Revenue": "Revenue",
    "VP of Analytics": "Analytics",
    "Senior Manager - Marketing": "Marketing",
    "Performance Marketing Manager": "Marketing",
    "Full stack developer": "Engineering",
    "AI head": "Engineering",
    "Chief Technology & Product Officer (CTPO)": "Product",
    "Community": "Marketing"
}

# Extract just the list of Role Names for the AI to choose from
SUITABLE_ROLES = list(ROLES_CONFIG.keys())

# --- 2. OTHER TAXONOMIES ---

FOUNDER_TYPES = [
    "Brand entrepreneur", "Partnership builder", "Community builder", "Generalist",
    "0-1 specialist", "GTM specialist", "Engineering leader", "Sales leader",
    "Product leader", "Product owner/Manager", "0-1 Product builder",
    "Founding Engineer", "SaaS leader", "Operations Leader", "Growth leader"
]

SENIORITY_LEVELS = ["IC", "Manager/Lead", "Head/Director", "CXO"]

# Defines the specific functional areas (Used for "Functions Overseen")
FUNCTIONS = [
    "Business", "Community", "Customer Success", "Design", "Engineering",
    "Marketing", "Hardware", "HR", "Operations", "Partnerships", "Product",
    "Sales", "Stakeholder Management", "Finance", "Strategy", "Analytics"
]

STARTUP_STAGES = ["0-1", "1-10", "10-100", "100+"]

INDUSTRIES = [
    "Adtech", "Agritech", "Analytics/Data", "AI/ML", "Blockchain/Cryptocurrency",
    "Consumer", "D2C", "DeepTech", "Developer Tools", "Drones", "E-commerce",
    "Education", "Enterprise Software", "Fashion", "Fitness and Wellness", "Fintech",
    "Food and Beverages", "Games", "Healthcare", "HR/Recruiting", "IoT & Hardware",
    "IT Services and Consulting", "Logistics/Transportation/Shipping", "Manufacturing",
    "Marketplaces", "Media", "Mobile", "Mobility", "Online Rental",
    "Professional/Consumer Services", "Productivity Software", "Real-Estate",
    "Renewable/Sustainability", "Retail", "SaaS", "Security", "Social Media",
    "Social Startups (NGOs, Government)", "Space Tech", "Travel/Tourism",
    "Virtual Reality", "Wearables", "Financial/Equities/VentureFunding"
]

SKILLS = [
    "Strategy & Consulting", "Financial Analysis & Modeling", "P&L Ownership",
    "Business Analytics", "Market Research & Sizing", "Data & Analytics",
    "Product Analytics", "Data Science", "Data Engineering", "AI / ML / NLP",
    "Automation & AI Workflows", "Cybersecurity", "Full-Stack Development",
    "Engineering Team Building", "Hardware Experience", "Product Management",
    "Product Building (0–1)", "Product – SaaS", "Community-Led Product",
    "UX / Design Collaboration", "Growth Experimentation (A/B Testing)",
    "Performance Marketing", "Demand Generation", "Funnel Optimization",
    "Content Marketing", "Brand Marketing", "Marketing Automation", "SaaS Marketing",
    "D2C / DTC Marketing", "E-commerce Marketing", "Offline / Field Marketing",
    "GTM Strategy", "SaaS Sales (0–$1M ARR)", "Sales – Enterprise",
    "Sales – Mid-Market", "Sales – SMB", "Sales – Direct", "Sales – Institutional",
    "Business Operations", "Marketplace Operations", "Supply Chain & Logistics",
    "DTC Supply Chain", "Vendor Management", "Process Optimization & Automation",
    "Partnerships", "Brand Partnerships", "Channel Partnerships", "Community Building",
    "Developer Community", "User Community", "Campus / Student Programs",
    "Founder’s Office", "0–1 Builder", "Operator Mindset", "Cross-Functional Leadership"
]