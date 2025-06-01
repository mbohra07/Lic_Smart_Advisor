"""
LIC Chat Agent
Interactive chat interface with the genius LIC sales agent
Enhanced with real-time web search capabilities
"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from .sales_agent import LICGeniusSalesAgent
from .database_manager import ChatDatabaseManager
from .config import DashboardConfig
from .web_search import WebSearchManager

class LICChatAgent:
    """Interactive chat interface with AI sales agent"""
    
    def __init__(self):
        """Initialize chat agent"""
        self.config = DashboardConfig()
        self.sales_agent = LICGeniusSalesAgent()
        self.db_manager = ChatDatabaseManager()
        self.web_search = WebSearchManager()
        
        # Initialize session state
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        if "chat_session_id" not in st.session_state:
            st.session_state.chat_session_id = str(int(time.time()))
        
    def initialize_chat_interface(self, user_profile: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Initialize the chat interface"""
        
        # Initialize session state for chat
        if 'chat_session_id' not in st.session_state:
            st.session_state.chat_session_id = self.db_manager.create_chat_session(
                user_profile, recommendations
            )
        
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
            
            # Add agent introduction
            intro_message = self.sales_agent.get_agent_introduction()
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": intro_message,
                "timestamp": datetime.now(),
                "message_type": "introduction"
            })
        
        # Display chat interface
        self._display_chat_interface(user_profile, recommendations)
    
    def _display_chat_interface(self, user_profile: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Display the main chat interface"""
        
        st.markdown("## 💬 Chat with Your LIC Policy Advisor")
        st.markdown(f"**{self.config.AGENT_NAME}** - *{self.config.AGENT_CREDENTIALS}*")
        
        # Agent avatar and credentials
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("https://via.placeholder.com/100x100/004E89/FFFFFF?text=RK", width=100)
        
        with col2:
            st.markdown(f"""
            **About Your Advisor:**
            - 📚 Comprehensive knowledge of all LIC policies
            - 🎯 Specialized in personalized recommendations
            - 💡 Clear explanations without confusing jargon
            - 🤝 Honest advice that puts your family's interests first
            - 📞 Available to guide you through your policy journey
            """)
        
        st.markdown("---")
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            self._display_chat_messages()
        
        # Chat input
        self._handle_chat_input(user_profile, recommendations)
        
        # Quick action buttons
        self._display_quick_actions(user_profile, recommendations)
    
    def _display_chat_messages(self):
        """Display chat messages using Streamlit's native chat components"""

        for message in st.session_state.chat_messages:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", datetime.now())

            if role == "user":
                # User message
                with st.chat_message("user"):
                    st.write(content)
                    st.caption(f"You • {timestamp.strftime('%H:%M')}")

            else:
                # Agent message
                with st.chat_message("assistant", avatar="👨‍💼"):
                    st.write(content)
                    st.caption(f"{self.config.AGENT_NAME} • {timestamp.strftime('%H:%M')}")
    
    def _handle_chat_input(self, user_profile: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Handle user chat input"""
        
        # Chat input field
        user_input = st.chat_input("Ask me anything about LIC policies...")
        
        if user_input:
            # Add user message
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now(),
                "message_type": "question"
            }
            st.session_state.chat_messages.append(user_message)
            
            # Generate agent response with web search enhancement
            with st.spinner("💭 Agent is thinking..."):
                time.sleep(self.config.TYPING_DELAY)  # Simulate typing
                
                # Get web search results if needed
                web_context = self._get_web_context(user_input, recommendations)
                
                agent_response = self._generate_agent_response(
                    user_input, 
                    user_profile, 
                    recommendations,
                    web_context
                )
                
                agent_message = {
                    "role": "assistant", 
                    "content": agent_response,
                    "timestamp": datetime.now(),
                    "message_type": "response",
                    "web_context": web_context  # Store web context for reference
                }
                st.session_state.chat_messages.append(agent_message)
            
            # Save conversation to database
            self.db_manager.save_chat_message(
                st.session_state.chat_session_id,
                user_message,
                agent_message
            )
            
            # Rerun to display new messages
            st.rerun()
    
    def _get_web_context(self, user_input: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get relevant web search context based on user query"""
        web_context = {}
        
        # Check if query needs market insights
        market_keywords = ["market", "trend", "news", "latest", "update"]
        if any(keyword in user_input.lower() for keyword in market_keywords):
            for rec in recommendations[:1]:  # Get insights for top recommendation
                policy_type = rec['policy_metadata'].get('category', '')
                web_context['market_insights'] = self.web_search.get_market_insights(policy_type)
        
        # Check if query is about policy comparison
        comparison_keywords = ["compare", "difference", "better", "review", "rating"]
        if any(keyword in user_input.lower() for keyword in comparison_keywords):
            for rec in recommendations[:1]:
                policy_name = rec['policy_metadata'].get('policy_name', '')
                web_context['comparisons'] = self.web_search.get_policy_comparisons(policy_name)
        
        # Check if query is about tax benefits
        tax_keywords = ["tax", "80c", "80d", "deduction", "benefit"]
        if any(keyword in user_input.lower() for keyword in tax_keywords):
            for rec in recommendations[:1]:
                policy_type = rec['policy_metadata'].get('category', '')
                web_context['tax_benefits'] = self.web_search.get_tax_benefits(policy_type)
        
        # Get general insurance information if needed
        if not web_context:
            web_context['general_info'] = self.web_search.search_insurance_info(user_input)
        
        return web_context

    def _generate_agent_response(
        self, 
        user_input: str, 
        user_profile: Dict[str, Any], 
        recommendations: List[Dict[str, Any]],
        web_context: Dict[str, Any] = None
    ) -> str:
        """Generate intelligent agent response with web search enhancement"""
        
        try:
            # Get general web search results for any query
            if not web_context or 'general_info' not in web_context:
                general_search = self.web_search.search_insurance_info(user_input)
                if not web_context:
                    web_context = {}
                web_context['general_info'] = general_search

            # Detect if this is an insurance-related query
            insurance_keywords = [
                'policy', 'insurance', 'lic', 'premium', 'coverage',
                'investment', 'return', 'benefit', 'plan', 'term'
            ]
            
            is_insurance_query = any(keyword in user_input.lower() for keyword in insurance_keywords)
            
            # Generate response using Groq
            from groq import Groq
            groq_client = Groq(api_key=self.config.GROQ_API_KEY)
            
            # Prepare context including web search results
            context = self._prepare_chat_context(
                user_profile, 
                recommendations, 
                user_input,
                web_context
            )
            
            # Create appropriate prompt based on query type
            if is_insurance_query:
                prompt = f"""
                Insurance Question: "{user_input}"
                
                Context: {context}
                Web Search Context: {web_context}
                
                Provide an expert insurance-focused response that:
                1. Directly answers their insurance question
                2. Provides specific policy details and calculations
                3. Includes relevant market insights
                4. Guides them toward the next step
                
                Keep response conversational and under 300 words.
                """
            else:
                prompt = f"""
                General Question: "{user_input}"
                
                Context: {context}
                Web Search Context: {web_context}
                
                Provide a helpful response that:
                1. Directly and clearly answers their question using web search data
                2. Provides relevant supporting details or context
                3. IF APPROPRIATE, creates a natural bridge to financial planning/insurance
                4. Maintains a helpful, conversational tone
                
                Remember:
                - Answer the actual question first
                - Only transition to insurance if there's a natural connection
                - Keep response under 300 words
                - Be informative and engaging
                """
            
            response = groq_client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.sales_agent.agent_persona},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            # Fallback response with basic web search results
            general_info = web_context.get('general_info', [])
            if general_info:
                return f"Based on the latest information: {general_info[0].get('snippet', '')}. Would you like to know how this relates to your financial planning?"
            else:
                return "I understand your question. While I'm primarily an insurance expert, I aim to be helpful with any query. Would you like me to explain how this topic might relate to your financial planning?"
    
    def _prepare_chat_context(
        self, 
        user_profile: Dict[str, Any], 
        recommendations: List[Dict[str, Any]], 
        user_question: str,
        web_context: Dict[str, Any] = None
    ) -> str:
        """Prepare context for chat response"""
        
        primary_policy = recommendations[0] if recommendations else {}
        
        context = f"""
        Customer Profile:
        - Age: {user_profile.get('age')}
        - Income: ₹{user_profile.get('monthly_income', 0):,}/month
        - Goal: {user_profile.get('primary_goal')}
        - Life Stage: {user_profile.get('life_stage')}
        - Risk Comfort: {user_profile.get('risk_comfort')}
        
        Primary Recommendation:
        - Policy: {primary_policy.get('policy_metadata', {}).get('policy_name', 'N/A')}
        - Category: {primary_policy.get('policy_metadata', {}).get('category', 'N/A')}
        - Score: {primary_policy.get('recommendation_score', 0)}/100
        
        Customer Question: {user_question}
        """
        
        if web_context:
            context += f"\n\nWeb Search Context: {web_context}"
        
        return context
    
    def _display_quick_actions(self, user_profile: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Display quick action buttons"""
        
        st.markdown("### 🚀 Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💰 Calculate Premium", use_container_width=True):
                self._handle_quick_action("premium_calculation", user_profile, recommendations)

        with col2:
            if st.button("💡 Tax Benefits", use_container_width=True):
                self._handle_quick_action("tax_benefits", user_profile, recommendations)

        with col3:
            if st.button("📞 Schedule Call", use_container_width=True):
                self._handle_quick_action("schedule_call", user_profile, recommendations)
    
    def _handle_quick_action(
        self, 
        action: str, 
        user_profile: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ):
        """Handle quick action button clicks"""
        
        action_responses = {
            "premium_calculation": f"Let me calculate the exact premium for your recommended policy based on your age ({user_profile.get('age')}) and income (₹{user_profile.get('monthly_income', 0):,}). For the recommended policy, you're looking at approximately ₹{user_profile.get('monthly_income', 50000) * 0.15:,.0f} per month, which is just ₹{user_profile.get('monthly_income', 50000) * 0.15 / 30:.0f} per day - less than a cup of coffee! This gives you comprehensive coverage and builds wealth for your family's future.",

            "tax_benefits": f"Excellent! Your recommended policy offers significant tax benefits. You can save up to ₹{min(150000, user_profile.get('monthly_income', 50000) * 12 * 0.15):,.0f} under Section 80C, plus the maturity amount is completely tax-free under Section 10(10D). This means substantial tax savings while building wealth - a win-win situation!",

            "schedule_call": f"I'd be delighted to schedule a personal consultation! As your dedicated LIC policy advisor, I can provide detailed analysis of your recommended policies and answer all your questions. We can discuss premium payment options, policy features, and create a complete financial plan for your family. When would be a convenient time for you?"
        }
        
        response = action_responses.get(action, "I'm here to help with any questions about your policy recommendations!")
        
        # Add response as agent message
        agent_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now(),
            "message_type": "quick_action_response"
        }
        st.session_state.chat_messages.append(agent_message)
        
        # Save to database
        user_action_message = {
            "role": "user",
            "content": f"[Quick Action: {action.replace('_', ' ').title()}]",
            "timestamp": datetime.now(),
            "message_type": "quick_action"
        }
        
        self.db_manager.save_chat_message(
            st.session_state.chat_session_id,
            user_action_message,
            agent_message
        )
        
        st.rerun()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary for analytics"""
        
        if not st.session_state.get('chat_messages'):
            return {}
        
        messages = st.session_state.chat_messages
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        agent_messages = [msg for msg in messages if msg['role'] == 'assistant']
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'agent_messages': len(agent_messages),
            'conversation_duration': self._calculate_conversation_duration(messages),
            'engagement_level': self._calculate_engagement_level(user_messages),
            'last_activity': messages[-1]['timestamp'] if messages else None
        }
    
    def _calculate_conversation_duration(self, messages: List[Dict]) -> int:
        """Calculate conversation duration in minutes"""
        if len(messages) < 2:
            return 0
        
        start_time = messages[0]['timestamp']
        end_time = messages[-1]['timestamp']
        duration = (end_time - start_time).total_seconds() / 60
        return int(duration)
    
    def _calculate_engagement_level(self, user_messages: List[Dict]) -> str:
        """Calculate user engagement level"""
        message_count = len(user_messages)
        
        if message_count >= 10:
            return "High"
        elif message_count >= 5:
            return "Medium"
        elif message_count >= 2:
            return "Low"
        else:
            return "Minimal"
