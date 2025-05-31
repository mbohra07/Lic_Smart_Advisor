"""
Utility functions for LIC Policy Scraper
Contains helper functions for data processing, validation, and file operations
"""

import json
import csv
import pandas as pd
import logging
import time
import random
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from fake_useragent import UserAgent

def setup_logging(log_file: str, level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger('LIC_Scraper')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_random_user_agent() -> str:
    """Get a random user agent string"""
    ua = UserAgent()
    return ua.random

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.\,\(\)\[\]\:\;\!\?\%\&\@\#\$]', '', text)
    
    return text

def standardize_currency_format(amount_str: str) -> str:
    """Standardize currency format to Rs. X,XX,XXX"""
    if not amount_str:
        return ""

    # Extract numbers from the string
    numbers = re.findall(r'[\d,]+', amount_str)
    if not numbers:
        return amount_str

    # Get the largest number (likely the amount)
    amount = numbers[0].replace(',', '')

    if not amount.isdigit():
        return amount_str

    # Convert to integer and format with commas
    try:
        amount_int = int(amount)

        # Handle different units
        if 'lakh' in amount_str.lower() or 'lac' in amount_str.lower():
            return f"Rs. {amount_int:,} lakhs"
        elif 'crore' in amount_str.lower():
            return f"Rs. {amount_int:,} crores"
        elif 'thousand' in amount_str.lower():
            return f"Rs. {amount_int:,} thousands"
        else:
            # Standard formatting with commas
            return f"Rs. {amount_int:,}"
    except ValueError:
        return amount_str

def standardize_age_format(age_str: str) -> str:
    """Standardize age format to XX-XX years or XX years"""
    if not age_str:
        return ""

    # Extract age numbers
    age_numbers = re.findall(r'\d+', age_str)
    if not age_numbers:
        return age_str

    if len(age_numbers) >= 2:
        # Range format
        min_age, max_age = age_numbers[0], age_numbers[1]
        return f"{min_age}-{max_age} years"
    elif len(age_numbers) == 1:
        # Single age format
        age = age_numbers[0]
        if 'minimum' in age_str.lower() or 'min' in age_str.lower():
            return f"{age} years minimum"
        elif 'maximum' in age_str.lower() or 'max' in age_str.lower():
            return f"{age} years maximum"
        else:
            return f"{age} years"

    return age_str

def determine_subcategory(policy_name: str, features: List[str]) -> str:
    """Determine subcategory based on policy name and features"""
    policy_name_lower = policy_name.lower()
    features_text = ' '.join(features).lower()

    # Endowment plans
    if any(word in policy_name_lower for word in ['endowment', 'jeevan anand', 'jeevan lakshya']):
        return 'Endowment_Plans'

    # Money back plans
    elif any(word in policy_name_lower for word in ['money back', 'jeevan labh']):
        return 'Money_Back_Plans'

    # Term plans
    elif any(word in policy_name_lower for word in ['term', 'jeevan amar', 'tech term']):
        return 'Term_Assurance_Plans'

    # Whole life plans
    elif any(word in policy_name_lower for word in ['whole life', 'jeevan umang', 'jeevan azad']):
        return 'Whole_Life_Plans'

    # Child plans
    elif any(word in policy_name_lower for word in ['child', 'amritbaal', 'jeevan tarun']):
        return 'Child_Plans'

    # Pension plans
    elif any(word in policy_name_lower for word in ['pension', 'jeevan akshay', 'jeevan shanti']):
        return 'Pension_Plans'

    # Unit linked plans
    elif any(word in policy_name_lower for word in ['ulip', 'unit linked', 'nivesh', 'index']):
        return 'Unit_Linked_Plans'

    # Micro insurance
    elif any(word in policy_name_lower for word in ['micro', 'bachat']):
        return 'Micro_Insurance_Plans'

    # Default based on features
    elif any(word in features_text for word in ['maturity', 'endowment', 'bonus']):
        return 'Endowment_Plans'
    elif any(word in features_text for word in ['money back', 'survival benefit']):
        return 'Money_Back_Plans'
    elif any(word in features_text for word in ['term', 'pure protection']):
        return 'Term_Assurance_Plans'
    else:
        return 'Insurance_Plans'

def validate_and_clean_data(policy_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean policy data before saving"""
    cleaned_data = policy_data.copy()

    # Standardize currency fields
    if 'eligibility_criteria' in cleaned_data and isinstance(cleaned_data['eligibility_criteria'], dict):
        if 'income_requirement' in cleaned_data['eligibility_criteria']:
            cleaned_data['eligibility_criteria']['income_requirement'] = standardize_currency_format(
                cleaned_data['eligibility_criteria']['income_requirement']
            )

    # Standardize age fields
    if 'eligibility_criteria' in cleaned_data and isinstance(cleaned_data['eligibility_criteria'], dict):
        if 'age_range' in cleaned_data['eligibility_criteria']:
            cleaned_data['eligibility_criteria']['age_range'] = standardize_age_format(
                cleaned_data['eligibility_criteria']['age_range']
            )
        if 'age_limit' in cleaned_data['eligibility_criteria']:
            cleaned_data['eligibility_criteria']['age_limit'] = standardize_age_format(
                cleaned_data['eligibility_criteria']['age_limit']
            )

    # Determine subcategory if missing
    if not cleaned_data.get('subcategory'):
        cleaned_data['subcategory'] = determine_subcategory(
            cleaned_data.get('policy_name', ''),
            cleaned_data.get('features_benefits', [])
        )

    # Clean text fields
    text_fields = ['features_benefits', 'maturity_benefits', 'terms_conditions', 'tax_benefits']
    for field in text_fields:
        if field in cleaned_data and isinstance(cleaned_data[field], list):
            cleaned_data[field] = [clean_text(item) for item in cleaned_data[field] if clean_text(item)]

    return cleaned_data

def extract_plan_number(text: str) -> Optional[str]:
    """Extract plan number from text"""
    if not text:
        return None
    
    # Look for plan number patterns
    patterns = [
        r'Plan\s+No\.?\s*:?\s*(\d+)',
        r'Plan\s+Number\s*:?\s*(\d+)',
        r'(\d{3,4})'  # 3-4 digit numbers
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_uin_number(text: str) -> Optional[str]:
    """Extract UIN number from text"""
    if not text:
        return None
    
    # Look for UIN patterns
    patterns = [
        r'UIN\s+No\.?\s*:?\s*([A-Z0-9]+)',
        r'UIN\s*:?\s*([A-Z0-9]+)',
        r'(\d{3}[A-Z]\d{3}V\d{2})'  # Standard UIN format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def flatten_policy_data_for_vector_db(data: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten policy data structure for vector database compatibility"""
    flattened = {}

    # Basic fields
    flattened['policy_id'] = f"{data.get('category', 'unknown')}_{data.get('plan_number', 'unknown')}"
    flattened['policy_name'] = data.get('policy_name', '')
    flattened['plan_number'] = data.get('plan_number', '')
    flattened['uin_number'] = data.get('uin_number', '')
    flattened['category'] = data.get('category', '')
    flattened['subcategory'] = data.get('subcategory', '')

    # Flatten features and benefits into a single text field
    features = data.get('features_benefits', [])
    if isinstance(features, list):
        flattened['features_benefits_text'] = ' | '.join(features)
        flattened['features_count'] = len(features)
    else:
        flattened['features_benefits_text'] = str(features) if features else ''
        flattened['features_count'] = 0

    # Flatten eligibility criteria
    eligibility = data.get('eligibility_criteria', {})
    if isinstance(eligibility, dict):
        flattened['age_range'] = eligibility.get('age_range', '')
        flattened['age_limit'] = eligibility.get('age_limit', '')
        flattened['income_requirement'] = eligibility.get('income_requirement', '')
        flattened['medical_examination'] = eligibility.get('medical_examination', '')
        flattened['residency_requirement'] = eligibility.get('residency_requirement', '')
    else:
        flattened['age_range'] = ''
        flattened['age_limit'] = ''
        flattened['income_requirement'] = ''
        flattened['medical_examination'] = ''
        flattened['residency_requirement'] = ''

    # Flatten premium payment options
    premium_options = data.get('premium_payment_options', [])
    if isinstance(premium_options, list):
        flattened['premium_payment_options'] = ' | '.join(premium_options)
        flattened['premium_options_count'] = len(premium_options)
    else:
        flattened['premium_payment_options'] = str(premium_options) if premium_options else ''
        flattened['premium_options_count'] = 0

    # Flatten maturity benefits
    maturity_benefits = data.get('maturity_benefits', [])
    if isinstance(maturity_benefits, list):
        flattened['maturity_benefits_text'] = ' | '.join(maturity_benefits)
        flattened['maturity_benefits_count'] = len(maturity_benefits)
    else:
        flattened['maturity_benefits_text'] = str(maturity_benefits) if maturity_benefits else ''
        flattened['maturity_benefits_count'] = 0

    # Flatten surrender values
    surrender_values = data.get('surrender_values', {})
    if isinstance(surrender_values, dict):
        flattened['surrender_clause'] = surrender_values.get('surrender_clause', '')
        flattened['surrender_period'] = surrender_values.get('surrender_period', '')
        flattened['surrender_value'] = surrender_values.get('surrender_value', '')
    else:
        flattened['surrender_clause'] = ''
        flattened['surrender_period'] = ''
        flattened['surrender_value'] = ''

    # Flatten tax benefits
    tax_benefits = data.get('tax_benefits', [])
    if isinstance(tax_benefits, list):
        flattened['tax_benefits_text'] = ' | '.join(tax_benefits)
        flattened['tax_benefits_count'] = len(tax_benefits)
    else:
        flattened['tax_benefits_text'] = str(tax_benefits) if tax_benefits else ''
        flattened['tax_benefits_count'] = 0

    # Flatten terms and conditions
    terms_conditions = data.get('terms_conditions', [])
    if isinstance(terms_conditions, list):
        flattened['terms_conditions_text'] = ' | '.join(terms_conditions)
        flattened['terms_conditions_count'] = len(terms_conditions)
    else:
        flattened['terms_conditions_text'] = str(terms_conditions) if terms_conditions else ''
        flattened['terms_conditions_count'] = 0

    # Flatten riders
    riders = data.get('riders_available', [])
    if isinstance(riders, list):
        flattened['riders_available_text'] = ' | '.join(riders)
        flattened['riders_count'] = len(riders)
    else:
        flattened['riders_available_text'] = str(riders) if riders else ''
        flattened['riders_count'] = 0

    # Metadata fields
    flattened['source_url'] = data.get('source_url', '')
    flattened['scraped_timestamp'] = data.get('scraped_timestamp', '')
    flattened['scraped_successfully'] = data.get('scraped_successfully', False)

    # PDF extraction metadata
    pdf_sources = data.get('pdf_sources', [])
    if isinstance(pdf_sources, list):
        flattened['pdf_sources'] = ' | '.join(pdf_sources)
        flattened['pdf_sources_count'] = len(pdf_sources)
    else:
        flattened['pdf_sources'] = str(pdf_sources) if pdf_sources else ''
        flattened['pdf_sources_count'] = 0

    # Enhanced data completeness calculation
    required_fields = {
        'policy_name': 1.0,
        'plan_number': 1.0,
        'uin_number': 1.0,
        'features_benefits_text': 1.0,
        'age_range': 1.5,  # Higher weight for critical eligibility
        'age_limit': 1.0,  # Alternative to age_range
        'income_requirement': 1.5,  # Higher weight for critical eligibility
        'medical_examination': 1.0,
        'premium_payment_options': 1.0,
        'maturity_benefits_text': 1.5,  # Higher weight for key benefit
        'surrender_clause': 1.0,
        'tax_benefits_text': 1.0,
        'terms_conditions_text': 1.0
    }

    total_weight = 0
    achieved_weight = 0

    for field, weight in required_fields.items():
        total_weight += weight
        field_value = flattened.get(field, '')

        if field_value and str(field_value).strip() and str(field_value) != 'nan':
            # Special handling for age fields (either age_range OR age_limit is sufficient)
            if field == 'age_limit' and flattened.get('age_range', ''):
                continue  # Skip age_limit if age_range is present
            elif field == 'age_range' and not field_value and flattened.get('age_limit', ''):
                achieved_weight += weight  # Count age_limit as fulfilling age requirement
            else:
                achieved_weight += weight

    flattened['data_completeness_score'] = round((achieved_weight / total_weight) * 100, 2)

    return flattened

def save_data_vector_db_format(data: Dict[str, Any], base_filename: str, output_dir: str) -> Dict[str, str]:
    """Save data in CSV and PDF formats optimized for vector database"""
    saved_files = {}

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Flatten data for vector database
    flattened_data = flatten_policy_data_for_vector_db(data)

    # Save as CSV (primary format for vector database)
    csv_file = f"{output_dir}/{base_filename}.csv"
    df = pd.DataFrame([flattened_data])
    df.to_csv(csv_file, index=False, encoding='utf-8')
    saved_files['csv'] = csv_file

    return saved_files

def create_master_csv_for_vector_db(all_policies: List[Dict[str, Any]], output_dir: str) -> str:
    """Create a master CSV file with all policies for vector database"""
    master_data = []

    for policy in all_policies:
        flattened_policy = flatten_policy_data_for_vector_db(policy)
        master_data.append(flattened_policy)

    # Create master CSV
    master_csv_file = f"{output_dir}/Master_Index/lic_policies_master_vector_db.csv"
    Path(f"{output_dir}/Master_Index").mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(master_data)
    df.to_csv(master_csv_file, index=False, encoding='utf-8')

    return master_csv_file

def create_pdf_summary_report(all_policies: List[Dict[str, Any]], output_dir: str) -> str:
    """Create a comprehensive PDF summary report"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    pdf_file = f"{output_dir}/Reports/lic_policies_comprehensive_report.pdf"
    Path(f"{output_dir}/Reports").mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("LIC Policies Comprehensive Report", title_style))
    story.append(Spacer(1, 20))

    # Summary statistics
    total_policies = len(all_policies)
    successful_policies = len([p for p in all_policies if p.get('scraped_successfully', False)])

    summary_data = [
        ['Metric', 'Value'],
        ['Total Policies Scraped', str(total_policies)],
        ['Successful Extractions', str(successful_policies)],
        ['Success Rate', f"{(successful_policies/total_policies)*100:.1f}%"],
        ['Scraping Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]

    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(Paragraph("Summary Statistics", styles['Heading2']))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Category breakdown
    category_stats = {}
    for policy in all_policies:
        category = policy.get('category', 'Unknown')
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'successful': 0}
        category_stats[category]['total'] += 1
        if policy.get('scraped_successfully', False):
            category_stats[category]['successful'] += 1

    category_data = [['Category', 'Total Policies', 'Successful', 'Success Rate']]
    for category, stats in category_stats.items():
        success_rate = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
        category_data.append([
            category.replace('_', ' '),
            str(stats['total']),
            str(stats['successful']),
            f"{success_rate:.1f}%"
        ])

    category_table = Table(category_data)
    category_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(Paragraph("Category Breakdown", styles['Heading2']))
    story.append(category_table)
    story.append(Spacer(1, 20))

    # Policy details (first 10 policies as sample)
    story.append(Paragraph("Sample Policy Details", styles['Heading2']))

    for i, policy in enumerate(all_policies[:10], 1):
        story.append(Paragraph(f"{i}. {policy.get('policy_name', 'Unknown')}", styles['Heading3']))

        details = [
            f"Plan Number: {policy.get('plan_number', 'N/A')}",
            f"UIN: {policy.get('uin_number', 'N/A')}",
            f"Category: {policy.get('category', 'N/A')}",
            f"Features Count: {len(policy.get('features_benefits', []))}",
            f"PDF Sources: {len(policy.get('pdf_sources', []))}"
        ]

        for detail in details:
            story.append(Paragraph(detail, styles['Normal']))

        story.append(Spacer(1, 10))

    # Build PDF
    doc.build(story)
    return pdf_file

def save_data_multiple_formats(data: Dict[str, Any], base_filename: str, output_dir: str) -> Dict[str, str]:
    """Save data in multiple formats (JSON, CSV, Excel) - Legacy function"""
    saved_files = {}

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Save as JSON
    json_file = f"{output_dir}/{base_filename}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    saved_files['json'] = json_file

    # Save as CSV (flatten the data if needed)
    csv_file = f"{output_dir}/{base_filename}.csv"
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([data])

    df.to_csv(csv_file, index=False, encoding='utf-8')
    saved_files['csv'] = csv_file

    # Save as Excel
    excel_file = f"{output_dir}/{base_filename}.xlsx"
    df.to_excel(excel_file, index=False, engine='openpyxl')
    saved_files['xlsx'] = excel_file

    return saved_files

def validate_policy_data(policy_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate policy data completeness"""
    validation_result = {
        'is_valid': True,
        'missing_fields': [],
        'empty_fields': [],
        'completeness_score': 0
    }
    
    total_fields = len(required_fields)
    valid_fields = 0
    
    for field in required_fields:
        if field not in policy_data:
            validation_result['missing_fields'].append(field)
            validation_result['is_valid'] = False
        elif not policy_data[field] or policy_data[field] == "":
            validation_result['empty_fields'].append(field)
        else:
            valid_fields += 1
    
    validation_result['completeness_score'] = (valid_fields / total_fields) * 100
    
    return validation_result

def create_master_index(all_policies: List[Dict[str, Any]], output_dir: str) -> str:
    """Create a master index file with all policies"""
    master_index = {
        'metadata': {
            'total_policies': len(all_policies),
            'scraping_timestamp': datetime.now().isoformat(),
            'categories': {}
        },
        'policies': all_policies
    }
    
    # Count policies by category
    for policy in all_policies:
        category = policy.get('category', 'Unknown')
        if category not in master_index['metadata']['categories']:
            master_index['metadata']['categories'][category] = 0
        master_index['metadata']['categories'][category] += 1
    
    # Save master index
    index_file = f"{output_dir}/Master_Index/master_policy_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)
    
    return index_file

def generate_summary_report(all_policies: List[Dict[str, Any]], validation_results: List[Dict], output_dir: str) -> str:
    """Generate a comprehensive summary report"""
    report = {
        'scraping_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_policies_found': len(all_policies),
            'successful_scrapes': len([p for p in all_policies if p.get('scraped_successfully', False)]),
            'failed_scrapes': len([p for p in all_policies if not p.get('scraped_successfully', False)])
        },
        'category_breakdown': {},
        'data_quality': {
            'average_completeness': 0,
            'policies_with_complete_data': 0,
            'common_missing_fields': {}
        },
        'validation_details': validation_results
    }
    
    # Category breakdown
    for policy in all_policies:
        category = policy.get('category', 'Unknown')
        if category not in report['category_breakdown']:
            report['category_breakdown'][category] = {
                'total': 0,
                'successful': 0,
                'failed': 0
            }
        
        report['category_breakdown'][category]['total'] += 1
        if policy.get('scraped_successfully', False):
            report['category_breakdown'][category]['successful'] += 1
        else:
            report['category_breakdown'][category]['failed'] += 1
    
    # Data quality analysis
    if validation_results:
        total_completeness = sum(v.get('completeness_score', 0) for v in validation_results)
        report['data_quality']['average_completeness'] = total_completeness / len(validation_results)
        report['data_quality']['policies_with_complete_data'] = len([v for v in validation_results if v.get('completeness_score', 0) == 100])
        
        # Count missing fields
        all_missing_fields = []
        for v in validation_results:
            all_missing_fields.extend(v.get('missing_fields', []))
            all_missing_fields.extend(v.get('empty_fields', []))
        
        from collections import Counter
        field_counts = Counter(all_missing_fields)
        report['data_quality']['common_missing_fields'] = dict(field_counts.most_common(10))
    
    # Save report
    report_file = f"{output_dir}/Reports/scraping_summary_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file

def safe_request(url: str, headers: Dict[str, str], timeout: int = 30, retries: int = 3) -> Optional[requests.Response]:
    """Make a safe HTTP request with retries"""
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(1, 3))  # Random delay
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == retries - 1:
                logging.error(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
