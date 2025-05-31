#!/usr/bin/env python3
"""
PDF Data Extractor for LIC Policies
Extracts detailed policy information from PDF documents
"""

import requests
import PyPDF2
import io
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import logging
from datetime import datetime

from .config import BASE_URL
from .utils import setup_logging, clean_text

class LICPDFExtractor:
    """Extract policy data from LIC PDF documents"""
    
    def __init__(self):
        self.logger = setup_logging("logs/pdf_extractor.log")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF content"""
        try:
            full_url = urljoin(BASE_URL, pdf_url)
            self.logger.info(f"Downloading PDF: {full_url}")
            
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Failed to download PDF {pdf_url}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to extract text from PDF: {e}")
            return ""
    
    def extract_eligibility_from_pdf(self, pdf_text: str) -> Dict[str, str]:
        """Extract eligibility criteria from PDF text"""
        criteria = {}
        
        # Age patterns
        age_patterns = [
            r'(?:Entry|Minimum|Min\.?)\s+Age\s*:?\s*(\d+)\s*(?:years?|yrs?)',
            r'(?:Maximum|Max\.?)\s+Age\s*:?\s*(\d+)\s*(?:years?|yrs?)',
            r'Age\s+(?:Range|Limit)\s*:?\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:to|-|–)\s*(\d+)\s*years?\s+(?:age|old)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    criteria['age_range'] = f"{groups[0]}-{groups[1]} years"
                else:
                    criteria['age_limit'] = f"{groups[0]} years"
                break
        
        # Income patterns
        income_patterns = [
            r'(?:Minimum|Min\.?)\s+(?:Annual\s+)?Income\s*:?\s*Rs\.?\s*([\d,]+)',
            r'Income\s+(?:Requirement|Criteria)\s*:?\s*Rs\.?\s*([\d,]+)'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                criteria['income_requirement'] = f"Rs. {match.group(1)}"
                break
        
        # Medical examination
        if re.search(r'medical\s+examination', pdf_text, re.IGNORECASE):
            criteria['medical_examination'] = 'Required'
        
        return criteria
    
    def extract_maturity_benefits_from_pdf(self, pdf_text: str) -> List[str]:
        """Extract maturity benefits from PDF text"""
        benefits = []
        
        maturity_patterns = [
            r'(?:On\s+)?Maturity\s+Benefit\s*:?\s*([^.]{20,300})',
            r'Maturity\s+Amount\s*:?\s*([^.]{20,300})',
            r'(?:At\s+)?Maturity\s*,?\s*(?:the\s+)?(?:policyholder|you)\s+(?:will\s+)?(?:receive|get)\s*:?\s*([^.]{20,300})',
            r'Sum\s+Assured\s+(?:plus|with|\+)\s+([^.]{20,300})'
        ]
        
        for pattern in maturity_patterns:
            matches = re.findall(pattern, pdf_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_benefit = clean_text(match.strip())
                if clean_benefit and len(clean_benefit) > 20:
                    benefits.append(clean_benefit)
        
        return benefits[:5]
    
    def extract_surrender_values_from_pdf(self, pdf_text: str) -> Dict[str, str]:
        """Extract surrender values from PDF text"""
        surrender_info = {}
        
        surrender_patterns = [
            r'Surrender\s+Value\s*:?\s*([^.]{20,300})',
            r'(?:Cash|Paid-up)\s+Value\s*:?\s*([^.]{20,300})',
            r'(?:If\s+)?(?:you\s+)?surrender\s+(?:the\s+)?policy\s*,?\s*([^.]{20,300})',
            r'Guaranteed\s+Surrender\s+Value\s*:?\s*([^.]{20,300})'
        ]
        
        for pattern in surrender_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE | re.DOTALL)
            if match:
                surrender_info['surrender_clause'] = clean_text(match.group(1))
                break
        
        # Look for surrender period
        period_pattern = r'surrender\s+(?:after|from)\s+(\d+)\s+years?'
        period_match = re.search(period_pattern, pdf_text, re.IGNORECASE)
        if period_match:
            surrender_info['surrender_period'] = f"{period_match.group(1)} years"
        
        return surrender_info
    
    def extract_terms_from_pdf(self, pdf_text: str) -> List[str]:
        """Extract terms and conditions from PDF text"""
        terms = []
        
        terms_patterns = [
            r'Grace\s+Period\s*:?\s*([^.]{10,200})',
            r'Free\s+Look\s+Period\s*:?\s*([^.]{10,200})',
            r'(?:Policy\s+)?Loan\s+(?:Facility|Available)\s*:?\s*([^.]{10,200})',
            r'Death\s+Benefit\s*:?\s*([^.]{10,200})',
            r'Exclusions?\s*:?\s*([^.]{10,200})'
        ]
        
        for pattern in terms_patterns:
            matches = re.findall(pattern, pdf_text, re.IGNORECASE)
            for match in matches:
                clean_term = clean_text(match)
                if clean_term and len(clean_term) > 10:
                    terms.append(clean_term)
        
        return terms[:8]
    
    def extract_features_from_pdf(self, pdf_text: str) -> List[str]:
        """Extract policy features from PDF text"""
        features = []
        
        # Look for bullet points and features
        feature_patterns = [
            r'•\s*([^•\n]{20,200})',
            r'✓\s*([^✓\n]{20,200})',
            r'(?:Feature|Benefit)\s*:?\s*([^.\n]{20,200})',
            r'(?:Key\s+)?(?:Features?|Benefits?)\s*:?\s*([^.\n]{20,200})'
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, pdf_text, re.IGNORECASE)
            for match in matches:
                clean_feature = clean_text(match)
                if clean_feature and len(clean_feature) > 20:
                    features.append(clean_feature)
        
        return features[:10]
    
    def extract_policy_data_from_pdfs(self, pdf_urls: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract comprehensive policy data from multiple PDFs"""
        extracted_data = {
            'eligibility_criteria': {},
            'maturity_benefits': [],
            'surrender_values': {},
            'terms_conditions': [],
            'features_benefits_pdf': [],
            'pdf_extraction_status': {}
        }
        
        for pdf_info in pdf_urls:
            pdf_url = pdf_info.get('url', '')
            pdf_title = pdf_info.get('title', 'Unknown')
            
            self.logger.info(f"Processing PDF: {pdf_title}")
            
            # Download PDF
            pdf_content = self.download_pdf(pdf_url)
            if not pdf_content:
                extracted_data['pdf_extraction_status'][pdf_title] = 'Download failed'
                continue
            
            # Extract text
            pdf_text = self.extract_text_from_pdf(pdf_content)
            if not pdf_text:
                extracted_data['pdf_extraction_status'][pdf_title] = 'Text extraction failed'
                continue
            
            extracted_data['pdf_extraction_status'][pdf_title] = 'Success'
            
            # Extract different types of data
            if 'brochure' in pdf_title.lower() or 'sales' in pdf_title.lower():
                # Sales brochures usually have features and benefits
                features = self.extract_features_from_pdf(pdf_text)
                extracted_data['features_benefits_pdf'].extend(features)
                
                eligibility = self.extract_eligibility_from_pdf(pdf_text)
                extracted_data['eligibility_criteria'].update(eligibility)
            
            elif 'policy document' in pdf_title.lower() or 'policy doc' in pdf_title.lower():
                # Policy documents have detailed terms and conditions
                terms = self.extract_terms_from_pdf(pdf_text)
                extracted_data['terms_conditions'].extend(terms)
                
                surrender = self.extract_surrender_values_from_pdf(pdf_text)
                extracted_data['surrender_values'].update(surrender)
                
                maturity = self.extract_maturity_benefits_from_pdf(pdf_text)
                extracted_data['maturity_benefits'].extend(maturity)
            
            elif 'cis' in pdf_title.lower():
                # Customer Information Sheet - usually has key features
                features = self.extract_features_from_pdf(pdf_text)
                extracted_data['features_benefits_pdf'].extend(features)
                
                eligibility = self.extract_eligibility_from_pdf(pdf_text)
                extracted_data['eligibility_criteria'].update(eligibility)
        
        # Remove duplicates
        extracted_data['features_benefits_pdf'] = list(set(extracted_data['features_benefits_pdf']))
        extracted_data['maturity_benefits'] = list(set(extracted_data['maturity_benefits']))
        extracted_data['terms_conditions'] = list(set(extracted_data['terms_conditions']))
        
        return extracted_data

