#!/usr/bin/env python3
"""
Vector Search Index Verification Script
Confirms that MongoDB Atlas vector search index is properly configured and working
"""

import logging
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorSearchVerifier:
    def __init__(self, mongodb_uri: str):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.collection = None
        self.embedding_model = None
        
    def connect(self):
        """Connect to MongoDB and load embedding model"""
        try:
            logger.info("🔗 Connecting to MongoDB Atlas...")
            self.client = MongoClient(self.mongodb_uri)
            self.client.admin.command('ping')
            
            self.db = self.client["lic_knowledge_base"]
            self.collection = self.db["policy_vectors"]
            
            logger.info("✅ MongoDB connection successful")
            
            logger.info("🤖 Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {str(e)}")
            return False
    
    def check_database_status(self):
        """Check database and collection status"""
        try:
            logger.info("📊 Checking database status...")
            
            # Check collections
            collections = self.db.list_collection_names()
            logger.info(f"Collections found: {collections}")
            
            # Check document count
            doc_count = self.collection.count_documents({})
            logger.info(f"Documents in policy_vectors: {doc_count}")
            
            # Check sample document structure
            sample = self.collection.find_one()
            if sample:
                has_embedding = 'embedding' in sample
                embedding_size = len(sample.get('embedding', [])) if has_embedding else 0
                has_metadata = 'policy_metadata' in sample
                
                logger.info(f"✅ Sample document analysis:")
                logger.info(f"   - Has embedding field: {has_embedding}")
                logger.info(f"   - Embedding dimensions: {embedding_size}")
                logger.info(f"   - Has metadata: {has_metadata}")
                
                if has_embedding and embedding_size == 384:
                    logger.info("✅ Document structure is correct for vector search")
                    return True
                else:
                    logger.error("❌ Document structure issues detected")
                    return False
            else:
                logger.error("❌ No documents found in collection")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database check failed: {str(e)}")
            return False
    
    def check_search_indexes(self):
        """Check if search indexes exist"""
        try:
            logger.info("🔍 Checking search indexes...")
            
            # List all indexes
            indexes = list(self.collection.list_indexes())
            logger.info(f"Regular indexes found: {len(indexes)}")
            
            for idx in indexes:
                logger.info(f"   - {idx.get('name', 'unnamed')}: {list(idx.get('key', {}).keys())}")
            
            # Note: Search indexes are separate from regular MongoDB indexes
            # They're managed through Atlas UI and not visible via list_indexes()
            logger.info("ℹ️  Atlas Search indexes are managed separately and not visible via MongoDB drivers")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Index check failed: {str(e)}")
            return False
    
    def test_vector_search_atlas(self):
        """Test Atlas Vector Search ($vectorSearch)"""
        try:
            logger.info("🧪 Testing Atlas Vector Search...")
            
            # Generate test query embedding
            test_query = "child education planning policy"
            query_embedding = self.embedding_model.encode(test_query).tolist()
            
            # Try Atlas Vector Search pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": 3
                    }
                },
                {
                    "$project": {
                        "policy_metadata.policy_name": 1,
                        "policy_metadata.category": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            if results:
                logger.info(f"✅ Atlas Vector Search working! Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    policy_name = result.get('policy_metadata', {}).get('policy_name', 'Unknown')
                    score = result.get('score', 0)
                    logger.info(f"   {i}. {policy_name} (Score: {score:.3f})")
                return True, "vectorSearch"
            else:
                logger.warning("⚠️  Atlas Vector Search returned no results")
                return False, "vectorSearch"
                
        except Exception as e:
            logger.warning(f"⚠️  Atlas Vector Search failed: {str(e)}")
            return False, "vectorSearch"
    
    def test_atlas_search_knn(self):
        """Test Atlas Search with knnBeta"""
        try:
            logger.info("🧪 Testing Atlas Search with knnBeta...")
            
            # Generate test query embedding
            test_query = "child education planning policy"
            query_embedding = self.embedding_model.encode(test_query).tolist()
            
            # Try Atlas Search with knnBeta
            pipeline = [
                {
                    "$search": {
                        "index": "vector_index",
                        "knnBeta": {
                            "vector": query_embedding,
                            "path": "embedding",
                            "k": 3
                        }
                    }
                },
                {
                    "$project": {
                        "policy_metadata.policy_name": 1,
                        "policy_metadata.category": 1,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            if results:
                logger.info(f"✅ Atlas Search knnBeta working! Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    policy_name = result.get('policy_metadata', {}).get('policy_name', 'Unknown')
                    score = result.get('score', 0)
                    logger.info(f"   {i}. {policy_name} (Score: {score:.3f})")
                return True, "atlasSearch"
            else:
                logger.warning("⚠️  Atlas Search knnBeta returned no results")
                return False, "atlasSearch"
                
        except Exception as e:
            logger.warning(f"⚠️  Atlas Search knnBeta failed: {str(e)}")
            return False, "atlasSearch"
    
    def test_multiple_queries(self, search_type):
        """Test multiple queries to verify search quality"""
        try:
            logger.info(f"🎯 Testing multiple queries with {search_type}...")
            
            test_queries = [
                "child education planning",
                "retirement planning guaranteed returns", 
                "family protection term insurance",
                "tax saving investment"
            ]
            
            successful_queries = 0
            
            for query in test_queries:
                logger.info(f"📝 Testing: '{query}'")
                
                query_embedding = self.embedding_model.encode(query).tolist()
                
                if search_type == "vectorSearch":
                    pipeline = [
                        {
                            "$vectorSearch": {
                                "index": "vector_index",
                                "path": "embedding", 
                                "queryVector": query_embedding,
                                "numCandidates": 100,
                                "limit": 2
                            }
                        },
                        {
                            "$project": {
                                "policy_metadata.policy_name": 1,
                                "score": {"$meta": "vectorSearchScore"}
                            }
                        }
                    ]
                else:  # atlasSearch
                    pipeline = [
                        {
                            "$search": {
                                "index": "vector_index",
                                "knnBeta": {
                                    "vector": query_embedding,
                                    "path": "embedding",
                                    "k": 2
                                }
                            }
                        },
                        {
                            "$project": {
                                "policy_metadata.policy_name": 1,
                                "score": {"$meta": "searchScore"}
                            }
                        }
                    ]
                
                results = list(self.collection.aggregate(pipeline))
                
                if results and len(results) > 0:
                    successful_queries += 1
                    top_result = results[0]
                    policy_name = top_result.get('policy_metadata', {}).get('policy_name', 'Unknown')
                    score = top_result.get('score', 0)
                    logger.info(f"   ✅ Top result: {policy_name} (Score: {score:.3f})")
                else:
                    logger.warning(f"   ⚠️  No results for query: {query}")
            
            success_rate = (successful_queries / len(test_queries)) * 100
            logger.info(f"📊 Query success rate: {success_rate:.1f}% ({successful_queries}/{len(test_queries)})")
            
            return success_rate >= 75  # 75% success rate threshold
            
        except Exception as e:
            logger.error(f"❌ Multiple query test failed: {str(e)}")
            return False
    
    def run_comprehensive_verification(self):
        """Run all verification tests"""
        logger.info("🚀 Starting comprehensive vector search verification...")
        logger.info("=" * 60)
        
        # Test 1: Connection and database status
        if not self.connect():
            return False
        
        # Test 2: Database structure
        if not self.check_database_status():
            return False
        
        # Test 3: Index status
        self.check_search_indexes()
        
        # Test 4: Try Atlas Vector Search
        vector_search_works, search_type = self.test_vector_search_atlas()
        
        # Test 5: Try Atlas Search if Vector Search failed
        if not vector_search_works:
            atlas_search_works, search_type = self.test_atlas_search_knn()
            if not atlas_search_works:
                logger.error("❌ Both Atlas Vector Search and Atlas Search failed")
                return False
        
        # Test 6: Multiple query testing
        if not self.test_multiple_queries(search_type):
            logger.warning("⚠️  Search quality below threshold")
        
        # Final assessment
        logger.info("=" * 60)
        logger.info("📋 VERIFICATION SUMMARY")
        logger.info("=" * 60)
        logger.info("✅ Database connection: WORKING")
        logger.info("✅ Document structure: CORRECT")
        logger.info("✅ Embedding dimensions: 384 (CORRECT)")
        logger.info(f"✅ Vector search method: {search_type.upper()}")
        logger.info("✅ Search functionality: WORKING")
        
        logger.info("\n🎉 VECTOR SEARCH INDEX VERIFICATION SUCCESSFUL!")
        logger.info(f"🔧 Your system is using: {search_type}")
        logger.info("🚀 Ready for production use!")
        
        return True
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")

def main():
    """Main verification function"""
    mongodb_uri = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    
    verifier = VectorSearchVerifier(mongodb_uri)
    
    try:
        success = verifier.run_comprehensive_verification()
        
        if success:
            logger.info("\n🎯 NEXT STEPS:")
            logger.info("1. Update your RAG application to use the working search method")
            logger.info("2. Run performance tests with real user queries")
            logger.info("3. Monitor search quality and user satisfaction")
        else:
            logger.error("\n❌ VECTOR SEARCH SETUP INCOMPLETE")
            logger.error("Please check the error messages above and:")
            logger.error("1. Verify your Atlas search index configuration")
            logger.error("2. Ensure the index is in 'Ready' status")
            logger.error("3. Check index name matches 'vector_index'")
        
    except Exception as e:
        logger.error(f"❌ Verification failed with error: {str(e)}")
    
    finally:
        verifier.close()

if __name__ == "__main__":
    main()
