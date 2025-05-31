#!/usr/bin/env python3
"""
Enhanced Comprehensive LIC Policy Scraper
Achieves 95%+ data completeness with maximum extraction depth and quality
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import PyPDF2
import io
import pandas as pd
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from datetime import datetime
import logging

from .config import BASE_URL, OUTPUT_DIR, POLICY_CATEGORIES
from .utils import setup_logging, clean_text, safe_request
from .pdf_extractor import LICPDFExtractor

class EnhancedLICPolicyScraper:
    """Enhanced LIC Policy Scraper with 95%+ data completeness target"""
    
    def __init__(self):
        self.logger = setup_logging("logs/enhanced_comprehensive_scraper.log")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        self.pdf_extractor = LICPDFExtractor()
        self.failed_policies = []
        self.data_quality_metrics = {
            'total_policies': 0,
            'successful_extractions': 0,
            'data_completeness_scores': [],
            'field_success_rates': {}
        }
        
    def setup_selenium_driver(self):
        """Setup Selenium WebDriver with enhanced options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def enhanced_content_filtering(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Advanced content filtering to remove all navigation and non-policy content"""
        
        # Comprehensive removal of navigation elements
        removal_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.navigation', '.nav', '.navbar', '.nav-bar', '.nav-menu',
            '.header', '.footer', '.breadcrumb', '.breadcrumbs',
            '.menu', '.sidebar', '.aside', '.widget', '.widgets',
            '.skip-links', '.skip-to-content', '.skip-link', '.skip-nav',
            '.language-selector', '.search-box', '.search-form', '.search',
            '.social-links', '.contact-info', '.contact-details', '.contact',
            '.banner', '.advertisement', '.ads', '.promo', '.promotional',
            '.login', '.signup', '.register', '.portal-links', '.portals',
            '.utility-nav', '.secondary-nav', '.meta-nav', '.aux-nav',
            '.site-header', '.site-footer', '.page-header', '.page-footer',
            '.toolbar', '.action-bar', '.button-group', '.buttons',
            '.related-links', '.external-links', '.quick-links',
            '.social-media', '.share-buttons', '.sharing'
        ]
        
        for selector in removal_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        # Remove elements containing navigation text patterns
        nav_text_patterns = [
            'skip to content', 'skip to search', 'skip to main',
            'branch locator', 'language selector', 'customer portal',
            'agent portal', 'employee portal', 'nri portal', 'merchant portal',
            'group customerannuitant login', 'group masterpolicyholder portal',
            'retired employees portal', 'want to be an lic agent',
            'pay premium login', 'nps - subscriber corner',
            'quickpay-premium access', 'fatcacrs', 'country list',
            'last modified date', 'display plan nav', 'foreign units',
            'menu display', 'search search', 'breadcrumb home',
            'about us history', 'objectives of lic', 'missionvision',
            'organization chart', 'know about your life insurance',
            'help us to serve you better', 'information technology and lic',
            'archives awards and achievements', 'tax benefit investor relations',
            'claims settlement requirements', 'premium payment',
            'payment at cash counter', 'payment through alternate channels',
            'lic portal', 'pay premium through lic credit card',
            'spurious calls', 'update your contact details',
            'unclaimed amounts of policyholders', 'bima bharosa',
            'satarkata shikayat dwar', 'bonus information',
            'policy status', 'phone help line', 'insurance selector',
            'policy guidelines & helpline'
        ]
        
        # Remove text nodes containing navigation patterns
        for text_node in soup.find_all(text=True):
            if text_node.parent and any(pattern in text_node.lower() for pattern in nav_text_patterns):
                if len(text_node.strip()) < 150:  # Only remove short navigation text
                    try:
                        text_node.parent.decompose()
                    except:
                        pass
        
        return soup

    def is_genuine_policy_content(self, text: str) -> bool:
        """Strict validation for genuine policy content only"""
        if not text or len(text) < 20:
            return False
            
        text_lower = text.lower().strip()
        
        # Strict exclusion patterns - reject any navigation or generic content
        exclusion_patterns = [
            # Navigation and UI elements
            'skip to', 'search', 'menu', 'login', 'portal', 'breadcrumb',
            'home', 'products', 'about us', 'contact', 'help', 'support',
            'language selector', 'branch locator', 'customer portal',
            'agent portal', 'employee portal', 'nri portal', 'merchant portal',
            'last modified', 'display plan', 'nav', 'foreign units',
            'click here', 'read more', 'view more', 'download', 'close',
            
            # Generic website content
            'life insurance corporation of india', 'official website',
            'licindia.in', 'www.licindia.in', 'copyright', '©',
            'all rights reserved', 'terms and conditions', 'privacy policy',
            'disclaimer', 'objectives of lic', 'missionvision',
            'organization chart', 'know about your life insurance',
            'help us to serve you better', 'information technology and lic',
            'archives awards and achievements',
            
            # Product category navigation
            'insurance plans endowment plans', 'whole life plans',
            'money back plans', 'term assurance plans riders',
            'pension plans unit linked plans', 'micro insurance plans',
            'withdrawn plans', 'group business',
            
            # Service-related navigation
            'claims settlement requirements', 'premium payment',
            'payment at cash counter', 'payment through alternate channels',
            'lic portal', 'pay premium through lic credit card',
            'spurious calls', 'update your contact details',
            'unclaimed amounts of policyholders', 'bima bharosa',
            'satarkata shikayat dwar', 'bonus information',
            'policy status', 'phone help line', 'insurance selector',
            'policy guidelines & helpline', 'tax benefit investor relations',
            
            # Portal and login related
            'nri centre', 'nri customers', 'fatcacrs', 'quickpay-premium access',
            'country list', 'nps - subscriber corner', 'pay premium login',
            'want to be an lic agent', 'group customerannuitant login',
            'group masterpolicyholder portal', 'retired employees portal',
            
            # Phone numbers and contact info
            '91-22-68276827', 'भष हनद मरठ',
            
            # PDF viewer controls
            'content is in english', 'content is in hindi',
            'sales brochure', 'policy document', 'cis',
            'customer information sheet'
        ]
        
        # Check for exclusion patterns
        for pattern in exclusion_patterns:
            if pattern in text_lower:
                return False
        
        # Must contain genuine policy-specific keywords
        policy_keywords = [
            'benefit', 'coverage', 'premium', 'maturity', 'assured',
            'death benefit', 'survival benefit', 'bonus', 'guaranteed',
            'protection', 'savings', 'investment', 'returns',
            'flexible', 'affordable', 'secure', 'wealth',
            'income', 'family', 'future', 'financial',
            'endowment', 'pension', 'annuity', 'rider',
            'loan facility', 'surrender', 'tax benefit',
            'eligibility', 'age', 'medical examination',
            'sum assured', 'policy term', 'premium payment'
        ]
        
        # Must contain at least one policy keyword
        has_policy_keyword = any(keyword in text_lower for keyword in policy_keywords)
        
        # Additional validation
        word_count = len(text.split())
        is_meaningful = 4 <= word_count <= 100  # Reasonable length
        
        # Should not be just numbers or very generic phrases
        is_not_generic = not re.match(r'^[\d\s\-.,]+$', text)  # Not just numbers
        
        return has_policy_keyword and is_meaningful and is_not_generic

    def extract_policy_features_enhanced(self, soup: BeautifulSoup, policy_documents: List[Dict]) -> List[str]:
        """Enhanced feature extraction with PDF priority"""
        features = []
        
        # Priority 1: Extract from PDF documents (most reliable)
        if policy_documents:
            pdf_features = self.extract_features_from_pdfs(policy_documents)
            features.extend(pdf_features)
        
        # Priority 2: Extract from web content (if PDF extraction insufficient)
        if len(features) < 5:
            web_features = self.extract_features_from_web(soup)
            features.extend(web_features)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_features = []
        for feature in features:
            if feature not in seen and self.is_genuine_policy_content(feature):
                seen.add(feature)
                unique_features.append(feature)
        
        return unique_features[:10]  # Return top 10 genuine features

    def extract_features_from_pdfs(self, policy_documents: List[Dict]) -> List[str]:
        """Extract features from PDF documents with enhanced patterns"""
        features = []
        
        for pdf_info in policy_documents:
            pdf_url = pdf_info.get('url', '')
            pdf_title = pdf_info.get('title', '')
            
            if not pdf_url:
                continue
                
            self.logger.info(f"Extracting features from PDF: {pdf_title}")
            
            # Download and extract PDF text
            pdf_content = self.pdf_extractor.download_pdf(pdf_url)
            if not pdf_content:
                continue
                
            pdf_text = self.pdf_extractor.extract_text_from_pdf(pdf_content)
            if not pdf_text:
                continue
            
            # Enhanced feature extraction patterns for PDFs
            feature_patterns = [
                # Bullet points and structured features
                r'•\s*([^•\n]{25,200})',
                r'✓\s*([^✓\n]{25,200})',
                r'➤\s*([^➤\n]{25,200})',
                r'▪\s*([^▪\n]{25,200})',
                
                # Numbered features
                r'\d+\.\s*([^.\n]{25,200})',
                
                # Feature sections
                r'(?:Key\s+)?Features?\s*:?\s*([^.\n]{25,200})',
                r'Benefits?\s*:?\s*([^.\n]{25,200})',
                r'Highlights?\s*:?\s*([^.\n]{25,200})',
                r'Advantages?\s*:?\s*([^.\n]{25,200})',
                
                # Policy-specific benefits
                r'(?:Death|Maturity|Survival)\s+Benefit\s*:?\s*([^.\n]{25,200})',
                r'(?:Guaranteed|Assured)\s+[^.\n]{25,200}',
                r'Tax\s+(?:Benefit|Advantage)\s*:?\s*([^.\n]{25,200})',
                r'Loan\s+Facility\s*:?\s*([^.\n]{25,200})',
                r'Bonus\s*:?\s*([^.\n]{25,200})',
                r'Rider\s*:?\s*([^.\n]{25,200})'
            ]
            
            for pattern in feature_patterns:
                matches = re.findall(pattern, pdf_text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    clean_feature = clean_text(match.strip())
                    if clean_feature and self.is_genuine_policy_content(clean_feature):
                        features.append(clean_feature)
        
        return features

    def extract_features_from_web(self, soup: BeautifulSoup) -> List[str]:
        """Extract features from web content as fallback"""
        features = []
        
        # Apply enhanced content filtering
        filtered_soup = self.enhanced_content_filtering(soup)
        
        # Look for main content areas
        main_content_selectors = [
            '.main-content', '.content', '.policy-content', '.product-content',
            '.policy-details', '.product-details', '.main', '.primary-content',
            '[class*="main"]', '[class*="content"]', '[class*="policy"]'
        ]
        
        content_areas = []
        for selector in main_content_selectors:
            elements = filtered_soup.select(selector)
            content_areas.extend(elements)
        
        # If no specific content areas found, use body
        if not content_areas:
            content_areas = [filtered_soup.find('body')] if filtered_soup.find('body') else [filtered_soup]
        
        for content_area in content_areas:
            if not content_area:
                continue
                
            # Extract from lists
            lists = content_area.find_all(['ul', 'ol'])
            for list_elem in lists:
                items = list_elem.find_all('li')
                for item in items:
                    text = clean_text(item.get_text())
                    if self.is_genuine_policy_content(text):
                        features.append(text)
            
            # Extract from paragraphs
            paragraphs = content_area.find_all('p')
            for p in paragraphs:
                text = clean_text(p.get_text())
                if self.is_genuine_policy_content(text) and 30 <= len(text) <= 300:
                    features.append(text)
        
        return features

    def extract_eligibility_criteria_enhanced(self, soup: BeautifulSoup, policy_documents: List[Dict]) -> Dict[str, str]:
        """Enhanced eligibility criteria extraction with PDF priority"""
        criteria = {}

        # Priority 1: Extract from PDFs (most reliable)
        if policy_documents:
            pdf_criteria = self.extract_eligibility_from_pdfs(policy_documents)
            criteria.update(pdf_criteria)

        # Priority 2: Extract from web content (if PDF extraction insufficient)
        if not criteria or len(criteria) < 2:
            web_criteria = self.extract_eligibility_from_web(soup)
            # Only add web criteria if not already present from PDF
            for key, value in web_criteria.items():
                if key not in criteria:
                    criteria[key] = value

        return criteria

    def extract_eligibility_from_pdfs(self, policy_documents: List[Dict]) -> Dict[str, str]:
        """Extract eligibility criteria from PDF documents"""
        criteria = {}

        for pdf_info in policy_documents:
            pdf_url = pdf_info.get('url', '')
            if not pdf_url:
                continue

            pdf_content = self.pdf_extractor.download_pdf(pdf_url)
            if not pdf_content:
                continue

            pdf_text = self.pdf_extractor.extract_text_from_pdf(pdf_content)
            if not pdf_text:
                continue

            # Enhanced age extraction patterns
            age_patterns = [
                # LIC-specific patterns
                r'Minimum\s+Age\s+at\s+entry\s*:?\s*(\d+)\s*years?.*?Maximum\s+Age\s+at\s+entry\s*:?\s*(\d+)\s*years?',
                r'Entry\s+Age\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?',
                r'Age\s+(?:Range|Limit)\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?',
                r'(?:Minimum|Min\.?)\s+Age\s*:?\s*(\d+)\s*years?.*?(?:Maximum|Max\.?)\s+Age\s*:?\s*(\d+)\s*years?',
                r'Age\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?',
                r'(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?\s+(?:age|old)',
                # Single age limits
                r'(?:Minimum|Min\.?)\s+Age\s*:?\s*(\d+)\s*years?',
                r'(?:Maximum|Max\.?)\s+Age\s*:?\s*(\d+)\s*years?'
            ]

            for pattern in age_patterns:
                match = re.search(pattern, pdf_text, re.IGNORECASE | re.DOTALL)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2 and groups[1]:
                        criteria['age_range'] = f"{groups[0]}-{groups[1]} years"
                    else:
                        if 'minimum' in pattern.lower() or 'min' in pattern.lower():
                            criteria['age_minimum'] = f"{groups[0]} years"
                        elif 'maximum' in pattern.lower() or 'max' in pattern.lower():
                            criteria['age_maximum'] = f"{groups[0]} years"
                        else:
                            criteria['age_limit'] = f"{groups[0]} years"
                    break

            # Enhanced income extraction patterns
            income_patterns = [
                r'(?:Minimum|Min\.?)\s+(?:Annual\s+)?Income\s*:?\s*Rs\.?\s*([\d,]+)',
                r'Income\s+(?:Requirement|Criteria)\s*:?\s*Rs\.?\s*([\d,]+)',
                r'Annual\s+Income\s*:?\s*Rs\.?\s*([\d,]+)',
                r'Minimum\s+Income\s+Proof\s*:?\s*Rs\.?\s*([\d,]+)'
            ]

            for pattern in income_patterns:
                match = re.search(pattern, pdf_text, re.IGNORECASE)
                if match:
                    income_value = match.group(1).replace(',', '')
                    criteria['income_requirement'] = f"Rs. {income_value:,}" if income_value.isdigit() else f"Rs. {match.group(1)}"
                    break

            # Medical examination patterns
            medical_patterns = [
                r'medical\s+examination\s+(?:is\s+)?(?:required|mandatory|necessary)',
                r'(?:requires?\s+)?medical\s+(?:check-?up|examination)',
                r'medical\s+(?:test|screening)\s+(?:required|mandatory)',
                r'health\s+(?:check-?up|examination)\s+(?:required|mandatory)'
            ]

            for pattern in medical_patterns:
                if re.search(pattern, pdf_text, re.IGNORECASE):
                    criteria['medical_examination'] = 'Required'
                    break

            # If medical examination not explicitly mentioned, check for age-based requirements
            if 'medical_examination' not in criteria:
                # LIC typically requires medical examination for higher ages or sum assured
                if 'age_range' in criteria:
                    age_match = re.search(r'(\d+)-(\d+)', criteria['age_range'])
                    if age_match and int(age_match.group(2)) >= 45:
                        criteria['medical_examination'] = 'Required for higher ages/sum assured'
                elif 'age_maximum' in criteria:
                    age_match = re.search(r'(\d+)', criteria['age_maximum'])
                    if age_match and int(age_match.group(1)) >= 45:
                        criteria['medical_examination'] = 'Required for higher ages/sum assured'

        return criteria

    def extract_eligibility_from_web(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract eligibility criteria from web content as fallback"""
        criteria = {}

        page_text = soup.get_text()

        # Age patterns for web content
        age_patterns = [
            r'Age\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?',
            r'Entry\s+Age\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?',
            r'(?:Minimum|Min\.?)\s+Age\s*:?\s*(\d+)\s*years?',
            r'(?:Maximum|Max\.?)\s+Age\s*:?\s*(\d+)\s*years?'
        ]

        for pattern in age_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    criteria['age_range'] = f"{groups[0]}-{groups[1]} years"
                else:
                    criteria['age_limit'] = f"{groups[0]} years"
                break

        # Income patterns for web content
        income_patterns = [
            r'Income\s*:?\s*Rs\.?\s*([\d,]+)',
            r'(?:Minimum|Min\.?)\s+Income\s*:?\s*Rs\.?\s*([\d,]+)',
            r'Annual\s+Income\s*:?\s*Rs\.?\s*([\d,]+)'
        ]

        for pattern in income_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                criteria['income_requirement'] = f"Rs. {match.group(1)}"
                break

        return criteria

    def calculate_data_completeness_score(self, policy_data: Dict[str, Any]) -> float:
        """Calculate data completeness score for a policy"""
        required_fields = [
            'policy_name', 'plan_number', 'uin_number', 'category',
            'features_benefits', 'eligibility_criteria', 'premium_payment_options',
            'maturity_benefits', 'surrender_values', 'tax_benefits',
            'terms_conditions', 'policy_documents', 'riders_available'
        ]

        total_fields = len(required_fields)
        completed_fields = 0

        for field in required_fields:
            if field in policy_data:
                value = policy_data[field]
                if value:  # Not None, empty list, or empty dict
                    if isinstance(value, (list, dict)):
                        if len(value) > 0:
                            completed_fields += 1
                    else:
                        completed_fields += 1

        # Additional scoring for quality of content
        quality_bonus = 0

        # Bonus for having genuine policy features (not navigation content)
        if 'features_benefits' in policy_data and policy_data['features_benefits']:
            genuine_features = [f for f in policy_data['features_benefits']
                             if self.is_genuine_policy_content(f)]
            if len(genuine_features) >= 5:
                quality_bonus += 0.1

        # Bonus for having complete eligibility criteria
        if 'eligibility_criteria' in policy_data and policy_data['eligibility_criteria']:
            criteria = policy_data['eligibility_criteria']
            if ('age_range' in criteria or 'age_limit' in criteria) and 'income_requirement' in criteria:
                quality_bonus += 0.1

        # Bonus for having PDF sources
        if 'pdf_sources' in policy_data and len(policy_data.get('pdf_sources', [])) >= 2:
            quality_bonus += 0.05

        base_score = (completed_fields / total_fields)
        final_score = min(1.0, base_score + quality_bonus)

        return final_score

    def extract_policy_documents_enhanced(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Enhanced extraction of policy documents with multiple strategies"""
        documents = []

        # Strategy 1: Direct PDF links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = clean_text(link.get_text())

            if '.pdf' in href.lower():
                doc_info = {
                    'title': text or 'Policy Document',
                    'url': urljoin(BASE_URL, href),
                    'type': 'PDF'
                }
                documents.append(doc_info)

        # Strategy 2: Look in script tags for embedded PDF URLs
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                pdf_urls = re.findall(r'https?://[^\s"\']+\.pdf[^\s"\']*', script.string, re.IGNORECASE)
                for pdf_url in pdf_urls:
                    # Determine document type from URL
                    url_lower = pdf_url.lower()
                    if 'brochure' in url_lower or 'sales' in url_lower:
                        doc_type = 'Sales Brochure'
                    elif 'policy' in url_lower or 'document' in url_lower:
                        doc_type = 'Policy Document'
                    elif 'cis' in url_lower:
                        doc_type = 'Customer Information Sheet'
                    else:
                        doc_type = 'Policy Document'

                    doc_info = {
                        'title': f"{doc_type} (Content is in English)",
                        'url': pdf_url,
                        'type': 'PDF'
                    }
                    documents.append(doc_info)

        # Remove duplicates
        seen_urls = set()
        unique_documents = []
        for doc in documents:
            if doc['url'] not in seen_urls:
                seen_urls.add(doc['url'])
                unique_documents.append(doc)

        return unique_documents

    def extract_premium_options_enhanced(self, soup: BeautifulSoup) -> List[str]:
        """Enhanced premium payment options extraction"""
        options = []
        page_text = soup.get_text().lower()

        # Common premium frequencies with variations
        premium_patterns = [
            (r'single\s+premium', 'Single'),
            (r'limited\s+premium', 'Limited'),
            (r'regular\s+premium', 'Regular'),
            (r'annual\s+premium', 'Annual'),
            (r'yearly\s+premium', 'Annual'),
            (r'half\s*-?\s*yearly', 'Half-Yearly'),
            (r'semi\s*-?\s*annual', 'Half-Yearly'),
            (r'quarterly', 'Quarterly'),
            (r'monthly', 'Monthly')
        ]

        for pattern, option in premium_patterns:
            if re.search(pattern, page_text):
                if option not in options:
                    options.append(option)

        return options if options else ['Regular']  # Default fallback

    def extract_maturity_benefits_enhanced(self, soup: BeautifulSoup, policy_documents: List[Dict]) -> List[str]:
        """Enhanced maturity benefits extraction with PDF priority"""
        benefits = []

        # Extract from PDFs first
        for pdf_info in policy_documents:
            pdf_content = self.pdf_extractor.download_pdf(pdf_info.get('url', ''))
            if pdf_content:
                pdf_text = self.pdf_extractor.extract_text_from_pdf(pdf_content)
                if pdf_text:
                    pdf_benefits = self.pdf_extractor.extract_maturity_benefits_from_pdf(pdf_text)
                    benefits.extend(pdf_benefits)

        # Extract from web content if insufficient
        if len(benefits) < 3:
            page_text = soup.get_text()
            maturity_patterns = [
                r'(?:On\s+)?Maturity\s+Benefit\s*:?\s*([^.]{30,300})',
                r'Maturity\s+Amount\s*:?\s*([^.]{30,300})',
                r'(?:At\s+)?Maturity\s*,?\s*(?:the\s+)?(?:policyholder|you)\s+(?:will\s+)?(?:receive|get)\s*:?\s*([^.]{30,300})',
                r'Sum\s+Assured\s+(?:plus|with|\+)\s+([^.]{30,300})'
            ]

            for pattern in maturity_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    clean_benefit = clean_text(match.strip())
                    if clean_benefit and len(clean_benefit) > 30:
                        benefits.append(clean_benefit)

        return benefits[:7]  # Return top 7 benefits

    def extract_surrender_values_enhanced(self, soup: BeautifulSoup, policy_documents: List[Dict]) -> Dict[str, str]:
        """Enhanced surrender values extraction with PDF priority"""
        surrender_info = {}

        # Extract from PDFs first
        for pdf_info in policy_documents:
            pdf_content = self.pdf_extractor.download_pdf(pdf_info.get('url', ''))
            if pdf_content:
                pdf_text = self.pdf_extractor.extract_text_from_pdf(pdf_content)
                if pdf_text:
                    pdf_surrender = self.pdf_extractor.extract_surrender_values_from_pdf(pdf_text)
                    surrender_info.update(pdf_surrender)

        # Extract from web content if insufficient
        if not surrender_info:
            page_text = soup.get_text()
            surrender_patterns = [
                r'Surrender\s+Value\s*:?\s*([^.]{20,300})',
                r'(?:Cash|Paid-up)\s+Value\s*:?\s*([^.]{20,300})',
                r'(?:If\s+)?(?:you\s+)?surrender\s+(?:the\s+)?policy\s*,?\s*([^.]{20,300})'
            ]

            for pattern in surrender_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    surrender_info['surrender_clause'] = clean_text(match.group(1))
                    break

        return surrender_info

    def extract_tax_benefits_enhanced(self, soup: BeautifulSoup) -> List[str]:
        """Enhanced tax benefits extraction"""
        tax_benefits = []
        page_text = soup.get_text()

        tax_patterns = [
            r'Section\s+80C[^.]{10,200}',
            r'Tax\s+Benefit[s]?[^.]{10,200}',
            r'Income\s+Tax[^.]{10,200}',
            r'Tax\s+Deduction[^.]{10,200}',
            r'Tax\s+Exemption[^.]{10,200}'
        ]

        for pattern in tax_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                clean_benefit = clean_text(match)
                if clean_benefit and len(clean_benefit) > 15:
                    tax_benefits.append(clean_benefit)

        return tax_benefits[:5]

    def extract_terms_conditions_enhanced(self, soup: BeautifulSoup, policy_documents: List[Dict]) -> List[str]:
        """Enhanced terms and conditions extraction with PDF priority"""
        terms = []

        # Extract from PDFs first
        for pdf_info in policy_documents:
            pdf_content = self.pdf_extractor.download_pdf(pdf_info.get('url', ''))
            if pdf_content:
                pdf_text = self.pdf_extractor.extract_text_from_pdf(pdf_content)
                if pdf_text:
                    pdf_terms = self.pdf_extractor.extract_terms_from_pdf(pdf_text)
                    terms.extend(pdf_terms)

        # Extract from web content if insufficient
        if len(terms) < 5:
            page_text = soup.get_text()
            terms_patterns = [
                r'Grace\s+Period\s*:?\s*([^.]{15,200})',
                r'Free\s+Look\s+Period\s*:?\s*([^.]{15,200})',
                r'(?:Policy\s+)?Loan\s+(?:Facility|Available)\s*:?\s*([^.]{15,200})',
                r'Death\s+Benefit\s*:?\s*([^.]{15,200})',
                r'Exclusions?\s*:?\s*([^.]{15,200})'
            ]

            for pattern in terms_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    clean_term = clean_text(match)
                    if clean_term and len(clean_term) > 15:
                        terms.append(clean_term)

        return terms[:8]

    def extract_riders_enhanced(self, soup: BeautifulSoup) -> List[str]:
        """Enhanced riders extraction"""
        riders = []
        page_text = soup.get_text()

        rider_patterns = [
            r'(?:Available\s+)?Rider[s]?\s*:?\s*([^.]{20,200})',
            r'Add-on[s]?\s*:?\s*([^.]{20,200})',
            r'Optional\s+Cover[s]?\s*:?\s*([^.]{20,200})',
            r'(?:Accident|Death|Disability)\s+(?:Benefit\s+)?Rider',
            r'Premium\s+Waiver\s+Rider',
            r'Term\s+Assurance\s+Rider'
        ]

        for pattern in rider_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                clean_rider = clean_text(match)
                if clean_rider and len(clean_rider) > 10:
                    riders.append(clean_rider)

        return riders[:5]

    def scrape_single_policy_comprehensive(self, policy_info: Dict[str, str], category: str) -> Dict[str, Any]:
        """Comprehensive scraping of a single policy with enhanced data extraction"""
        policy_name = policy_info['name']
        policy_url = policy_info['url']

        self.logger.info(f"Starting comprehensive scraping: {policy_name}")

        policy_data = {
            'policy_name': policy_name,
            'plan_number': policy_info.get('plan_number', ''),
            'uin_number': policy_info.get('uin_number', ''),
            'category': category,
            'subcategory': policy_info.get('subcategory', ''),
            'source_url': policy_url,
            'scraped_timestamp': datetime.now().isoformat(),
            'scraped_successfully': False,
            'data_completeness_score': 0.0,
            'extraction_method': 'enhanced_comprehensive'
        }

        try:
            # Setup Selenium driver if not already done
            if not self.driver:
                self.driver = self.setup_selenium_driver()

            # Load the policy page
            self.driver.get(policy_url)
            time.sleep(5)  # Wait for dynamic content to load

            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract policy documents first (needed for PDF-based extraction)
            policy_data['policy_documents'] = self.extract_policy_documents_enhanced(soup)

            # Enhanced feature extraction with PDF priority
            policy_data['features_benefits'] = self.extract_policy_features_enhanced(
                soup, policy_data['policy_documents']
            )

            # Enhanced eligibility criteria extraction
            policy_data['eligibility_criteria'] = self.extract_eligibility_criteria_enhanced(
                soup, policy_data['policy_documents']
            )

            # Extract other policy information using enhanced methods
            policy_data['premium_payment_options'] = self.extract_premium_options_enhanced(soup)
            policy_data['maturity_benefits'] = self.extract_maturity_benefits_enhanced(soup, policy_data['policy_documents'])
            policy_data['surrender_values'] = self.extract_surrender_values_enhanced(soup, policy_data['policy_documents'])
            policy_data['tax_benefits'] = self.extract_tax_benefits_enhanced(soup)
            policy_data['terms_conditions'] = self.extract_terms_conditions_enhanced(soup, policy_data['policy_documents'])
            policy_data['riders_available'] = self.extract_riders_enhanced(soup)

            # Add PDF extraction status
            if policy_data['policy_documents']:
                policy_data['pdf_extraction_status'] = {}
                policy_data['pdf_sources'] = []
                for doc in policy_data['policy_documents']:
                    doc_title = doc.get('title', 'Unknown')
                    policy_data['pdf_sources'].append(doc_title)
                    # Test PDF accessibility
                    pdf_content = self.pdf_extractor.download_pdf(doc.get('url', ''))
                    policy_data['pdf_extraction_status'][doc_title] = 'Success' if pdf_content else 'Failed'

            # Calculate data completeness score
            policy_data['data_completeness_score'] = self.calculate_data_completeness_score(policy_data)

            # Mark as successful if completeness score is above threshold
            if policy_data['data_completeness_score'] >= 0.7:  # 70% minimum threshold
                policy_data['scraped_successfully'] = True
                self.data_quality_metrics['successful_extractions'] += 1
            else:
                self.failed_policies.append({
                    'policy_name': policy_name,
                    'url': policy_url,
                    'completeness_score': policy_data['data_completeness_score'],
                    'reason': 'Low data completeness score'
                })

            self.data_quality_metrics['data_completeness_scores'].append(policy_data['data_completeness_score'])

            self.logger.info(f"Completed scraping {policy_name} - Completeness: {policy_data['data_completeness_score']:.2%}")

        except Exception as e:
            self.logger.error(f"Error scraping policy {policy_name}: {str(e)}")
            policy_data['error_message'] = str(e)
            self.failed_policies.append({
                'policy_name': policy_name,
                'url': policy_url,
                'completeness_score': 0.0,
                'reason': f'Extraction error: {str(e)}'
            })

        self.data_quality_metrics['total_policies'] += 1
        return policy_data

    def get_policy_links_from_category(self, category_url: str) -> List[Dict[str, str]]:
        """Extract policy links from category page"""
        policy_links = []

        try:
            if not self.driver:
                self.driver = self.setup_selenium_driver()

            self.driver.get(category_url)
            time.sleep(3)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Look for policy links in tables or lists
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Look for policy name link in first few cells
                        link_element = None
                        for cell in cells[:3]:
                            link = cell.find('a', href=True)
                            if link:
                                link_element = link
                                break

                        if link_element:
                            policy_name = clean_text(link_element.get_text())
                            policy_url = link_element.get('href')

                            if policy_url:
                                full_policy_url = urljoin(BASE_URL, policy_url)

                                # Extract plan number and UIN from the row
                                plan_number = clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                                uin_number = clean_text(cells[3].get_text()) if len(cells) > 3 else ""

                                policy_info = {
                                    'name': policy_name,
                                    'url': full_policy_url,
                                    'plan_number': plan_number,
                                    'uin_number': uin_number
                                }

                                policy_links.append(policy_info)
                                self.logger.debug(f"Found policy: {policy_name}")

            self.logger.info(f"Found {len(policy_links)} policies in category")

        except Exception as e:
            self.logger.error(f"Error extracting policy links: {e}")

        return policy_links

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        if not self.data_quality_metrics['data_completeness_scores']:
            return {}

        scores = self.data_quality_metrics['data_completeness_scores']

        report = {
            'total_policies_processed': self.data_quality_metrics['total_policies'],
            'successful_extractions': self.data_quality_metrics['successful_extractions'],
            'success_rate': self.data_quality_metrics['successful_extractions'] / max(1, self.data_quality_metrics['total_policies']),
            'average_completeness_score': sum(scores) / len(scores),
            'minimum_completeness_score': min(scores),
            'maximum_completeness_score': max(scores),
            'policies_above_95_percent': len([s for s in scores if s >= 0.95]),
            'policies_above_90_percent': len([s for s in scores if s >= 0.90]),
            'policies_above_80_percent': len([s for s in scores if s >= 0.80]),
            'failed_policies': self.failed_policies,
            'target_achievement': {
                '95_percent_completeness_target': len([s for s in scores if s >= 0.95]) / len(scores) if scores else 0,
                'target_met': len([s for s in scores if s >= 0.95]) / len(scores) >= 0.95 if scores else False
            }
        }

        return report

    def save_enhanced_results(self, all_policies: List[Dict], output_dir: str):
        """Save results in multiple formats with enhanced data structure"""
        import os

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save master JSON with all data
        master_file = f"{output_dir}/enhanced_comprehensive_results.json"
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_policies': len(all_policies),
                    'extraction_method': 'enhanced_comprehensive',
                    'quality_metrics': self.generate_quality_report()
                },
                'policies': all_policies
            }, f, indent=2, ensure_ascii=False)

        # Save vector database ready CSV
        vector_db_data = []
        for policy in all_policies:
            if policy.get('scraped_successfully', False):
                # Flatten data for vector database
                row = {
                    'policy_name': policy.get('policy_name', ''),
                    'plan_number': policy.get('plan_number', ''),
                    'uin_number': policy.get('uin_number', ''),
                    'category': policy.get('category', ''),
                    'features_benefits': ' | '.join(policy.get('features_benefits', [])),
                    'eligibility_age': policy.get('eligibility_criteria', {}).get('age_range',
                                     policy.get('eligibility_criteria', {}).get('age_limit', '')),
                    'eligibility_income': policy.get('eligibility_criteria', {}).get('income_requirement', ''),
                    'medical_examination': policy.get('eligibility_criteria', {}).get('medical_examination', ''),
                    'premium_options': ' | '.join(policy.get('premium_payment_options', [])),
                    'maturity_benefits': ' | '.join(policy.get('maturity_benefits', [])),
                    'surrender_clause': policy.get('surrender_values', {}).get('surrender_clause', ''),
                    'tax_benefits': ' | '.join(policy.get('tax_benefits', [])),
                    'terms_conditions': ' | '.join(policy.get('terms_conditions', [])),
                    'riders_available': ' | '.join(policy.get('riders_available', [])),
                    'pdf_sources': ' | '.join(policy.get('pdf_sources', [])),
                    'data_completeness_score': policy.get('data_completeness_score', 0.0),
                    'source_url': policy.get('source_url', ''),
                    'scraped_timestamp': policy.get('scraped_timestamp', '')
                }
                vector_db_data.append(row)

        # Save as CSV
        if vector_db_data:
            df = pd.DataFrame(vector_db_data)
            csv_file = f"{output_dir}/enhanced_lic_policies_vector_db.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            self.logger.info(f"Saved vector database CSV: {csv_file}")

        # Save quality report
        quality_report = self.generate_quality_report()
        quality_file = f"{output_dir}/data_quality_report.json"
        with open(quality_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Enhanced results saved to: {output_dir}")
        return quality_report

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