def test_pdf_extraction():
    """Test PDF extraction on a sample policy"""
    print("🧪 Testing PDF Extraction...")
    
    # Sample PDF URLs from LIC's New Endowment Plan
    sample_pdfs = [
        {
            'title': 'Sales brochure (Content is in English)',
            'url': '/documents/20121/1248951/Lic+NEW+ENDOWMENT+PLAN+2024++4x9+inches+wxh+single+pages.pdf+-8th+cut+Final+-+24.10.24.pdf/8bfc1204-31c9-4dbd-95c0-0991a1c7a392?t=1729776062988'
        },
        {
            'title': 'Policy Document (Content is in English)',
            'url': '/documents/20121/1243952/Final+Policy+doc_LIC%27s+New+Endowment_V03_website.pdf/46cf5516-ccb5-70ba-b28d-c7480959af13?t=1728039920686'
        }
    ]
    
    extractor = LICPDFExtractor()
    result = extractor.extract_policy_data_from_pdfs(sample_pdfs)
    
    print("📊 PDF Extraction Results:")
    print(f"✅ Eligibility criteria: {len(result['eligibility_criteria'])} items")
    print(f"✅ Maturity benefits: {len(result['maturity_benefits'])} items")
    print(f"✅ Surrender values: {len(result['surrender_values'])} items")
    print(f"✅ Terms & conditions: {len(result['terms_conditions'])} items")
    print(f"✅ Features from PDF: {len(result['features_benefits_pdf'])} items")
    
    print(f"\n📋 PDF Processing Status:")
    for pdf, status in result['pdf_extraction_status'].items():
        print(f"  {pdf}: {status}")
    
    # Save results
    import json
    with open('pdf_extraction_test.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: pdf_extraction_test.json")

if __name__ == "__main__":
    test_pdf_extraction()
