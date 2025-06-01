"""
Web Search Manager
Enhances LIC recommendations with real-time web search data using Google Custom Search
"""

import os
from typing import List, Dict, Any
import streamlit as st
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.tools import Tool
from datetime import datetime
from .config import DashboardConfig

class WebSearchManager:
    """
    Manages web search functionality to enhance LIC recommendations
    with real-time market data and insurance insights
    """
    
    def __init__(self):
        """Initialize web search manager"""
        self.config = DashboardConfig()
        self._setup_environment()
        self.search = self._initialize_search()
        self.search_tool = self._create_search_tool()
    
    def _setup_environment(self):
        """Set up environment variables for Google Search"""
        # Ensure environment variables are set
        if not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = "AIzaSyBuUsd7mkCyCyVnxCxIjBzZRnJbcDRwbVw"
        if not os.getenv("GOOGLE_CSE_ID"):
            os.environ["GOOGLE_CSE_ID"] = "454f612e8566d4fe4"
        
    def _initialize_search(self) -> GoogleSearchAPIWrapper:
        """Initialize Google Search wrapper"""
        try:
            wrapper = GoogleSearchAPIWrapper(k=self.config.SEARCH_MAX_RESULTS)
            # Test the wrapper with a simple search
            test_result = wrapper.run("LIC India")
            if not test_result:
                raise Exception("Search test failed")
            return wrapper
        except Exception as e:
            if "accessNotConfigured" in str(e):
                st.warning("""
                🔧 Google Custom Search API needs to be enabled. Please:
                1. Visit: https://console.developers.google.com/apis/api/customsearch.googleapis.com/overview?project=776935506468
                2. Click 'Enable' to activate the API
                3. Wait a few minutes for changes to take effect
                4. Restart the application
                
                The system will continue to work with limited functionality until this is set up.
                """)
            else:
                st.warning(f"⚠️ Web search initialization failed: {str(e)}")
            return None
            
    def _create_search_tool(self) -> Tool:
        """Create a search tool using Google Search"""
        if not self.search:
            return Tool(
                name="Web Search",
                description="Search functionality temporarily limited",
                func=lambda x: "Search functionality is being set up. Please enable the Google Custom Search API and try again in a few minutes."
            )
            
        return Tool(
            name="Web Search",
            description="Search for real-time insurance and financial information",
            func=self.search.run
        )
    
    def search_insurance_info(self, query: str) -> List[Dict[str, Any]]:
        """Search for real-time insurance information"""
        if not self.search_tool:
            return [{"title": "Setup Required", "snippet": "Search functionality is being initialized. Please enable the Google Custom Search API and try again in a few minutes."}]
        try:
            search_results = self.search_tool.run(f"site:licindia.in {query}")
            if isinstance(search_results, str):
                return [{"title": "Search Result", "snippet": search_results}]
            return search_results[:5]  # Top 5 relevant results
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return [{"title": "Error", "snippet": "Unable to perform search at this time. Please try again later."}]
    
    def get_market_insights(self, policy_name: str) -> Dict[str, Any]:
        """Get real-time market insights for a policy"""
        if not self.search_tool:
            return {
                'market_trends': [{"title": "Setup Required", "snippet": "Market insights temporarily unavailable. Please enable the Google Custom Search API."}],
                'latest_news': [],
                'performance_metrics': []
            }
        try:
            search_results = self.search_tool.run(f"LIC {policy_name} market performance analysis latest trends site:licindia.in OR site:economictimes.indiatimes.com")
            if isinstance(search_results, str):
                search_results = [{"title": "Market Insight", "snippet": search_results}]
            
            news_results = self.search_tool.run(f"LIC {policy_name} latest news updates 2024 site:licindia.in OR site:economictimes.indiatimes.com")
            if isinstance(news_results, str):
                news_results = [{"title": "Latest News", "snippet": news_results}]
            
            metrics_results = self.search_tool.run(f"LIC {policy_name} returns performance metrics site:licindia.in")
            if isinstance(metrics_results, str):
                metrics_results = [{"title": "Performance Metrics", "snippet": metrics_results}]
            
            return {
                'market_trends': search_results[:3],
                'latest_news': news_results[:3],
                'performance_metrics': metrics_results[:3]
            }
        except Exception as e:
            st.error(f"Market insights search failed: {str(e)}")
            return {'market_trends': [], 'latest_news': [], 'performance_metrics': []}
    
    def get_policy_comparisons(self, policy_name: str) -> List[Dict[str, Any]]:
        """Get real-time policy comparisons"""
        if not self.search_tool:
            raise Exception("Search tool not initialized")
        try:
            search_results = self.search_tool.run(f"LIC {policy_name} vs competitors comparison analysis site:policybazaar.com OR site:bankbazaar.com")
            if isinstance(search_results, str):
                return [{"title": "Policy Comparison", "snippet": search_results}]
            return search_results[:5]
        except Exception as e:
            st.error(f"Policy comparison search failed: {str(e)}")
            return []
    
    def get_tax_benefits(self, policy_name: str) -> Dict[str, Any]:
        """Get real-time tax benefit information"""
        if not self.search_tool:
            raise Exception("Search tool not initialized")
        try:
            updates_results = self.search_tool.run(f"LIC {policy_name} tax benefits latest updates 2024 site:licindia.in OR site:incometaxindia.gov.in")
            if isinstance(updates_results, str):
                updates_results = [{"title": "Tax Updates", "snippet": updates_results}]
            
            rules_results = self.search_tool.run("LIC insurance tax benefits section 80C 80D rules 2024 site:incometaxindia.gov.in")
            if isinstance(rules_results, str):
                rules_results = [{"title": "Tax Rules", "snippet": rules_results}]
            
            examples_results = self.search_tool.run(f"LIC {policy_name} tax saving calculation examples site:licindia.in")
            if isinstance(examples_results, str):
                examples_results = [{"title": "Tax Examples", "snippet": examples_results}]
            
            return {
                'latest_updates': updates_results[:3],
                'tax_rules': rules_results[:3],
                'savings_examples': examples_results[:3]
            }
        except Exception as e:
            st.error(f"Tax benefits search failed: {str(e)}")
            return {'latest_updates': [], 'tax_rules': [], 'savings_examples': []} 