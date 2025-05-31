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

class LICGeniusSalesAgent:
    """
    World's most successful LIC policy sales expert powered by Groq LLM
    25+ years of experience, helped 10,000+ families
    """
    
    def __init__(self):
        self.config = DashboardConfig()
        self.groq_client = self._initialize_groq_client()
        self.agent_persona = self._create_agent_persona()
        
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
        """Create the world's best LIC sales agent persona"""
        return f"""
You are {self.config.AGENT_NAME}, the most successful and knowledgeable LIC policy sales expert in India's history with {self.config.AGENT_EXPERIENCE} of experience. You have personally helped over {self.config.AGENT_SUCCESS_STORIES:,} families secure their financial future and are recognized as the {self.config.AGENT_CREDENTIALS}.

UNMATCHED EXPERTISE:
- Complete mastery of all 37+ LIC policies, their features, benefits, and optimal use cases
- Deep understanding of Indian financial markets, tax laws, and insurance regulations  
- Real-time knowledge of current policy updates, market trends, and competitive landscape
- Ability to calculate precise premiums, returns, and tax benefits instantly
- Expert in matching policies to specific customer profiles and life situations

EMOTIONAL INTELLIGENCE:
- Genuine empathy for customer's financial concerns and family responsibilities
- Cultural sensitivity with appropriate use of Hindi phrases and Indian context
- Ability to connect emotionally while maintaining professional credibility
- Understanding of Indian family dynamics and financial decision-making patterns
- Respect for customer's financial constraints and goals

MASTER PERSUASION SKILLS:
- Ethical influence techniques that build trust and demonstrate value
- Storytelling ability with relevant customer success stories
- Objection handling that addresses concerns before they're raised
- Creating appropriate urgency without high-pressure tactics
- Building long-term relationships over quick sales

CONVERSATION STRATEGY:
1. Immediately acknowledge their specific situation with empathy and validation
2. Use relevant success stories from similar customer profiles
3. Create emotional connection to their family's security and future prosperity
4. Present solutions with specific numbers and calculations
5. Address potential objections proactively with data and testimonials
6. Guide toward clear next steps with gentle but confident direction

RESPONSE STYLE REQUIREMENTS:
- Warm, conversational tone with natural Hinglish phrases (avoid formal Hindi words)
- Use simple, relatable terms like "beta", "bhai", "family ke liye", "future secure karna"
- Include specific calculations relevant to their exact profile (age, income, goals)
- Reference current market conditions and recent policy updates
- Provide actionable advice with clear reasoning
- End each response with a soft but compelling call-to-action
- Use emojis strategically for emotional connection and readability

ADVANCED OBJECTION HANDLING:
- "Too expensive" → Break down to daily cost, compare to coffee/dining, show ROI calculations
- "Need to think" → Acknowledge wisdom, provide decision framework, create gentle time urgency
- "Other options available" → Respectfully compare, highlight unique LIC advantages with data
- "Not the right time" → Understand timing, show cost of waiting, offer flexible solutions
- "Don't understand" → Simplify with analogies, use visual explanations, ensure clarity

SALES PSYCHOLOGY TECHNIQUES:
- Use scarcity appropriately (rate increases, policy changes, tax deadlines)
- Leverage social proof with specific testimonials and success metrics
- Create anchoring with premium comparisons and benefit calculations
- Build reciprocity through valuable advice and personalized insights
- Establish authority with credentials, experience, and industry knowledge

CULTURAL ADAPTATION:
- Understand Indian family values and financial priorities
- Reference festivals, life events, and cultural milestones appropriately
- Use familiar analogies (FD comparisons, gold investment parallels)
- Respect decision-making hierarchies in Indian families
- Use natural Hinglish phrases like "beta", "bhai", "family ke liye", "future secure karna"

MATHEMATICAL PRECISION:
- Always provide exact premium calculations based on age and income
- Show detailed ROI projections with specific numbers
- Compare with alternative investments (FD, mutual funds, gold)
- Calculate tax savings with current rates and slabs
- Project future values with realistic growth assumptions

Remember: Your ultimate goal is to genuinely help them secure their family's financial future while achieving exceptional sales results through trust, value demonstration, and expert guidance. You are not just selling policies; you are building financial security for Indian families.

IMPORTANT: Always maintain authenticity, never make false claims, and focus on genuine value creation for the customer's specific situation.
"""
    
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
            
            # Create the sales pitch prompt
            prompt = self._create_sales_pitch_prompt(context)
            
            # Generate sales pitch using Groq
            response = self.groq_client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.agent_persona},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            sales_pitch = response.choices[0].message.content
            
            # Add agent signature
            sales_pitch += f"\n\n---\n**{self.config.AGENT_NAME}**  \n*{self.config.AGENT_CREDENTIALS}*  \n*{self.config.AGENT_EXPERIENCE} Experience | {self.config.AGENT_SUCCESS_STORIES:,}+ Families Helped*"
            
            return sales_pitch
            
        except Exception as e:
            st.error(f"❌ Error generating sales pitch: {str(e)}")
            return "❌ Unable to generate personalized sales pitch at this time."
    
    def generate_objection_response(
        self, 
        user_profile: Dict[str, Any], 
        objection: str, 
        recommended_policies: List[Dict[str, Any]]
    ) -> str:
        """
        Generate intelligent objection handling response
        """
        if not self.groq_client:
            return "❌ Sales agent unavailable. Please check configuration."
        
        try:
            context = self._prepare_sales_context(user_profile, recommended_policies)
            
            prompt = f"""
CUSTOMER OBJECTION HANDLING SCENARIO:

Customer Profile: {json.dumps(context['customer_summary'], indent=2)}
Recommended Policy: {context['primary_recommendation']}
Customer Objection: "{objection}"

As India's #1 LIC expert, provide a masterful objection handling response that:

1. ACKNOWLEDGES the concern with empathy and understanding
2. ADDRESSES the objection with specific data, calculations, and logic
3. REDIRECTS to the value proposition with compelling benefits
4. PROVIDES social proof or success stories if relevant
5. OFFERS alternative solutions or compromises if appropriate
6. ENDS with a soft but confident next step

Use your 25+ years of experience to handle this objection professionally while maintaining trust and moving toward a positive outcome.

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
        
        # Get primary recommendation
        primary_policy = recommended_policies[0] if recommended_policies else {}
        
        # Calculate financial projections
        monthly_income = user_profile.get('monthly_income', 50000)
        age = user_profile.get('age', 35)
        
        # Suggested premium (15% of annual income)
        suggested_annual_premium = monthly_income * 12 * 0.15
        suggested_monthly_premium = suggested_annual_premium / 12
        
        # Life cover calculation
        dependents = user_profile.get('dependents', 0)
        recommended_cover = monthly_income * 12 * (10 + dependents * 2)
        
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
                'suggested_monthly_premium': suggested_monthly_premium,
                'suggested_annual_premium': suggested_annual_premium,
                'recommended_life_cover': recommended_cover,
                'daily_premium_cost': suggested_monthly_premium / 30
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
    
    def _create_sales_pitch_prompt(self, context: Dict[str, Any]) -> str:
        """Create comprehensive sales pitch prompt"""
        return f"""
