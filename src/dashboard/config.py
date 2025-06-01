"""
Dashboard Configuration
Centralized configuration for the LIC Policy Recommendation Dashboard
"""

import os
from typing import Dict, List, Any

class DashboardConfig:
    """Configuration class for the dashboard"""
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    DATABASE_NAME: str = "lic_knowledge_base"
    POLICIES_COLLECTION: str = "policy_vectors"
    CHAT_COLLECTION: str = "chat_sessions"
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "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")
    GROQ_MODEL: str = "llama-3.1-8b-instant"  # Fast and efficient model for sales agent
    
    # Google Search API (for market intelligence)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")
    
    # Dashboard Settings
    PAGE_TITLE: str = "🏛️ LIC Policy Advisor - AI-Powered Recommendations"
    PAGE_ICON: str = "🏛️"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"
    
    # User Profile Configuration
    AGE_RANGE: tuple = (25, 65)
    INCOME_RANGE: tuple = (20000, 500000)
    MAX_DEPENDENTS: int = 10
    
    # Recommendation Settings
    MAX_RECOMMENDATIONS: int = 5
    MIN_SIMILARITY_SCORE: float = 0.6
    VECTOR_SEARCH_CANDIDATES: int = 100
    
    # Sales Agent Configuration
    AGENT_NAME: str = "Suresh Kumar"
    AGENT_CREDENTIALS: str = "LIC Policy Advisor"
    
    # Chat Configuration
    MAX_CHAT_HISTORY: int = 50
    TYPING_DELAY: float = 1.5
    RESPONSE_TIMEOUT: int = 30
    
    # UI Configuration
    PRIMARY_COLOR: str = "#FF6B35"
    SECONDARY_COLOR: str = "#004E89"
    SUCCESS_COLOR: str = "#28A745"
    WARNING_COLOR: str = "#FFC107"
    DANGER_COLOR: str = "#DC3545"
    
    # Life Stage Configurations
    LIFE_STAGES: Dict[str, Dict[str, Any]] = {
        "Single Professional": {
            "icon": "🌱",
            "description": "Early Career - Focus on wealth creation and tax savings",
            "typical_goals": ["wealth_creation", "tax_optimization"],
            "recommended_coverage": "5-8x annual income",
            "priority_features": ["high returns", "flexibility", "tax benefits"]
        },
        "Married (No Children)": {
            "icon": "💑",
            "description": "Building Together - Joint financial planning and security",
            "typical_goals": ["wealth_creation", "family_protection"],
            "recommended_coverage": "8-10x annual income",
            "priority_features": ["joint coverage", "wealth building", "flexibility"]
        },
        "Young Family (Kids <10)": {
            "icon": "👨‍👩‍👧‍👦",
            "description": "Growing Family - Child education and family protection",
            "typical_goals": ["child_education", "family_protection"],
            "recommended_coverage": "10-15x annual income",
            "priority_features": ["education planning", "high coverage", "guaranteed benefits"]
        },
        "Established Family (Kids 10+)": {
            "icon": "🏠",
            "description": "Stability Phase - Education funding and retirement planning",
            "typical_goals": ["child_education", "retirement_planning"],
            "recommended_coverage": "8-12x annual income",
            "priority_features": ["education corpus", "retirement planning", "wealth transfer"]
        },
        "Pre-Retirement (50+)": {
            "icon": "🌅",
            "description": "Golden Years Prep - Retirement corpus and legacy planning",
            "typical_goals": ["retirement_planning", "legacy_planning"],
            "recommended_coverage": "5-8x annual income",
            "priority_features": ["guaranteed income", "legacy planning", "health coverage"]
        }
    }
    
    # Financial Goals Configuration
    FINANCIAL_GOALS: Dict[str, Dict[str, Any]] = {
        "wealth_creation": {
            "display_name": "Wealth Creation & Growth",
            "icon": "📈",
            "description": "Build long-term wealth with market-linked returns",
            "expected_returns": "12-15%",
            "risk_level": "Moderate to High",
            "tax_benefits": "Section 80C + 10(10D)",
            "suitable_policies": ["ULIP", "Endowment", "Money Back"]
        },
        "child_education": {
            "display_name": "Child's Education Fund",
            "icon": "🎓",
            "description": "Secure your child's educational future",
            "expected_returns": "8-12%",
            "risk_level": "Low to Moderate",
            "tax_benefits": "Section 80C + Tax-free maturity",
            "suitable_policies": ["Child Plans", "Endowment", "ULIP"]
        },
        "retirement_planning": {
            "display_name": "Retirement Planning",
            "icon": "🏖️",
            "description": "Build a comfortable retirement corpus",
            "expected_returns": "10-14%",
            "risk_level": "Moderate",
            "tax_benefits": "Section 80C + Pension benefits",
            "suitable_policies": ["Pension Plans", "Annuity", "Endowment"]
        },
        "family_protection": {
            "display_name": "Family Protection & Security",
            "icon": "🛡️",
            "description": "Comprehensive protection for your family",
            "expected_returns": "Guaranteed benefits",
            "risk_level": "Very Low",
            "tax_benefits": "Section 80C + 10(10D)",
            "suitable_policies": ["Term Plans", "Whole Life", "Endowment"]
        },
        "tax_optimization": {
            "display_name": "Tax Optimization",
            "icon": "💰",
            "description": "Maximize tax savings while building wealth",
            "expected_returns": "8-12%",
            "risk_level": "Low to Moderate",
            "tax_benefits": "Section 80C + 10(10D) + ELSS",
            "suitable_policies": ["ELSS", "Endowment", "ULIP"]
        },
        "legacy_planning": {
            "display_name": "Legacy & Estate Planning",
            "icon": "🏛️",
            "description": "Transfer wealth to next generation efficiently",
            "expected_returns": "Guaranteed + Bonus",
            "risk_level": "Very Low",
            "tax_benefits": "Estate planning benefits",
            "suitable_policies": ["Whole Life", "Endowment", "Legacy Plans"]
        }
    }
    
    # Risk Profiles
    RISK_PROFILES: Dict[str, Dict[str, Any]] = {
        "conservative": {
            "display_name": "Conservative",
            "icon": "🛡️",
            "description": "I prefer guaranteed returns and capital protection",
            "expected_returns": "6-8%",
            "risk_tolerance": "Very Low",
            "suitable_products": ["Traditional Plans", "Guaranteed Returns", "Fixed Deposits"]
        },
        "moderate": {
            "display_name": "Moderate", 
            "icon": "⚖️",
            "description": "I'm comfortable with some risk for better returns",
            "expected_returns": "8-12%",
            "risk_tolerance": "Medium",
            "suitable_products": ["Balanced Funds", "Hybrid Plans", "Moderate ULIP"]
        },
        "aggressive": {
            "display_name": "Aggressive",
            "icon": "🚀", 
            "description": "I'm willing to take higher risks for maximum growth",
            "expected_returns": "12-18%",
            "risk_tolerance": "High",
            "suitable_products": ["Equity ULIP", "Market-Linked", "Growth Funds"]
        }
    }
    
    # Decision Making Styles
    DECISION_STYLES: Dict[str, Dict[str, Any]] = {
        "quick_decider": {
            "display_name": "Quick Decider",
            "icon": "⚡",
            "description": "I trust my instincts and decide fast",
            "communication_style": "Direct, benefit-focused approach",
            "sales_approach": "Highlight key benefits, create urgency, quick close"
        },
        "research_heavy": {
            "display_name": "Research Heavy",
            "icon": "📊",
            "description": "I need detailed analysis before deciding",
            "communication_style": "Data-driven, comprehensive comparisons",
            "sales_approach": "Detailed analysis, comparisons, technical details"
        },
        "seeks_validation": {
            "display_name": "Seeks Validation",
            "icon": "👥",
            "description": "I prefer expert opinions and social proof",
            "communication_style": "Testimonials, expert endorsements",
            "sales_approach": "Social proof, expert opinions, success stories"
        },
        "price_sensitive": {
            "display_name": "Price Sensitive",
            "icon": "💵",
            "description": "Cost-effectiveness is my top priority",
            "communication_style": "Value propositions, cost breakdowns",
            "sales_approach": "ROI focus, cost comparisons, value demonstration"
        }
    }
    
    # Purchase Timeline Configuration
    PURCHASE_TIMELINES: Dict[str, Dict[str, Any]] = {
        "immediate": {
            "display_name": "Need Immediately",
            "urgency_level": "High",
            "incentives": ["Same-day processing", "Immediate tax benefits", "Quick approval"],
            "sales_message": "Act now to secure immediate benefits!"
        },
        "within_3_months": {
            "display_name": "Within 3 Months", 
            "urgency_level": "Medium",
            "incentives": ["Quarterly tax planning", "Rate lock benefits", "Early bird offers"],
            "sales_message": "Perfect timing for quarterly financial planning!"
        },
        "within_year": {
            "display_name": "Within This Year",
            "urgency_level": "Medium",
            "incentives": ["Annual tax savings", "Year-end benefits", "Policy rate locks"],
            "sales_message": "Maximize your annual tax savings!"
        },
        "exploring": {
            "display_name": "Just Exploring Options",
            "urgency_level": "Low", 
            "incentives": ["Educational resources", "Free consultations", "No pressure guidance"],
            "sales_message": "Let's explore the best options for your future!"
        }
    }

    @classmethod
    def get_life_stage_info(cls, life_stage: str) -> Dict[str, Any]:
        """Get information about a specific life stage"""
        return cls.LIFE_STAGES.get(life_stage, {})
    
    @classmethod
    def get_goal_info(cls, goal: str) -> Dict[str, Any]:
        """Get information about a specific financial goal"""
        return cls.FINANCIAL_GOALS.get(goal, {})
    
    @classmethod
    def get_risk_profile_info(cls, risk_profile: str) -> Dict[str, Any]:
        """Get information about a specific risk profile"""
        return cls.RISK_PROFILES.get(risk_profile, {})
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        required_env_vars = ["GROQ_API_KEY"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            return False
        
        return True
