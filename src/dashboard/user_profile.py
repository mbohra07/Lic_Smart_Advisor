"""
User Profile Collection Module
Psychologically-optimized multi-step form for user data collection
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
from .config import DashboardConfig

class UserProfileCollector:
    """Handles intelligent user profile collection with psychological optimization"""
    
    def __init__(self):
        self.config = DashboardConfig()
        
    def collect_profile(self) -> Optional[Dict[str, Any]]:
        """Main method to collect user profile through multi-step form"""
        
        # Initialize session state for profile
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 Demographics", 
            "🏠 Life Context", 
            "🧠 Financial Psychology", 
            "⏰ Timeline", 
            "📋 Summary"
        ])
        
        with tab1:
            self._collect_demographics()
        
        with tab2:
            self._collect_life_context()
            
        with tab3:
            self._collect_financial_psychology()
            
        with tab4:
            self._collect_timeline()
            
        with tab5:
            return self._show_summary_and_proceed()
        
        return None
    
    def _collect_demographics(self):
        """Collect demographic information with smart defaults"""
        st.header("📊 Tell Us About Yourself")
        st.markdown("*Help us understand your current situation for personalized recommendations*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Age with dynamic life stage indicators
            age = st.slider(
                "🎂 Your Age",
                min_value=self.config.AGE_RANGE[0],
                max_value=self.config.AGE_RANGE[1],
                value=st.session_state.user_profile.get('age', 35),
                help="Your current age helps us recommend age-appropriate policies"
            )
            
            # Dynamic life stage indicator
            life_stage_indicator = self._get_life_stage_indicator(age)
            st.info(f"**Life Stage:** {life_stage_indicator}")
            
            st.session_state.user_profile['age'] = age
        
        with col2:
            # Monthly Income with real-time classification
            income = st.slider(
                "💰 Monthly Income (₹)",
                min_value=self.config.INCOME_RANGE[0],
                max_value=self.config.INCOME_RANGE[1],
                value=st.session_state.user_profile.get('monthly_income', 50000),
                step=5000,
                format="₹%d",
                help="Your monthly income helps determine affordable premium ranges"
            )
            
            # Income bracket classification
            income_bracket = self._get_income_bracket(income)
            st.info(f"**Income Bracket:** {income_bracket}")
            
            # Auto-suggest premium ranges
            suggested_premium = self._calculate_suggested_premium(income)
            st.success(f"**Suggested Premium Range:** ₹{suggested_premium['min']:,} - ₹{suggested_premium['max']:,} per month")
            
            st.session_state.user_profile['monthly_income'] = income
    
    def _collect_life_context(self):
        """Collect life context with intelligent validation"""
        st.header("🏠 Your Life Context")
        st.markdown("*Understanding your family situation helps us recommend the right coverage*")
        
        # Life Stage Selection
        life_stage_options = list(self.config.LIFE_STAGES.keys())
        life_stage = st.selectbox(
            "👨‍👩‍👧‍👦 Life Stage",
            options=life_stage_options,
            index=life_stage_options.index(st.session_state.user_profile.get('life_stage', life_stage_options[0])),
            help="Select the option that best describes your current life situation"
        )
        
        # Show detailed information about selected life stage
        stage_info = self.config.get_life_stage_info(life_stage)
        if stage_info:
            st.info(f"**{stage_info['icon']} {stage_info['description']}**")
            st.markdown(f"**Recommended Coverage:** {stage_info['recommended_coverage']}")
        
        st.session_state.user_profile['life_stage'] = life_stage
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Number of Dependents
            dependents = st.number_input(
                "👥 Number of Dependents",
                min_value=0,
                max_value=self.config.MAX_DEPENDENTS,
                value=st.session_state.user_profile.get('dependents', 0),
                help="Include spouse, children, parents, or anyone financially dependent on your income"
            )
            
            # Auto-calculate recommended life cover
            if dependents > 0:
                recommended_cover = self._calculate_recommended_cover(
                    st.session_state.user_profile.get('monthly_income', 50000), 
                    dependents
                )
                st.success(f"**Recommended Life Cover:** ₹{recommended_cover:,}")
            
            st.session_state.user_profile['dependents'] = dependents
        
        with col2:
            # Primary Financial Goal
            goal_options = list(self.config.FINANCIAL_GOALS.keys())
            goal_display_names = [self.config.FINANCIAL_GOALS[goal]['display_name'] for goal in goal_options]
            
            selected_goal_display = st.selectbox(
                "🎯 Primary Financial Goal",
                options=goal_display_names,
                index=0,
                help="What's your main financial objective?"
            )
            
            # Find the corresponding goal key
            primary_goal = goal_options[goal_display_names.index(selected_goal_display)]
            
            # Show goal information
            goal_info = self.config.get_goal_info(primary_goal)
            if goal_info:
                st.info(f"**{goal_info['icon']} Expected Returns:** {goal_info['expected_returns']}")
                st.markdown(f"**Tax Benefits:** {goal_info['tax_benefits']}")
            
            st.session_state.user_profile['primary_goal'] = primary_goal
    
    def _collect_financial_psychology(self):
        """Collect financial psychology with behavioral insights"""
        st.header("🧠 Your Financial Psychology")
        st.markdown("*Help us understand your investment mindset for better recommendations*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk Comfort Level with visual charts
            st.subheader("📊 Risk Comfort Level")
            
            risk_options = list(self.config.RISK_PROFILES.keys())
            risk_labels = [self.config.RISK_PROFILES[risk]['display_name'] for risk in risk_options]
            
            selected_risk = st.radio(
                "Select your risk comfort level:",
                options=risk_options,
                format_func=lambda x: f"{self.config.RISK_PROFILES[x]['icon']} {self.config.RISK_PROFILES[x]['display_name']}",
                index=risk_options.index(st.session_state.user_profile.get('risk_comfort', 'moderate'))
            )
            
            # Show risk profile information
            risk_info = self.config.get_risk_profile_info(selected_risk)
            if risk_info:
                st.info(f"**{risk_info['description']}**")
                st.markdown(f"**Expected Returns:** {risk_info['expected_returns']}")
                
                # Visual risk-return chart
                self._show_risk_return_chart(selected_risk)
            
            st.session_state.user_profile['risk_comfort'] = selected_risk
        
        with col2:
            # Decision Making Style
            st.subheader("🤔 Decision Making Style")
            
            decision_options = list(self.config.DECISION_STYLES.keys())
            decision_labels = [self.config.DECISION_STYLES[style]['display_name'] for style in decision_options]
            
            selected_style = st.radio(
                "How do you typically make financial decisions?",
                options=decision_options,
                format_func=lambda x: f"{self.config.DECISION_STYLES[x]['icon']} {self.config.DECISION_STYLES[x]['display_name']}",
                index=decision_options.index(st.session_state.user_profile.get('decision_style', 'research_heavy'))
            )
            
            # Show decision style information
            style_info = self.config.DECISION_STYLES[selected_style]
            st.info(f"**{style_info['description']}**")
            st.markdown(f"**Our Approach:** {style_info['communication_style']}")
            
            st.session_state.user_profile['decision_style'] = selected_style
    
    def _collect_timeline(self):
        """Collect purchase timeline with urgency-based incentives"""
        st.header("⏰ Purchase Timeline")
        st.markdown("*When are you looking to make a decision?*")
        
        timeline_options = list(self.config.PURCHASE_TIMELINES.keys())
        timeline_labels = [self.config.PURCHASE_TIMELINES[timeline]['display_name'] for timeline in timeline_options]
        
        selected_timeline = st.selectbox(
            "🗓️ When would you like to purchase a policy?",
            options=timeline_options,
            format_func=lambda x: self.config.PURCHASE_TIMELINES[x]['display_name'],
            index=timeline_options.index(st.session_state.user_profile.get('timeline', 'within_3_months'))
        )
        
        # Show timeline-specific incentives
        timeline_info = self.config.PURCHASE_TIMELINES[selected_timeline]
        
        st.success(f"**{timeline_info['sales_message']}**")
        
        if timeline_info['incentives']:
            st.markdown("**Special Benefits for Your Timeline:**")
            for incentive in timeline_info['incentives']:
                st.markdown(f"✅ {incentive}")
        
        st.session_state.user_profile['timeline'] = selected_timeline
        
        # Dynamic CTA based on urgency
        urgency_level = timeline_info['urgency_level']
        if urgency_level == "High":
            st.error("🚨 **Limited Time Offer!** Act now to secure immediate benefits!")
        elif urgency_level == "Medium":
            st.warning("⏰ **Perfect Timing!** Great opportunities available this quarter!")
        else:
            st.info("🌱 **Take Your Time!** We're here to help you explore all options!")
    
    def _show_summary_and_proceed(self) -> Optional[Dict[str, Any]]:
        """Show profile summary and proceed to recommendations"""
        st.header("📋 Profile Summary")
        st.markdown("*Please review your information before proceeding*")
        
        profile = st.session_state.user_profile
        
        if not self._is_profile_complete(profile):
            st.warning("⚠️ Please complete all sections before proceeding to recommendations.")
            return None
        
        # Display summary in organized format
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Personal Information")
            st.write(f"**Age:** {profile.get('age')} years")
            st.write(f"**Monthly Income:** ₹{profile.get('monthly_income', 0):,}")
            st.write(f"**Life Stage:** {profile.get('life_stage', 'Not specified')}")
            st.write(f"**Dependents:** {profile.get('dependents', 0)}")
        
        with col2:
            st.subheader("🎯 Financial Profile")
            goal_info = self.config.get_goal_info(profile.get('primary_goal', ''))
            risk_info = self.config.get_risk_profile_info(profile.get('risk_comfort', ''))
            
            st.write(f"**Primary Goal:** {goal_info.get('display_name', 'Not specified')}")
            st.write(f"**Risk Profile:** {risk_info.get('display_name', 'Not specified')}")
            st.write(f"**Decision Style:** {self.config.DECISION_STYLES.get(profile.get('decision_style', {}), {}).get('display_name', 'Not specified')}")
            st.write(f"**Timeline:** {self.config.PURCHASE_TIMELINES.get(profile.get('timeline', {}), {}).get('display_name', 'Not specified')}")
        
        # Proceed button
        st.markdown("---")
        
        # Dynamic button text based on user psychology
        decision_style = profile.get('decision_style', 'research_heavy')
        timeline = profile.get('timeline', 'within_3_months')
        
        button_text = self._get_dynamic_button_text(decision_style, timeline)
        
        if st.button(button_text, type="primary", use_container_width=True):
            return profile
        
        return None
    
    def _get_life_stage_indicator(self, age: int) -> str:
        """Get life stage indicator based on age"""
        if 25 <= age <= 30:
            return "🌱 Early Career"
        elif 31 <= age <= 40:
            return "🚀 Growth Phase"
        elif 41 <= age <= 50:
            return "🏗️ Wealth Building"
        elif 51 <= age <= 65:
            return "🌅 Pre-Retirement"
        else:
            return "📊 Custom Planning"
    
    def _get_income_bracket(self, income: int) -> str:
        """Classify income bracket"""
        if income < 30000:
            return "💼 Entry Level"
        elif income < 60000:
            return "📈 Mid Level"
        elif income < 150000:
            return "🏆 Senior Level"
        else:
            return "💎 Executive Level"
    
    def _calculate_suggested_premium(self, income: int) -> Dict[str, int]:
        """Calculate suggested premium range (10-20% of annual income)"""
        annual_income = income * 12
        min_premium = int(annual_income * 0.10 / 12)  # 10% annually, monthly
        max_premium = int(annual_income * 0.20 / 12)  # 20% annually, monthly
        return {"min": min_premium, "max": max_premium}
    
    def _calculate_recommended_cover(self, monthly_income: int, dependents: int) -> int:
        """Calculate recommended life cover"""
        annual_income = monthly_income * 12
        base_multiplier = 10 + (dependents * 2)  # 10x + 2x per dependent
        return annual_income * base_multiplier
    
    def _show_risk_return_chart(self, risk_profile: str):
        """Show visual risk-return chart"""
        risk_data = {
            'conservative': {'risk': 2, 'return': 7, 'color': '#28A745'},
            'moderate': {'risk': 5, 'return': 10, 'color': '#FFC107'},
            'aggressive': {'risk': 8, 'return': 15, 'color': '#DC3545'}
        }
        
        fig = go.Figure()
        
        for profile, data in risk_data.items():
            fig.add_trace(go.Scatter(
                x=[data['risk']],
                y=[data['return']],
                mode='markers',
                marker=dict(size=20, color=data['color']),
                name=profile.title(),
                text=f"{profile.title()}<br>Risk: {data['risk']}/10<br>Return: {data['return']}%",
                hovertemplate='%{text}<extra></extra>'
            ))
        
        # Highlight selected profile
        if risk_profile in risk_data:
            selected_data = risk_data[risk_profile]
            fig.add_trace(go.Scatter(
                x=[selected_data['risk']],
                y=[selected_data['return']],
                mode='markers',
                marker=dict(size=30, color=selected_data['color'], line=dict(width=3, color='black')),
                name='Your Selection',
                showlegend=False
            ))
        
        fig.update_layout(
            title="Risk vs Return Profile",
            xaxis_title="Risk Level (1-10)",
            yaxis_title="Expected Return (%)",
            height=300,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _is_profile_complete(self, profile: Dict[str, Any]) -> bool:
        """Check if profile is complete"""
        required_fields = ['age', 'monthly_income', 'life_stage', 'dependents', 
                          'primary_goal', 'risk_comfort', 'decision_style', 'timeline']
        return all(field in profile for field in required_fields)
    
    def _get_dynamic_button_text(self, decision_style: str, timeline: str) -> str:
        """Generate dynamic button text based on user psychology"""
        if timeline == "immediate":
            return "🚀 Get Instant Recommendations Now!"
        elif decision_style == "quick_decider":
            return "⚡ Show Me My Perfect Policy!"
        elif decision_style == "research_heavy":
            return "📊 Analyze My Personalized Options"
        elif decision_style == "seeks_validation":
            return "🎯 Get Expert Recommendations"
        elif decision_style == "price_sensitive":
            return "💰 Find Best Value Policies"
        else:
            return "🎯 Get My AI-Powered Recommendations"
