"""
Chat Database Manager
MongoDB integration for chat history and session management
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
import streamlit as st
from .config import DashboardConfig

class ChatDatabaseManager:
    """Manages chat sessions and conversation history in MongoDB"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.client = None
        self.db = None
        self.chat_collection = None
        self._connect_to_mongodb()
    
    def _connect_to_mongodb(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = MongoClient(self.config.MONGODB_URI)
            self.client.admin.command('ping')  # Test connection
            
            self.db = self.client[self.config.DATABASE_NAME]
            self.chat_collection = self.db[self.config.CHAT_COLLECTION]
            
        except Exception as e:
            st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
    
    def create_chat_session(
        self, 
        user_profile: Dict[str, Any], 
        recommended_policies: List[Dict[str, Any]]
    ) -> str:
        """Create a new chat session"""
        
        session_id = str(uuid.uuid4())
        
        session_document = {
            "session_id": session_id,
            "user_profile": user_profile,
            "recommended_policies": recommended_policies,
            "conversation_history": [],
            "session_metrics": {
                "total_messages": 0,
                "session_duration": 0,
                "objections_raised": [],
                "objections_resolved": [],
                "final_sentiment": "neutral",
                "lead_score": 50,  # Initial score
                "next_action": "nurture"
            },
            "session_outcome": "in_progress",
            "follow_up_scheduled": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        try:
            if self.chat_collection is not None:
                self.chat_collection.insert_one(session_document)
            return session_id
        except Exception as e:
            st.error(f"❌ Error creating chat session: {str(e)}")
            return session_id
    
    def save_chat_message(
        self, 
        session_id: str, 
        user_message: Dict[str, Any], 
        agent_message: Dict[str, Any]
    ):
        """Save chat message exchange to database"""
        
        try:
            if self.chat_collection is None:
                return
            
            # Analyze message for sentiment and objections
            user_sentiment = self._analyze_message_sentiment(user_message['content'])
            objection_type = self._detect_objection_type(user_message['content'])
            
            # Create conversation entry
            conversation_entry = {
                "timestamp": datetime.now(),
                "user_message": user_message['content'],
                "agent_response": agent_message['content'],
                "user_sentiment": user_sentiment,
                "conversation_stage": self._determine_conversation_stage(user_message['content']),
                "objection_type": objection_type,
                "response_time": 2.0,  # Simulated response time
                "user_engagement_score": self._calculate_engagement_score(user_message['content'])
            }
            
            # Update session document
            update_data = {
                "$push": {"conversation_history": conversation_entry},
                "$inc": {"session_metrics.total_messages": 1},
                "$set": {
                    "updated_at": datetime.now(),
                    "session_metrics.final_sentiment": user_sentiment
                }
            }
            
            # Add objection tracking
            if objection_type != "none":
                update_data["$addToSet"] = {"session_metrics.objections_raised": objection_type}
            
            # Update lead score based on engagement
            new_lead_score = self._calculate_lead_score(conversation_entry, user_sentiment)
            update_data["$set"]["session_metrics.lead_score"] = new_lead_score
            
            self.chat_collection.update_one(
                {"session_id": session_id},
                update_data
            )
            
        except Exception as e:
            st.error(f"❌ Error saving chat message: {str(e)}")
    
    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chat session data"""
        try:
            if self.chat_collection is None:
                return None
            
            return self.chat_collection.find_one({"session_id": session_id})
        except Exception as e:
            st.error(f"❌ Error retrieving chat session: {str(e)}")
            return None
    
    def update_session_outcome(self, session_id: str, outcome: str, follow_up_date: Optional[datetime] = None):
        """Update session outcome and follow-up"""
        try:
            if self.chat_collection is None:
                return
            
            update_data = {
                "session_outcome": outcome,
                "updated_at": datetime.now()
            }
            
            if follow_up_date:
                update_data["follow_up_scheduled"] = follow_up_date
            
            self.chat_collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
        except Exception as e:
            st.error(f"❌ Error updating session outcome: {str(e)}")
    
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        try:
            session = self.get_chat_session(session_id)
            if not session:
                return {}
            
            conversation_history = session.get('conversation_history', [])
            
            if not conversation_history:
                return session.get('session_metrics', {})
            
            # Calculate session duration
            start_time = session['created_at']
            end_time = conversation_history[-1]['timestamp']
            duration_minutes = (end_time - start_time).total_seconds() / 60
            
            # Calculate average engagement
            engagement_scores = [msg.get('user_engagement_score', 5) for msg in conversation_history]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 5
            
            # Count objections
            objections = [msg.get('objection_type') for msg in conversation_history if msg.get('objection_type') != 'none']
            
            analytics = {
                'session_duration_minutes': round(duration_minutes, 2),
                'total_exchanges': len(conversation_history),
                'average_engagement': round(avg_engagement, 1),
                'objections_count': len(objections),
                'unique_objections': list(set(objections)),
                'final_sentiment': conversation_history[-1].get('user_sentiment', 'neutral'),
                'lead_score': session.get('session_metrics', {}).get('lead_score', 50),
                'conversation_stages': self._analyze_conversation_stages(conversation_history)
            }
            
            return analytics
            
        except Exception as e:
            st.error(f"❌ Error getting session analytics: {str(e)}")
            return {}
    
    def get_dashboard_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall dashboard analytics"""
        try:
            if self.chat_collection is None:
                return {}
            
            # Get sessions from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "avg_lead_score": {"$avg": "$session_metrics.lead_score"},
                    "hot_leads": {"$sum": {"$cond": [{"$gte": ["$session_metrics.lead_score", 80]}, 1, 0]}},
                    "warm_leads": {"$sum": {"$cond": [{"$and": [{"$gte": ["$session_metrics.lead_score", 60]}, {"$lt": ["$session_metrics.lead_score", 80]}]}, 1, 0]}},
                    "cold_leads": {"$sum": {"$cond": [{"$lt": ["$session_metrics.lead_score", 60]}, 1, 0]}},
                    "total_messages": {"$sum": "$session_metrics.total_messages"}
                }}
            ]
            
            result = list(self.chat_collection.aggregate(pipeline))
            
            if result:
                analytics = result[0]
                analytics.pop('_id', None)
                return analytics
            else:
                return {
                    "total_sessions": 0,
                    "avg_lead_score": 0,
                    "hot_leads": 0,
                    "warm_leads": 0,
                    "cold_leads": 0,
                    "total_messages": 0
                }
                
        except Exception as e:
            st.error(f"❌ Error getting dashboard analytics: {str(e)}")
            return {}
    
    def _analyze_message_sentiment(self, message: str) -> str:
        """Analyze message sentiment (simplified)"""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'love', 'like', 'interested', 'yes']
        negative_words = ['bad', 'expensive', 'costly', 'no', 'not', 'can\'t', 'won\'t', 'difficult']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_objection_type(self, message: str) -> str:
        """Detect type of objection in message"""
        message_lower = message.lower()
        
        objection_patterns = {
            "price": ["expensive", "costly", "too much", "can't afford", "budget", "cheap"],
            "timing": ["think about", "need time", "not ready", "later", "wait"],
            "competition": ["other options", "compare", "better deal", "elsewhere"],
            "confusion": ["don't understand", "confused", "complicated", "unclear"],
            "trust": ["not sure", "doubt", "reliable", "guarantee"]
        }
        
        for objection_type, keywords in objection_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return objection_type
        
        return "none"
    
    def _determine_conversation_stage(self, message: str) -> str:
        """Determine current conversation stage"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "namaste", "start"]):
            return "greeting"
        elif any(word in message_lower for word in ["tell me", "explain", "what is", "how does"]):
            return "discovery"
        elif any(word in message_lower for word in ["premium", "cost", "price", "calculate"]):
            return "presentation"
        elif any(word in message_lower for word in ["but", "however", "concern", "worry"]):
            return "objection"
        elif any(word in message_lower for word in ["buy", "purchase", "proceed", "apply"]):
            return "closing"
        else:
            return "discussion"
    
    def _calculate_engagement_score(self, message: str) -> int:
        """Calculate user engagement score (1-10)"""
        # Length factor
        length_score = min(len(message.split()) / 10, 1) * 3
        
        # Question factor
        question_score = 2 if '?' in message else 0
        
        # Enthusiasm factor
        enthusiasm_words = ['great', 'excellent', 'perfect', 'love', 'amazing']
        enthusiasm_score = 2 if any(word in message.lower() for word in enthusiasm_words) else 0
        
        # Detail factor
        detail_score = 3 if len(message) > 50 else 1
        
        total_score = length_score + question_score + enthusiasm_score + detail_score
        return min(int(total_score), 10)
    
    def _calculate_lead_score(self, conversation_entry: Dict[str, Any], sentiment: str) -> int:
        """Calculate updated lead score"""
        base_score = 50
        
        # Sentiment adjustment
        sentiment_adjustment = {
            "positive": 10,
            "neutral": 0,
            "negative": -5
        }
        
        # Engagement adjustment
        engagement_score = conversation_entry.get('user_engagement_score', 5)
        engagement_adjustment = (engagement_score - 5) * 2
        
        # Objection adjustment
        objection_type = conversation_entry.get('objection_type', 'none')
        objection_adjustment = -10 if objection_type != 'none' else 5
        
        new_score = base_score + sentiment_adjustment.get(sentiment, 0) + engagement_adjustment + objection_adjustment
        
        return max(0, min(100, new_score))
    
    def _analyze_conversation_stages(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze conversation stages distribution"""
        stages = {}
        for msg in conversation_history:
            stage = msg.get('conversation_stage', 'unknown')
            stages[stage] = stages.get(stage, 0) + 1
        return stages
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
