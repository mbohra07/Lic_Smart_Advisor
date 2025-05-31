"""
Configuration file for LIC Policy Scraper
Contains all constants, URLs, and settings for the scraping process
"""

import os
from datetime import datetime

# Base configuration
BASE_URL = "https://licindia.in"
OUTPUT_DIR = "LIC_Policies_Complete_Data"
LOG_DIR = "logs"

# Request settings
REQUEST_DELAY = 2  # seconds between requests
RETRY_ATTEMPTS = 3
TIMEOUT = 30

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# LIC Policy Categories and their URLs (simplified for scraper compatibility)
POLICY_CATEGORIES = {
    "Insurance_Plans": "https://licindia.in/web/guest/insurance-plan",
    "Pension_Plans": "https://licindia.in/web/guest/pension-plan",
    "Unit_Linked_Plans": "https://licindia.in/web/guest/unit-linked-plans",
    "Micro_Insurance_Plans": "https://licindia.in/web/guest/micro-insurance-plans"
}

# Detailed category structure for reference
POLICY_CATEGORIES_DETAILED = {
    "Insurance_Plans": {
        "url": "/web/guest/insurance-plan",
        "subcategories": {
            "Endowment_Plans": "/web/guest/endowment-plans",
            "Whole_Life_Plans": "/web/guest/whole-life-plans",
            "Money_Back_Plans": "/web/guest/money-back-plans",
            "Term_Assurance_Plans": "/web/guest/term-assurance-plans",
            "Riders": "/web/guest/riders"
        }
    },
    "Pension_Plans": {
        "url": "/web/guest/pension-plan",
        "subcategories": {}
    },
    "Unit_Linked_Plans": {
        "url": "/web/guest/unit-linked-plans",
        "subcategories": {}
    },
    "Micro_Insurance_Plans": {
        "url": "/web/guest/micro-insurance-plans",
        "subcategories": {}
    }
}

# Expected policy counts for validation
EXPECTED_COUNTS = {
    "Insurance_Plans": 29,
    "Pension_Plans": 5,
    "Unit_Linked_Plans": 4,
    "Micro_Insurance_Plans": 1
}

# Data fields to extract for each policy
POLICY_FIELDS = [
    'policy_name',
    'plan_number',
    'uin_number',
    'category',
    'subcategory',
    'features_benefits',
    'eligibility_criteria',
    'premium_payment_options',
    'maturity_benefits',
    'surrender_values',
    'tax_benefits',
    'terms_conditions',
    'policy_documents',
    'riders_available',
    'source_url',
    'scraped_timestamp'
]

# File formats for output (optimized for vector database)
OUTPUT_FORMATS = ['csv', 'pdf']  # Primary: CSV for vector DB, Secondary: PDF for reports

# Selenium settings
SELENIUM_SETTINGS = {
    'headless': True,
    'window_size': (1920, 1080),
    'page_load_timeout': 30,
    'implicit_wait': 10
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': f'{LOG_DIR}/lic_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
}

# Create necessary directories
def create_directories():
    """Create necessary directories for the project"""
    directories = [
        OUTPUT_DIR,
        LOG_DIR,
        f"{OUTPUT_DIR}/Insurance_Plans",
        f"{OUTPUT_DIR}/Pension_Plans", 
        f"{OUTPUT_DIR}/Unit_Linked_Plans",
        f"{OUTPUT_DIR}/Micro_Insurance_Plans",
        f"{OUTPUT_DIR}/Reports",
        f"{OUTPUT_DIR}/Master_Index"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    print("Directory structure created successfully!")
