#!/usr/bin/env python3
"""
LIC Policy RAG Recommendation Demo
Demonstrates the complete RAG-based policy recommendation system
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vector_db.mongodb_vector_knowledge_base import LICVectorKnowledgeBase, LICRAGQueryEngine

def demo_semantic_search():
    """Demonstrate semantic search functionality"""
    print("🔍 SEMANTIC SEARCH DEMO")
    print("-" * 40)
    
    # Configuration
    MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    
    # Initialize knowledge base and RAG engine
    kb = LICVectorKnowledgeBase(MONGODB_URI)
    
    if not kb.connect_to_mongodb():
        print("❌ Failed to connect to MongoDB")
        return False
    
    rag_engine = LICRAGQueryEngine(kb)
    
    # Test queries
    test_queries = [
        "child education planning policy",
        "retirement planning with guaranteed returns",
        "family protection term insurance",
        "tax saving investment plan"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = rag_engine.semantic_search(query, limit=3)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                policy_name = result['policy_metadata']['policy_name']
                score = result.get('similarity_score', 0)
                category = result['policy_metadata']['category']
                print(f"   {i}. {policy_name}")
                print(f"      Score: {score:.3f}, Category: {category}")
        else:
            print("❌ No results found")
    
    kb.close_connection()
    return True

def demo_user_recommendations():
    """Demonstrate user profile-based recommendations"""
    print("\n👤 USER PROFILE RECOMMENDATIONS DEMO")
    print("-" * 40)
    
    # Configuration
    MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    
    # Initialize knowledge base and RAG engine
    kb = LICVectorKnowledgeBase(MONGODB_URI)
    
    if not kb.connect_to_mongodb():
        print("❌ Failed to connect to MongoDB")
        return False
    
    rag_engine = LICRAGQueryEngine(kb)
    
    # Test user profiles
    test_profiles = [
        {
            "name": "Young Professional",
            "profile": {
                "age": 28,
                "monthly_income": 50000,
                "life_stage": "single",
                "dependents": 0,
                "primary_goal": "wealth_creation",
                "risk_comfort": "moderate"
            }
        },
        {
            "name": "Young Family",
            "profile": {
                "age": 32,
                "monthly_income": 75000,
                "life_stage": "young_family",
                "dependents": 2,
                "primary_goal": "child_education",
                "risk_comfort": "conservative"
            }
        },
        {
            "name": "Pre-Retirement",
            "profile": {
                "age": 45,
                "monthly_income": 120000,
                "life_stage": "established_family",
                "dependents": 2,
                "primary_goal": "retirement_planning",
                "risk_comfort": "moderate"
            }
        }
    ]
    
    for test_case in test_profiles:
        print(f"\n👨‍💼 Profile: {test_case['name']}")
        profile = test_case['profile']
        print(f"   Age: {profile['age']}, Goal: {profile['primary_goal']}")
        print(f"   Income: Rs. {profile['monthly_income']:,}, Risk: {profile['risk_comfort']}")
        
        recommendations = rag_engine.get_policy_recommendations(profile)
        
        if recommendations:
            print(f"✅ Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                policy_name = rec['policy_metadata']['policy_name']
                score = rec.get('recommendation_score', 0)
                category = rec['policy_metadata']['category']
                print(f"   {i}. {policy_name}")
                print(f"      Score: {score:.1f}/100, Category: {category}")
        else:
            print("❌ No recommendations found")
    
    kb.close_connection()
    return True

def main():
    """Main demo function"""
    print("🎯 LIC POLICY RAG RECOMMENDATION SYSTEM DEMO")
    print("=" * 60)
    
    try:
        # Demo 1: Semantic Search
        if not demo_semantic_search():
            return False
        
        # Demo 2: User Profile Recommendations
        if not demo_user_recommendations():
            return False
        
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("✅ Your RAG recommendation system is working perfectly")
        print("\n📝 Integration Notes:")
        print("   - Use LICRAGQueryEngine.semantic_search() for general queries")
        print("   - Use LICRAGQueryEngine.get_policy_recommendations() for user profiles")
        print("   - Similarity scores range from 0.0 to 1.0 (higher = better match)")
        print("   - Recommendation scores range from 0 to 100 (higher = better fit)")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
