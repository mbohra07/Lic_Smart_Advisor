"""
Dashboard Recommendation Engine
Enhanced RAG integration for personalized policy recommendations
"""

import sys
import os
import streamlit as st
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vector_db.mongodb_vector_knowledge_base import LICVectorKnowledgeBase, LICRAGQueryEngine
from .config import DashboardConfig
from .sales_agent import LICGeniusSalesAgent

class DashboardRecommendationEngine:
    """Enhanced recommendation engine for the dashboard"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.kb = None
        self.rag_engine = None
        self.sales_agent = LICGeniusSalesAgent()
        self._initialize_rag_system()
    
    def _initialize_rag_system(self):
        """Initialize the RAG system with MongoDB connection"""
        try:
            with st.spinner("🔗 Connecting to LIC Knowledge Base..."):
                self.kb = LICVectorKnowledgeBase(self.config.MONGODB_URI)
                
                if self.kb.connect_to_mongodb():
                    self.rag_engine = LICRAGQueryEngine(self.kb)
                    st.success("✅ Connected to LIC Knowledge Base successfully!")
                else:
                    st.error("❌ Failed to connect to LIC Knowledge Base")
                    
        except Exception as e:
            st.error(f"❌ Error initializing RAG system: {str(e)}")
    
    def get_personalized_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized policy recommendations with sales pitch
        """
        if not self.rag_engine:
            return {
                'success': False,
                'error': 'RAG system not available',
                'recommendations': [],
                'sales_pitch': ''
            }
        
        try:
            with st.spinner("🤖 AI is analyzing 37+ LIC policies for your perfect match..."):
                # Get recommendations from RAG engine
                recommendations = self.rag_engine.get_policy_recommendations(user_profile)
                
                if not recommendations:
                    return {
                        'success': False,
                        'error': 'No suitable policies found',
                        'recommendations': [],
                        'sales_pitch': ''
                    }
                
                # Enhance recommendations with additional insights
                enhanced_recommendations = self._enhance_recommendations(recommendations, user_profile)
                
                # Generate personalized sales pitch
                with st.spinner("✍️ Generating your personalized sales presentation..."):
                    sales_pitch = self.sales_agent.generate_personalized_sales_pitch(
                        user_profile, enhanced_recommendations
                    )
                
                return {
                    'success': True,
                    'recommendations': enhanced_recommendations,
                    'sales_pitch': sales_pitch,
                    'user_profile': user_profile,
                    'total_policies_analyzed': 37,
                    'recommendation_confidence': self._calculate_overall_confidence(enhanced_recommendations)
                }
                
        except Exception as e:
            st.error(f"❌ Error getting recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': [],
                'sales_pitch': ''
            }
    
    def display_recommendations(self, recommendation_data: Dict[str, Any]):
        """Display recommendations in an attractive format"""
        if not recommendation_data.get('success'):
            st.error(f"❌ {recommendation_data.get('error', 'Unknown error')}")
            return
        
        recommendations = recommendation_data['recommendations']
        user_profile = recommendation_data['user_profile']
        
        # Header with personalized message
        self._display_personalized_header(user_profile, recommendation_data)
        
        # Primary recommendation (Hero section)
        if recommendations:
            self._display_primary_recommendation(recommendations[0], user_profile)
            
            # Alternative recommendations
            if len(recommendations) > 1:
                self._display_alternative_recommendations(recommendations[1:], user_profile)
            
            # Sales pitch section
            self._display_sales_pitch(recommendation_data['sales_pitch'])
    
    def _enhance_recommendations(self, recommendations: List[Dict], user_profile: Dict[str, Any]) -> List[Dict]:
        """Enhance recommendations with additional insights"""
        enhanced = []
        
        for rec in recommendations:
            # Calculate personalized metrics
            monthly_income = user_profile.get('monthly_income', 50000)
            age = user_profile.get('age', 35)
            
            # Estimate premium based on age and income
            estimated_premium = self._estimate_premium(monthly_income, age, rec)
            
            # Calculate affordability score
            affordability_score = self._calculate_affordability_score(estimated_premium, monthly_income)
            
            # Add enhancement data
            rec['enhanced_data'] = {
                'estimated_monthly_premium': estimated_premium,
                'affordability_score': affordability_score,
                'premium_to_income_ratio': (estimated_premium * 12) / (monthly_income * 12) * 100,
                'personalized_benefits': self._get_personalized_benefits(rec, user_profile),
                'risk_alignment': self._calculate_risk_alignment(rec, user_profile),
                'goal_alignment': self._calculate_goal_alignment(rec, user_profile)
            }
            
            enhanced.append(rec)
        
        return enhanced
    
    def _display_personalized_header(self, user_profile: Dict[str, Any], recommendation_data: Dict[str, Any]):
        """Display personalized header message"""
        age = user_profile.get('age')
        income = user_profile.get('monthly_income', 0)
        goal = user_profile.get('primary_goal', '')
        total_analyzed = recommendation_data.get('total_policies_analyzed', 37)
        confidence = recommendation_data.get('recommendation_confidence', 85)
        
        goal_display = self.config.get_goal_info(goal).get('display_name', goal)
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #FF6B35, #004E89); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
            <h2>🙏 Namaste! Your Personalized LIC Recommendations</h2>
            <p style="font-size: 18px; margin: 10px 0;">
                Based on your profile (Age: {age}, Income: ₹{income:,}, Goal: {goal_display}), 
                we've analyzed <strong>{total_analyzed}+ LIC policies</strong> to find your perfect match.
            </p>
            <p style="font-size: 16px; margin: 5px 0;">
                <strong>Recommendation Confidence: {confidence}%</strong> ✨
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _display_primary_recommendation(self, primary_rec: Dict[str, Any], user_profile: Dict[str, Any]):
        """Display the primary recommendation as hero section"""
        st.markdown("## 🎯 Your Perfect Policy Match")
        
        policy_name = primary_rec.get('policy_metadata', {}).get('policy_name', 'Premium Policy')
        category = primary_rec.get('policy_metadata', {}).get('category', 'Comprehensive')
        score = primary_rec.get('recommendation_score', 85)
        enhanced_data = primary_rec.get('enhanced_data', {})
        
        # Main recommendation card
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #28A745;">
                <h3 style="color: #28A745; margin-top: 0;">🏆 {policy_name}</h3>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Match Score:</strong> {score:.1f}/100 🎯</p>
                <p><strong>Estimated Monthly Premium:</strong> ₹{enhanced_data.get('estimated_monthly_premium', 0):,.0f}</p>
                <p><strong>Affordability:</strong> {enhanced_data.get('affordability_score', 'Good')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Confidence gauge
            self._display_confidence_gauge(score)
        
        # Key benefits
        st.markdown("### 🌟 Why This is Perfect for You")
        benefits = enhanced_data.get('personalized_benefits', [])
        if benefits:
            for benefit in benefits[:3]:  # Top 3 benefits
                st.markdown(f"✅ {benefit}")
        
        # Features
        features = primary_rec.get('features_benefits', '')
        if features:
            with st.expander("📋 Complete Policy Features"):
                st.markdown(features)
    
    def _display_alternative_recommendations(self, alternatives: List[Dict[str, Any]], user_profile: Dict[str, Any]):
        """Display alternative recommendations"""
        st.markdown("## 🔄 Alternative Options")
        st.markdown("*Other excellent policies that match your profile*")
        
        cols = st.columns(min(len(alternatives), 3))
        
        for i, alt in enumerate(alternatives[:3]):
            with cols[i]:
                policy_name = alt.get('policy_metadata', {}).get('policy_name', f'Policy {i+2}')
                category = alt.get('policy_metadata', {}).get('category', 'Comprehensive')
                score = alt.get('recommendation_score', 75)
                enhanced_data = alt.get('enhanced_data', {})
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">
                    <h4 style="margin-top: 0;">{policy_name}</h4>
                    <p><strong>Score:</strong> {score:.1f}/100</p>
                    <p><strong>Premium:</strong> ₹{enhanced_data.get('estimated_monthly_premium', 0):,.0f}/month</p>
                    <p><strong>Category:</strong> {category}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def _display_sales_pitch(self, sales_pitch: str):
        """Display the AI-generated sales pitch"""
        st.markdown("## 💬 Expert Analysis & Recommendation")
        st.markdown("*Personalized insights from India's #1 LIC Expert*")
        
        # Replace newlines with <br> before using in f-string
        formatted_pitch = sales_pitch.replace('\n', '<br>')
        
        # Display sales pitch in an attractive format
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;">
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px;">
                {formatted_pitch}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _display_confidence_gauge(self, score: float):
        """Display confidence gauge"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Match Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#28A745"},
                'steps': [
                    {'range': [0, 50], 'color': "#DC3545"},
                    {'range': [50, 75], 'color': "#FFC107"},
                    {'range': [75, 100], 'color': "#28A745"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
    
    def _estimate_premium(self, monthly_income: int, age: int, recommendation: Dict[str, Any]) -> float:
        """Estimate premium based on income and age"""
        # Base premium as percentage of income (10-20%)
        base_premium_annual = monthly_income * 12 * 0.15
        
        # Age factor (younger = lower premium for term, higher for investment)
        age_factor = 1.0 + (age - 30) * 0.01
        
        # Policy type factor (simplified)
        category = recommendation.get('policy_metadata', {}).get('category', '').lower()
        if 'term' in category:
            category_factor = 0.3  # Term insurance is cheaper
        elif 'ulip' in category or 'investment' in category:
            category_factor = 1.2  # Investment plans cost more
        else:
            category_factor = 1.0  # Standard endowment
        
        estimated_annual = base_premium_annual * age_factor * category_factor
        return estimated_annual / 12  # Return monthly premium
    
    def _calculate_affordability_score(self, premium: float, monthly_income: int) -> str:
        """Calculate affordability score"""
        ratio = (premium / monthly_income) * 100
        
        if ratio <= 10:
            return "Excellent"
        elif ratio <= 15:
            return "Good"
        elif ratio <= 20:
            return "Moderate"
        else:
            return "High"
    
    def _get_personalized_benefits(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Get personalized benefits based on user profile"""
        benefits = []
        
        goal = user_profile.get('primary_goal', '')
        life_stage = user_profile.get('life_stage', '')
        risk_comfort = user_profile.get('risk_comfort', '')
        
        # Goal-based benefits
        if goal == 'child_education':
            benefits.append("Perfect for securing your child's educational future")
        elif goal == 'retirement_planning':
            benefits.append("Builds substantial retirement corpus with guaranteed returns")
        elif goal == 'wealth_creation':
            benefits.append("High growth potential with market-linked returns")
        
        # Life stage benefits
        if 'young' in life_stage.lower():
            benefits.append("Flexible premium payment options for growing careers")
        elif 'family' in life_stage.lower():
            benefits.append("Comprehensive family protection with multiple benefits")
        
        # Risk-based benefits
        if risk_comfort == 'conservative':
            benefits.append("Guaranteed returns with capital protection")
        elif risk_comfort == 'aggressive':
            benefits.append("High growth potential with equity exposure")
        
        return benefits
    
    def _calculate_risk_alignment(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate how well the policy aligns with user's risk profile"""
        # Simplified risk alignment calculation
        return 85.0  # Placeholder
    
    def _calculate_goal_alignment(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate how well the policy aligns with user's goals"""
        # Simplified goal alignment calculation
        return 90.0  # Placeholder
    
    def _calculate_overall_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate overall recommendation confidence"""
        if not recommendations:
            return 0.0
        
        scores = [rec.get('recommendation_score', 0) for rec in recommendations]
        return max(scores) if scores else 0.0
    
    def close_connection(self):
        """Close database connection"""
        if self.kb:
            self.kb.close_connection()
