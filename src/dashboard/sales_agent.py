"""
LIC Genius Sales Agent
World's smartest LIC policy sales agent powered by Groq LLM
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from groq import Groq
import streamlit as st
from .config import DashboardConfig
from .web_search import WebSearchManager

class LICGeniusSalesAgent:
    """
    Knowledgeable LIC policy advisor powered by Groq LLM
    Dedicated to helping families find the right insurance solutions
    """
    
    def __init__(self):
        self.config = DashboardConfig()
        self.groq_client = self._initialize_groq_client()
        self.agent_persona = self._create_agent_persona()
        self.web_search = WebSearchManager()
        
    def _initialize_groq_client(self) -> Optional[Groq]:
        """Initialize Groq client"""
        try:
            api_key = self.config.GROQ_API_KEY
            if not api_key:
                st.error("🚨 Groq API key not found. Please set GROQ_API_KEY environment variable.")
                return None

            return Groq(api_key=api_key)
        except Exception as e:
            st.error(f"❌ Failed to initialize Groq client: {str(e)}")
            return None
    
    def _create_agent_persona(self) -> str:
        """Create a knowledgeable and versatile agent persona"""
        return """You are Suresh Kumar, a highly knowledgeable LIC policy advisor with expertise in both insurance and general knowledge.

KEY TRAITS:
1. Direct & Informative: Always provide clear, accurate answers to ANY question asked, using real-time web search data when needed.
2. Naturally Transitional: After answering the primary question, smoothly connect it to relevant insurance concepts when appropriate.
3. Authentically Helpful: Focus on being genuinely helpful first, sales-oriented second.
4. Data-Driven: Use both real-time web search data and structured policy knowledge to provide comprehensive answers.

RESPONSE STRUCTURE:
1. Direct Answer: Begin with a clear, direct answer to the user's question, regardless of topic
2. Supporting Details: Provide relevant context or data from web searches
3. Natural Bridge: IF APPROPRIATE, create a natural connection to insurance/financial planning
4. Insurance Insight: Share relevant policy information only if the connection feels natural

EXAMPLES:
- Weather Question: "It's currently 25°C with clear skies in [location]. Speaking of planning ahead, just as weather forecasts help us prepare for the day, proper insurance planning helps us prepare for life's uncertainties..."
- Market Question: "The Sensex is currently at 65,000, showing a 2% increase. This market growth actually relates to how LIC's market-linked policies can help capture such positive market movements while providing protection..."
- General Question: Always answer directly first, then find natural connections to financial planning if relevant.

TONE:
- Professional yet conversational
- Informative without being overwhelming
- Naturally flowing rather than forced transitions
- Empathetic and understanding

