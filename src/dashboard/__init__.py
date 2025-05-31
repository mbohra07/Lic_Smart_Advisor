"""
LIC Policy Recommendation Dashboard
Production-ready Streamlit dashboard for LIC policy recommendations
"""

__version__ = "1.0.0"
__author__ = "LIC Advisory System"

from .user_profile import UserProfileCollector
from .recommendation_engine import DashboardRecommendationEngine
from .sales_agent import LICGeniusSalesAgent
from .chat_agent import LICChatAgent
from .database_manager import ChatDatabaseManager
from .ui_components import UIComponents
from .config import DashboardConfig

__all__ = [
    "UserProfileCollector",
    "DashboardRecommendationEngine",
    "LICGeniusSalesAgent",
    "LICChatAgent",
    "ChatDatabaseManager",
    "UIComponents",
    "DashboardConfig"
]
