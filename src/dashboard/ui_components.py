"""
UI Components
Reusable UI components for the dashboard
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
from .config import DashboardConfig

class UIComponents:
    """Reusable UI components for the dashboard"""
    
    def __init__(self):
        self.config = DashboardConfig()
    
    @staticmethod
    def custom_css():
        """Apply custom CSS styling"""
        st.markdown("""
        <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        .dashboard-header {
            background: linear-gradient(90deg, #FF6B35, #004E89);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Card styling */
        .policy-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #28A745;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .primary-card {
            border-left-color: #28A745;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        .alternative-card {
            border-left-color: #FFC107;
            background: #f8f9fa;
        }
        
        /* Chat styling */
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            background: #ffffff;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            padding: 10px 15px;
            border-radius: 18px 18px 5px 18px;
            margin: 5px 0;
            margin-left: 20%;
            text-align: right;
        }
        
        .agent-message {
            background: #f1f3f4;
            color: #333;
            padding: 10px 15px;
            border-radius: 18px 18px 18px 5px;
            margin: 5px 0;
            margin-right: 20%;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #FF6B35, #004E89);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #FF6B35, #004E89);
        }
        
        /* Metric styling */
        .metric-container {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Alert styling */
        .success-alert {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .warning-alert {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .info-alert {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .user-message, .agent-message {
                margin-left: 5%;
                margin-right: 5%;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def display_header(self, title: str, subtitle: str = ""):
        """Display dashboard header"""
        st.markdown(f"""
        <div class="dashboard-header fade-in">
            <h1>{title}</h1>
            {f'<p style="font-size: 18px; margin: 10px 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def display_policy_card(self, policy_data: Dict[str, Any], card_type: str = "primary"):
        """Display policy recommendation card"""
        
        policy_name = policy_data.get('policy_metadata', {}).get('policy_name', 'Policy')
        category = policy_data.get('policy_metadata', {}).get('category', 'Comprehensive')
        score = policy_data.get('recommendation_score', 85)
        enhanced_data = policy_data.get('enhanced_data', {})
        
        card_class = "primary-card" if card_type == "primary" else "alternative-card"
        icon = "🏆" if card_type == "primary" else "⭐"
        
        st.markdown(f"""
        <div class="policy-card {card_class} fade-in">
            <h3 style="margin-top: 0; color: #28A745;">{icon} {policy_name}</h3>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p><strong>Category:</strong> {category}</p>
                    <p><strong>Match Score:</strong> {score:.1f}/100 🎯</p>
                    <p><strong>Monthly Premium:</strong> ₹{enhanced_data.get('estimated_monthly_premium', 0):,.0f}</p>
                    <p><strong>Affordability:</strong> {enhanced_data.get('affordability_score', 'Good')}</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #28A745;">{score:.0f}%</div>
                    <div style="font-size: 12px; color: #666;">Match Score</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_progress_indicator(self, current_step: int, total_steps: int, step_names: List[str]):
        """Display progress indicator"""
        progress = current_step / total_steps
        
        st.markdown("### 📋 Profile Completion Progress")
        st.progress(progress)
        
        # Step indicators
        cols = st.columns(total_steps)
        for i, (col, step_name) in enumerate(zip(cols, step_names)):
            with col:
                if i < current_step:
                    st.markdown(f"✅ **{step_name}**")
                elif i == current_step:
                    st.markdown(f"🔄 **{step_name}**")
                else:
                    st.markdown(f"⏳ {step_name}")
    
    def display_metric_cards(self, metrics: Dict[str, Any]):
        """Display metric cards"""
        cols = st.columns(len(metrics))
        
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-container">
                    <div style="font-size: 24px; font-weight: bold; color: #FF6B35;">{value}</div>
                    <div style="font-size: 14px; color: #666;">{key}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def display_confidence_gauge(self, score: float, title: str = "Confidence Score"):
        """Display confidence gauge chart"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.config.PRIMARY_COLOR},
                'steps': [
                    {'range': [0, 50], 'color': self.config.DANGER_COLOR},
                    {'range': [50, 75], 'color': self.config.WARNING_COLOR},
                    {'range': [75, 100], 'color': self.config.SUCCESS_COLOR}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    

    
    def display_risk_return_chart(self, risk_profiles: Dict[str, Dict[str, Any]], selected_profile: str = ""):
        """Display risk vs return chart"""
        
        fig = go.Figure()
        
        for profile, data in risk_profiles.items():
            color = '#28A745' if profile == 'conservative' else '#FFC107' if profile == 'moderate' else '#DC3545'
            size = 25 if profile == selected_profile else 15
            
            fig.add_trace(go.Scatter(
                x=[data.get('risk_level', 5)],
                y=[float(data.get('expected_returns', '10').replace('%', ''))],
                mode='markers',
                marker=dict(size=size, color=color, line=dict(width=2, color='white')),
                name=profile.title(),
                text=f"{profile.title()}<br>Risk: {data.get('risk_level', 5)}/10<br>Return: {data.get('expected_returns', '10%')}",
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Risk vs Return Profile",
            xaxis_title="Risk Level (1-10)",
            yaxis_title="Expected Return (%)",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def display_alert(self, message: str, alert_type: str = "info"):
        """Display styled alert"""
        
        alert_classes = {
            "success": "success-alert",
            "warning": "warning-alert", 
            "info": "info-alert",
            "error": "warning-alert"  # Use warning style for errors
        }
        
        icons = {
            "success": "✅",
            "warning": "⚠️",
            "info": "ℹ️",
            "error": "❌"
        }
        
        alert_class = alert_classes.get(alert_type, "info-alert")
        icon = icons.get(alert_type, "ℹ️")
        
        st.markdown(f"""
        <div class="{alert_class}">
            {icon} {message}
        </div>
        """, unsafe_allow_html=True)
    
    def display_loading_animation(self, message: str = "Loading..."):
        """Display loading animation"""
        return st.spinner(f"🔄 {message}")
    
    def display_success_animation(self, message: str):
        """Display success message with animation"""
        st.balloons()
        self.display_alert(message, "success")
    
    def create_sidebar_navigation(self, pages: List[str], current_page: str = ""):
        """Create sidebar navigation"""
        
        st.sidebar.markdown("## 🧭 Navigation")
        
        for page in pages:
            if page == current_page:
                st.sidebar.markdown(f"**▶️ {page}**")
            else:
                if st.sidebar.button(page, key=f"nav_{page}"):
                    return page
        
        return current_page
    
    def display_agent_avatar(self, agent_name: str, credentials: str, experience: str):
        """Display agent avatar and credentials"""
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Placeholder avatar - in production, use actual image
            st.markdown(f"""
            <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(45deg, #FF6B35, #004E89); 
                        display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold;">
                {agent_name[:2]}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **{agent_name}**  
            *{credentials}*  
            📅 {experience} Experience  
            🏆 10,000+ Families Helped  
            ⭐ 4.9/5 Customer Rating
            """)
    
    def display_typing_indicator(self):
        """Display typing indicator for chat"""
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 10px;">
            <div style="margin-right: 10px;">Agent is typing</div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <style>
        .typing-indicator {
            display: flex;
            gap: 4px;
        }
        
        .typing-indicator span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #666;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        </style>
        """, unsafe_allow_html=True)