Remember: Your primary goal is to be genuinely helpful. Sales should be secondary and only introduced when there's a natural connection to the topic at hand."""
    
    def generate_personalized_sales_pitch(
        self, 
        user_profile: Dict[str, Any], 
        recommended_policies: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a highly personalized sales pitch based on user profile and recommendations
        """
        if not self.groq_client:
            return "❌ Sales agent unavailable. Please check configuration."
        
        try:
            # Prepare context for the sales agent
            context = self._prepare_sales_context(user_profile, recommended_policies)
            
            # Get real-time market insights and policy information
            web_context = self._get_sales_web_context(context['primary_recommendation']['policy_name'])
            
            # Create the sales pitch prompt
            prompt = self._create_sales_pitch_prompt(context, web_context)
            
            # Generate sales pitch using Groq
            response = self.groq_client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.agent_persona},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent, focused output
                max_tokens=1500,  # Reduced to encourage conciseness
                top_p=0.8
            )
            
            sales_pitch = response.choices[0].message.content
            
            # Add agent signature
            sales_pitch += f"\n\n---\n**{self.config.AGENT_NAME}**  \n*{self.config.AGENT_CREDENTIALS}*"
            
            return sales_pitch
            
        except Exception as e:
            st.error(f"❌ Error generating sales pitch: {str(e)}")
            return "❌ Unable to generate personalized sales pitch at this time."
    
    def generate_objection_response(
        self, 
        user_profile: Dict[str, Any], 
        objection: str, 
        recommended_policies: List[Dict[str, Any]],
        market_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate intelligent objection handling response with market context
        """
        if not self.groq_client:
            return "❌ Sales agent unavailable. Please check configuration."
        
        try:
            context = self._prepare_sales_context(user_profile, recommended_policies)
            
            # Get additional real-time context if not provided
            if not market_context:
                policy_name = context['primary_recommendation']['policy_name']
                market_context = self.web_search.get_market_insights(policy_name)
            
            prompt = f"""
CUSTOMER OBJECTION HANDLING SCENARIO:

Customer Profile: {json.dumps(context['customer_summary'], indent=2)}
Recommended Policy: {context['primary_recommendation']}
Customer Objection: "{objection}"

Market Context:
{json.dumps(market_context, indent=2)}

As a knowledgeable LIC policy advisor, provide a thoughtful objection handling response that:

1. ACKNOWLEDGES the concern with empathy and understanding
2. ADDRESSES the objection with specific data, calculations, and logic
3. REDIRECTS to the value proposition with compelling benefits
4. PROVIDES relevant market insights and comparisons
5. OFFERS alternative solutions or compromises if appropriate
6. ENDS with a soft but confident next step

Handle this objection professionally while maintaining trust and moving toward a positive outcome.

Response should be conversational, culturally appropriate, and include specific numbers/calculations where relevant.
"""
            
            response = self.groq_client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.agent_persona},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500,
                top_p=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"❌ Error handling objection: {str(e)}")
            return "❌ Unable to process your concern at this time."
    
    def generate_follow_up_message(
        self, 
        user_profile: Dict[str, Any], 
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Generate intelligent follow-up message based on conversation
        """
        if not self.groq_client:
            return "❌ Sales agent unavailable."
        
        try:
            # Analyze conversation sentiment and stage
            conversation_summary = self._analyze_conversation(conversation_history)
            
            prompt = f"""
FOLLOW-UP MESSAGE GENERATION:

Customer Profile: {json.dumps(user_profile, indent=2)}
Conversation Summary: {conversation_summary}

Based on the conversation flow and customer engagement, generate an appropriate follow-up message that:

1. References specific points from our previous discussion
2. Provides additional value or insights
3. Addresses any remaining concerns
4. Moves the conversation forward naturally
5. Maintains the relationship even if not ready to buy

The message should feel personal, helpful, and non-pushy while demonstrating your expertise.
"""
            
            response = self.groq_client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.agent_persona},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return "Thank you for your time today. I'm here whenever you're ready to discuss your financial security further."
    
    def _prepare_sales_context(
        self,
        user_profile: Dict[str, Any],
        recommended_policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare comprehensive context for sales pitch generation"""

        # Get primary recommendation and validate appropriateness
        primary_policy = recommended_policies[0] if recommended_policies else {}
        validated_policy = self._validate_policy_appropriateness(primary_policy, user_profile)

        # Calculate financial projections with mathematical consistency
        monthly_income = user_profile.get('monthly_income', 50000)
        age = user_profile.get('age', 35)

        # Suggested premium (10-15% of annual income based on age and dependents)
        dependents = user_profile.get('dependents', 0)
        premium_percentage = 0.10 + (dependents * 0.02) + (max(0, age - 30) * 0.001)  # 10-15% range
        premium_percentage = min(premium_percentage, 0.15)  # Cap at 15%

        suggested_annual_premium = monthly_income * 12 * premium_percentage
        suggested_monthly_premium = suggested_annual_premium / 12
        suggested_daily_premium = suggested_annual_premium / 365  # Consistent daily calculation

        # Life cover calculation
        recommended_cover = monthly_income * 12 * (8 + dependents * 2)  # More realistic multiplier
        
        context = {
            'customer_summary': {
                'age': age,
                'monthly_income': monthly_income,
                'annual_income': monthly_income * 12,
                'life_stage': user_profile.get('life_stage'),
                'dependents': dependents,
                'primary_goal': user_profile.get('primary_goal'),
                'risk_comfort': user_profile.get('risk_comfort'),
                'decision_style': user_profile.get('decision_style'),
                'timeline': user_profile.get('timeline')
            },
            'financial_projections': {
                'suggested_monthly_premium': round(suggested_monthly_premium, 0),
                'suggested_annual_premium': round(suggested_annual_premium, 0),
                'suggested_daily_premium': round(suggested_daily_premium, 0),
                'recommended_life_cover': recommended_cover,
                'premium_percentage': round(premium_percentage * 100, 1)
            },
            'primary_recommendation': {
                'policy_name': primary_policy.get('policy_metadata', {}).get('policy_name', 'Premium Policy'),
                'category': primary_policy.get('policy_metadata', {}).get('category', 'Comprehensive'),
                'features': primary_policy.get('features_benefits', 'Comprehensive benefits'),
                'recommendation_score': primary_policy.get('recommendation_score', 85)
            },
            'alternative_recommendations': [
                {
                    'policy_name': policy.get('policy_metadata', {}).get('policy_name', ''),
                    'category': policy.get('policy_metadata', {}).get('category', ''),
                    'score': policy.get('recommendation_score', 0)
                }
                for policy in recommended_policies[1:3]  # Top 2 alternatives
            ]
        }
        
        return context

    def _validate_policy_appropriateness(self, policy: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if the recommended policy is appropriate for the customer profile"""
        policy_name = policy.get('policy_metadata', {}).get('policy_name', '').lower()
        life_stage = user_profile.get('life_stage', '').lower()
        dependents = user_profile.get('dependents', 0)

        # Flag inappropriate recommendations
        inappropriate_flags = []

        # Check for children's plans for people without children
        if 'children' in policy_name or 'child' in policy_name:
            if dependents == 0 or 'single' in life_stage:
                inappropriate_flags.append("children_plan_without_children")

        # Check for pension plans for very young people
        if 'pension' in policy_name or 'retirement' in policy_name:
            age = user_profile.get('age', 35)
            if age < 25:
                inappropriate_flags.append("pension_plan_too_young")

        return {
            'policy': policy,
            'inappropriate_flags': inappropriate_flags,
            'is_appropriate': len(inappropriate_flags) == 0
        }

    def _get_sales_web_context(self, policy_name: str) -> Dict[str, Any]:
        """Get real-time web context for sales pitch"""
        # Get market insights
        market_insights = self.web_search.get_market_insights(policy_name)
        
        # Get policy comparisons
        comparisons = self.web_search.get_policy_comparisons(policy_name)
        
        # Get tax benefits
        tax_info = self.web_search.get_tax_benefits(policy_name)
        
        # Get general policy information
        general_info = self.web_search.search_insurance_info(f"LIC {policy_name} latest updates features")
        
        web_context = {
            'market_insights': market_insights,
            'policy_comparisons': comparisons,
            'tax_benefits': tax_info,
            'latest_updates': general_info
        }
        
        return web_context

    def _create_sales_pitch_prompt(self, context: Dict[str, Any], web_context: Dict[str, Any]) -> str:
        """Create comprehensive sales pitch prompt with real-time data"""
        
        # Extract relevant real-time information
        market_trends = web_context.get('market_insights', {}).get('market_trends', [])
        latest_news = web_context.get('market_insights', {}).get('latest_news', [])
        policy_comparisons = web_context.get('policy_comparisons', [])
        tax_updates = web_context.get('tax_benefits', {}).get('latest_updates', [])
        
        # Format web context for prompt
        real_time_context = """
REAL-TIME MARKET CONTEXT:

Market Trends:
{}

Latest News:
{}

Policy Comparisons:
{}

Tax Updates:
{}
""".format(
            "\n".join(f"- {trend.get('title', '')}" for trend in market_trends[:2]),
            "\n".join(f"- {news.get('title', '')}" for news in latest_news[:2]),
            "\n".join(f"- {comp.get('title', '')}" for comp in policy_comparisons[:2]),
            "\n".join(f"- {update.get('title', '')}" for update in tax_updates[:2])
        )

        return f"""
PERSONALIZED SALES PITCH GENERATION:

Customer Profile:
{json.dumps(context['customer_summary'], indent=2)}

Financial Projections (MATHEMATICALLY CONSISTENT):
{json.dumps(context['financial_projections'], indent=2)}

Primary Recommendation:
{json.dumps(context['primary_recommendation'], indent=2)}

Alternative Options:
{json.dumps(context['alternative_recommendations'], indent=2)}

{real_time_context}

CRITICAL REQUIREMENTS:

1. MATHEMATICAL ACCURACY:
   - Use ONLY the provided financial projections
   - Daily premium = Annual premium ÷ 365
   - Monthly premium = Annual premium ÷ 12
   - Verify all calculations are consistent
   - Do NOT create conflicting numbers

2. POLICY APPROPRIATENESS:
   - Ensure the recommended policy matches the customer's profile
   - Single professionals should NOT get children's plans
   - Young people should NOT get pension plans primarily
   - Match policy to actual life stage and dependents

3. LANGUAGE QUALITY:
   - Use varied, engaging language
   - AVOID repetitive phrases like "beta", "bhai", "yeh beneficial hoga"
   - Use Hindi words sparingly (maximum 2-3 in entire pitch)
   - No robotic or repetitive language patterns
   - Each sentence should add unique value

4. LOGICAL STRUCTURE (Follow this exact flow):
   A. Personal acknowledgment of their situation
   B. Policy recommendation with clear rationale
   C. Financial benefits with accurate calculations
   D. Tax advantages and returns (include latest updates)
   E. Market positioning and competitive advantages
   F. Compelling call to action

5. CONTENT QUALITY:
   - Present each key point only ONCE
   - Use smooth transitions between topics
   - Make it conversational and engaging
   - Focus on genuine value, not sales pressure
   - Incorporate relevant market insights naturally
   - Use real-time data to strengthen recommendations

Generate a compelling 600-800 word sales pitch following this structure exactly.
"""
    
    def _analyze_conversation(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Analyze conversation for follow-up generation"""
        if not conversation_history:
            return "Initial conversation - customer just received recommendations"
        
        # Simple analysis - in production, this could be more sophisticated
        total_messages = len(conversation_history)
        customer_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
        
        if total_messages < 3:
            return "Early stage conversation - building rapport"
        elif total_messages < 8:
            return "Active discussion - customer showing interest"
        else:
            return "Extended conversation - customer highly engaged"
    
    def get_agent_introduction(self) -> str:
        """Get agent introduction for chat interface"""
        return f"""Hello there! I'm {self.config.AGENT_NAME}, and I'm genuinely excited to help you today! 😊

You know, choosing the right insurance policy can feel overwhelming, but don't worry - I'm here to make this journey as smooth and comfortable as possible for you. I understand that every family has unique dreams and concerns, and I'm here to help you navigate through the options.

What I love most about helping families is seeing that moment when everything clicks - when you realize you've found the perfect policy that truly fits your life and goals.

Here's what I bring to our conversation:
• Deep understanding of all LIC policies and how they work in real life
• Personalized guidance based on what matters most to your family
• Clear explanations without confusing jargon
• Honest advice that puts your family's interests first

I'm here to listen, understand your situation, and help you discover which policy options make the most sense for your family's future. No pressure, no rush - just genuine guidance from someone who truly cares about getting this right for you.

So, what's on your mind about your policy recommendations? I'm all ears! 🤗"""
