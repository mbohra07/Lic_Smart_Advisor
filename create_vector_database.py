#!/usr/bin/env python3
"""
MongoDB Vector Database Creator - Main Entry Point
Creates MongoDB Atlas vector database from enhanced_lic_policies_vector_db.csv
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vector_db.mongodb_vector_knowledge_base import LICVectorKnowledgeBase

def main():
    """Main function to create the vector knowledge base"""
    print("🚀 Creating MongoDB Atlas Vector Knowledge Base")
    print("=" * 60)
    
    # Configuration
    MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    CSV_FILE_PATH = "data/enhanced_lic_policies_vector_db.csv"
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV file not found: {CSV_FILE_PATH}")
        print("📝 Please run 'python scrape_lic_policies.py' first to generate the data")
        return False
    
    # Initialize knowledge base
    kb = LICVectorKnowledgeBase(MONGODB_URI)
    
    try:
        # Step 1: Connect to MongoDB
        print("🔗 Connecting to MongoDB Atlas...")
        if not kb.connect_to_mongodb():
            return False
        
        # Step 2: Load LIC data
        print("📊 Loading LIC policy data...")
        df = kb.load_lic_data(CSV_FILE_PATH)
        if df is None:
            return False
        
        # Step 3: Process and insert policies
        print("🔄 Processing policies and creating embeddings...")
        if not kb.process_and_insert_policies(df):
            return False
        
        # Step 4: Create indexes
        print("📇 Creating database indexes...")
        if not kb.create_indexes():
            return False
        
        # Step 5: Create vector search index (manual step)
        print("🔍 Vector search index configuration...")
        kb.create_vector_search_index()
        
        # Step 6: Test the system
        print("🧪 Testing vector search functionality...")
        test_queries = [
            "child education planning policy",
            "retirement planning with guaranteed returns",
            "term insurance for young family"
        ]
        
        for query in test_queries:
            kb.test_vector_search(query)
        
        # Step 7: Get database statistics
        print("📊 Database statistics:")
        kb.get_database_stats()
        
        print("\n🎉 Vector knowledge base created successfully!")
        print("📝 Next steps:")
        print("   1. Create vector search index in MongoDB Atlas UI")
        print("   2. Run 'python verify_vector_search.py' to verify setup")
        print("   3. Use the RAG system for policy recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector database: {str(e)}")
        return False
    
    finally:
        kb.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
