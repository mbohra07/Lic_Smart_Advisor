"""
LIC Chat Agent
Interactive chat interface with the genius LIC sales agent
"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from .sales_agent import LICGeniusSalesAgent
from .database_manager import ChatDatabaseManager
from .config import DashboardConfig

class LICChatAgent:
    """Interactive chat interface with AI sales agent"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.sales_agent = LICGeniusSalesAgent()
        self.db_manager = ChatDatabaseManager()
        
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
        user_input = st.chat_input("Ask me anything about your policy recommendations...")
        
        if user_input:
            # Add user message
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now(),
                "message_type": "question"
            }
            st.session_state.chat_messages.append(user_message)
            
            # Generate agent response
            with st.spinner("💭 Agent is thinking..."):
                time.sleep(self.config.TYPING_DELAY)  # Simulate typing
                
                agent_response = self._generate_agent_response(
                    user_input, user_profile, recommendations
                )
                
                agent_message = {
                    "role": "assistant", 
                    "content": agent_response,
                    "timestamp": datetime.now(),
                    "message_type": "response"
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
    
    def _generate_agent_response(
        self, 
        user_input: str, 
        user_profile: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate intelligent agent response"""
        
        # Detect if this is an objection
        objection_keywords = [
            'expensive', 'costly', 'too much', 'can\'t afford', 'budget',
            'think about', 'need time', 'discuss', 'other options',
            'not sure', 'confused', 'don\'t understand', 'complicated'
        ]
        
        is_objection = any(keyword in user_input.lower() for keyword in objection_keywords)
        
        if is_objection:
            # Handle objection
            return self.sales_agent.generate_objection_response(
                user_profile, user_input, recommendations
            )
        else:
            # Generate regular response using Groq
            try:
                from groq import Groq
                groq_client = Groq(api_key=self.config.GROQ_API_KEY)
                
                context = self._prepare_chat_context(user_profile, recommendations, user_input)
                
                response = groq_client.chat.completions.create(
                    model=self.config.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": self.sales_agent.agent_persona},
                        {"role": "user", "content": f"""
                        Customer Question: "{user_input}"
                        
                        Context: {context}
                        
                        Provide a helpful, expert response that:
                        1. Directly answers their question
                        2. Provides specific details about their recommended policies
                        3. Includes relevant calculations or comparisons
                        4. Maintains the warm, expert tone
                        5. Guides them toward the next step
                        
                        Keep response conversational and under 300 words.
                        """}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                return f"I understand your question about {user_input}. Let me provide you with detailed information about your recommended policies. Based on your profile, I believe the recommended policy is an excellent fit for your needs. Would you like me to explain the specific benefits and how they align with your goals?"
    
    def _prepare_chat_context(
        self, 
        user_profile: Dict[str, Any], 
        recommendations: List[Dict[str, Any]], 
        user_question: str
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