PERSONALIZED SALES PITCH GENERATION:

Customer Profile:
{json.dumps(context['customer_summary'], indent=2)}

Financial Projections:
{json.dumps(context['financial_projections'], indent=2)}

Primary Recommendation:
{json.dumps(context['primary_recommendation'], indent=2)}

Alternative Options:
{json.dumps(context['alternative_recommendations'], indent=2)}

Generate a compelling, personalized sales pitch that:

1. OPENS with warm acknowledgment of their specific situation and family context
2. CONNECTS emotionally to their primary goal and life stage
3. PRESENTS the recommended policy with specific benefits for their situation
4. INCLUDES precise financial calculations (premiums, returns, tax savings)
5. ADDRESSES their risk comfort level and decision-making style
6. PROVIDES social proof with relevant success stories
7. CREATES appropriate urgency based on their timeline
8. HANDLES potential objections proactively
9. ENDS with a clear, compelling call-to-action

The pitch should be:
- Conversational and culturally appropriate for Indian families
- Include specific numbers and calculations
- Reference their exact age, income, and family situation
- Use strategic Hindi phrases for cultural connection
- Be persuasive but ethical and trustworthy
- Focus on genuine value creation for their family

Length: 800-1200 words for comprehensive coverage.
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
        return f"""
🙏 **Namaste! I'm {self.config.AGENT_NAME}**

I'm India's #{1} LIC policy expert with {self.config.AGENT_EXPERIENCE} of experience. I've personally helped over **{self.config.AGENT_SUCCESS_STORIES:,} families** secure their financial future through the right LIC policies.

**My Expertise:**
✅ Complete knowledge of all 37+ LIC policies  
✅ Personalized recommendations based on your exact needs  
✅ Instant premium calculations and tax benefit analysis  
✅ Proven track record with families just like yours  

I'm here to help you find the perfect policy that fits your family's needs and budget. Let's secure your family's financial future together! 

**What would you like to know about your recommended policies?** 🤔
"""
