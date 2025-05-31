#!/usr/bin/env python3
"""
MongoDB Atlas Vector Knowledge Base Creator for LIC Policies
Creates a vector database optimized for RAG-based policy recommendations
"""

import pandas as pd
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mongodb_vector_kb.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LICVectorKnowledgeBase:
    """
    Creates and manages LIC policy vector knowledge base on MongoDB Atlas
    """
    
    def __init__(self, mongodb_uri: str, database_name: str = "lic_knowledge_base"):
        """
        Initialize the vector knowledge base
        
        Args:
            mongodb_uri: MongoDB Atlas connection string
            database_name: Name of the database to create
        """
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.collection_name = "policy_vectors"
        self.metadata_collection = "policy_metadata"
        
        # Initialize embedding model
        logger.info("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        # Connect to MongoDB
        self.client = None
        self.db = None
        self.collection = None
        self.metadata_collection_obj = None
        
    def connect_to_mongodb(self):
        """Establish connection to MongoDB Atlas"""
        try:
            logger.info("Connecting to MongoDB Atlas...")
            self.client = MongoClient(self.mongodb_uri)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
            
            # Get database and collections
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            self.metadata_collection_obj = self.db[self.metadata_collection]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def create_vector_search_index(self):
        """Create vector search index for efficient similarity search"""
        try:
            logger.info("Creating vector search index...")
            
            # Vector search index configuration
            index_definition = {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": self.embedding_dimension,
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "policy_metadata.category"
                    },
                    {
                        "type": "filter", 
                        "path": "policy_metadata.eligibility_age_min"
                    },
                    {
                        "type": "filter",
                        "path": "policy_metadata.eligibility_age_max"
                    }
                ]
            }
            
            # Note: Vector search index creation requires Atlas UI or Atlas CLI
            # This is a placeholder for the index structure
            logger.info("📝 Vector search index definition created")
            logger.info("⚠️  Please create the vector search index manually in Atlas UI with this definition:")
            logger.info(json.dumps(index_definition, indent=2))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating vector search index: {str(e)}")
            return False
    
    def load_lic_data(self, csv_file_path: str) -> pd.DataFrame:
        """Load LIC policy data from CSV"""
        try:
            logger.info(f"Loading LIC data from {csv_file_path}...")
            df = pd.read_csv(csv_file_path)
            logger.info(f"✅ Loaded {len(df)} policies from CSV")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV data: {str(e)}")
            return None
    
    def parse_age_range(self, age_str: str) -> tuple:
        """Parse age range string into min and max values"""
        if pd.isna(age_str) or age_str == '':
            return 0, 100  # Default range
        
        try:
            if '-' in str(age_str):
                parts = str(age_str).split('-')
                min_age = int(parts[0].strip())
                max_age = int(parts[1].split()[0].strip())  # Handle "50 years" format
                return min_age, max_age
            else:
                # Single age or other format
                return 0, 100
        except:
            return 0, 100
    
    def create_policy_text_for_embedding(self, row: pd.Series) -> str:
        """Create comprehensive text representation for embedding"""
        text_parts = []
        
        # Policy name and basic info
        text_parts.append(f"Policy: {row['policy_name']}")
        text_parts.append(f"Category: {row['category']}")
        
        # Features and benefits
        if pd.notna(row['features_benefits']):
            text_parts.append(f"Features: {row['features_benefits']}")
        
        # Eligibility
        if pd.notna(row['eligibility_age']):
            text_parts.append(f"Age eligibility: {row['eligibility_age']}")
        
        # Benefits
        if pd.notna(row['maturity_benefits']):
            text_parts.append(f"Maturity benefits: {row['maturity_benefits']}")
        
        # Tax benefits
        if pd.notna(row['tax_benefits']):
            text_parts.append(f"Tax benefits: {row['tax_benefits']}")
        
        # Premium options
        if pd.notna(row['premium_options']):
            text_parts.append(f"Premium options: {row['premium_options']}")
        
        # Surrender clause
        if pd.notna(row['surrender_clause']):
            text_parts.append(f"Surrender: {row['surrender_clause']}")
        
        return " | ".join(text_parts)
    
    def process_and_insert_policies(self, df: pd.DataFrame):
        """Process policies and insert into MongoDB with embeddings"""
        try:
            logger.info("Processing policies and creating embeddings...")

            # Clear existing data
            self.collection.delete_many({})
            self.metadata_collection_obj.delete_many({})

            documents = []
            metadata_docs = []

            for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing policies"):
                # Handle missing plan numbers
                plan_number = row['plan_number']
                if pd.isna(plan_number) or str(plan_number).lower() == 'nan':
                    plan_number = f"unknown_{idx}"
                    logger.warning(f"Missing plan number for policy '{row['policy_name']}', using '{plan_number}'")

                # Create unique policy ID
                policy_id = f"lic_{plan_number}"

                # Create text for embedding
                policy_text = self.create_policy_text_for_embedding(row)

                # Generate embedding
                embedding = self.embedding_model.encode(policy_text).tolist()

                # Parse age range
                age_min, age_max = self.parse_age_range(row['eligibility_age'])

                # Create policy metadata
                metadata = {
                    "policy_id": policy_id,
                    "policy_name": row['policy_name'],
                    "plan_number": str(plan_number),
                    "uin_number": row['uin_number'] if pd.notna(row['uin_number']) else "",
                    "category": row['category'] if pd.notna(row['category']) else "Unknown",
                    "eligibility_age_min": age_min,
                    "eligibility_age_max": age_max,
                    "medical_examination": row['medical_examination'] if pd.notna(row['medical_examination']) else "",
                    "premium_options": row['premium_options'] if pd.notna(row['premium_options']) else "",
                    "data_completeness_score": float(row['data_completeness_score']) if pd.notna(row['data_completeness_score']) else 0.0,
                    "source_url": row['source_url'] if pd.notna(row['source_url']) else "",
                    "scraped_timestamp": row['scraped_timestamp'] if pd.notna(row['scraped_timestamp']) else ""
                }

                # Create document for vector collection
                document = {
                    "policy_id": policy_id,
                    "policy_text": policy_text,
                    "embedding": embedding,
                    "policy_metadata": metadata,
                    "features_benefits": row['features_benefits'] if pd.notna(row['features_benefits']) else "",
                    "maturity_benefits": row['maturity_benefits'] if pd.notna(row['maturity_benefits']) else "",
                    "tax_benefits": row['tax_benefits'] if pd.notna(row['tax_benefits']) else "",
                    "terms_conditions": row['terms_conditions'] if pd.notna(row['terms_conditions']) else "",
                    "riders_available": row['riders_available'] if pd.notna(row['riders_available']) else "",
                    "surrender_clause": row['surrender_clause'] if pd.notna(row['surrender_clause']) else "",
                    "created_at": datetime.now(timezone.utc)
                }

                documents.append(document)
                metadata_docs.append({**metadata, "created_at": datetime.now(timezone.utc)})

            # Bulk insert documents
            logger.info("Inserting documents into MongoDB...")
            result = self.collection.insert_many(documents)
            metadata_result = self.metadata_collection_obj.insert_many(metadata_docs)

            logger.info(f"✅ Successfully inserted {len(result.inserted_ids)} policy documents")
            logger.info(f"✅ Successfully inserted {len(metadata_result.inserted_ids)} metadata documents")

            return True

        except Exception as e:
            logger.error(f"❌ Error processing and inserting policies: {str(e)}")
            return False
    
    def create_indexes(self):
        """Create additional indexes for efficient querying"""
        try:
            logger.info("Creating database indexes...")
            
            # Indexes for policy collection
            self.collection.create_index("policy_id", unique=True)
            self.collection.create_index("policy_metadata.category")
            self.collection.create_index("policy_metadata.eligibility_age_min")
            self.collection.create_index("policy_metadata.eligibility_age_max")
            self.collection.create_index("policy_metadata.data_completeness_score")
            
            # Indexes for metadata collection
            self.metadata_collection_obj.create_index("policy_id", unique=True)
            self.metadata_collection_obj.create_index("category")
            self.metadata_collection_obj.create_index([("eligibility_age_min", 1), ("eligibility_age_max", 1)])
            
            logger.info("✅ Database indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {str(e)}")
            return False
    
    def test_vector_search(self, query: str, limit: int = 3):
        """Test vector search functionality"""
        try:
            logger.info(f"Testing vector search with query: '{query}'")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Perform similarity search using aggregation
            pipeline = [
                {
                    "$addFields": {
                        "similarity": {
                            "$reduce": {
                                "input": {"$range": [0, len(query_embedding)]},
                                "initialValue": 0,
                                "in": {
                                    "$add": [
                                        "$$value",
                                        {"$multiply": [
                                            {"$arrayElemAt": ["$embedding", "$$this"]},
                                            query_embedding[{"$toInt": "$$this"}] if isinstance(query_embedding[0], (int, float)) else 0
                                        ]}
                                    ]
                                }
                            }
                        }
                    }
                },
                {"$sort": {"similarity": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "policy_id": 1,
                        "policy_metadata.policy_name": 1,
                        "policy_metadata.category": 1,
                        "similarity": 1,
                        "features_benefits": 1
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            logger.info(f"✅ Found {len(results)} similar policies")
            for i, result in enumerate(results, 1):
                logger.info(f"{i}. {result['policy_metadata']['policy_name']} (Similarity: {result.get('similarity', 0):.3f})")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error testing vector search: {str(e)}")
            return []
    
    def get_database_stats(self):
        """Get statistics about the knowledge base"""
        try:
            stats = {
                "total_policies": self.collection.count_documents({}),
                "categories": list(self.collection.distinct("policy_metadata.category")),
                "age_ranges": list(self.collection.distinct("policy_metadata.eligibility_age_min")),
                "database_size_mb": self.db.command("dbStats")["dataSize"] / (1024 * 1024),
                "indexes": len(list(self.collection.list_indexes()))
            }
            
            logger.info("📊 Database Statistics:")
            logger.info(f"   Total Policies: {stats['total_policies']}")
            logger.info(f"   Categories: {len(stats['categories'])}")
            logger.info(f"   Database Size: {stats['database_size_mb']:.2f} MB")
            logger.info(f"   Indexes: {stats['indexes']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {str(e)}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")


def main():
    """Main function to create the vector knowledge base"""
    # Configuration
    MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    CSV_FILE_PATH = "data/enhanced_lic_policies_vector_db.csv"
    
    # Initialize knowledge base
    kb = LICVectorKnowledgeBase(MONGODB_URI)
    
    try:
        # Step 1: Connect to MongoDB
        if not kb.connect_to_mongodb():
            return
        
        # Step 2: Load LIC data
        df = kb.load_lic_data(CSV_FILE_PATH)
        if df is None:
            return
        
        # Step 3: Process and insert policies
        if not kb.process_and_insert_policies(df):
            return
        
        # Step 4: Create indexes
        if not kb.create_indexes():
            return
        
        # Step 5: Create vector search index (manual step)
        kb.create_vector_search_index()
        
        # Step 6: Test the system
        test_queries = [
            "child education planning policy",
            "retirement planning with guaranteed returns",
            "term insurance for young family"
        ]
        
        for query in test_queries:
            kb.test_vector_search(query)
        
        # Step 7: Get database statistics
        kb.get_database_stats()
        
        logger.info("🎉 Vector knowledge base created successfully!")
        logger.info("📝 Next steps:")
        logger.info("   1. Create vector search index in MongoDB Atlas UI")
        logger.info("   2. Test RAG queries using the search functionality")
        logger.info("   3. Integrate with your recommendation system")
        
    except Exception as e:
        logger.error(f"❌ Error in main execution: {str(e)}")
    
    finally:
        kb.close_connection()


if __name__ == "__main__":
    main()


# Additional utility functions for RAG integration
class LICRAGQueryEngine:
    """
    Query engine for RAG-based policy recommendations
    """

    def __init__(self, kb: LICVectorKnowledgeBase):
        self.kb = kb
        self.embedding_model = kb.embedding_model
        self.collection = kb.collection

    def semantic_search(self, query: str, filters: Dict = None, limit: int = 5) -> List[Dict]:
        """
        Perform semantic search using Atlas Vector Search

        Args:
            query: Natural language query
            filters: Optional filters (age, category, etc.)
            limit: Number of results to return
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Use Atlas Vector Search pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": limit
                    }
                }
            ]

            # Add filters if provided (post-vector search filtering)
            if filters:
                match_conditions = {}
                if 'age' in filters:
                    age = filters['age']
                    match_conditions['policy_metadata.eligibility_age_min'] = {'$lte': age}
                    match_conditions['policy_metadata.eligibility_age_max'] = {'$gte': age}

                if 'category' in filters:
                    match_conditions['policy_metadata.category'] = filters['category']

                if match_conditions:
                    pipeline.append({'$match': match_conditions})

            # Add projection
            pipeline.append({
                '$project': {
                    'policy_id': 1,
                    'policy_metadata': 1,
                    'features_benefits': 1,
                    'maturity_benefits': 1,
                    'tax_benefits': 1,
                    'similarity_score': {"$meta": "vectorSearchScore"}
                }
            })

            results = list(self.collection.aggregate(pipeline))
            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    def get_policy_recommendations(self, user_profile: Dict) -> List[Dict]:
        """
        Get policy recommendations based on user profile

        Args:
            user_profile: Dictionary containing user information
        """
        try:
            # Build query based on user profile
            query_parts = []

            if user_profile.get('primary_goal'):
                goal_mapping = {
                    'wealth_creation': 'protection savings guaranteed returns endowment',
                    'child_education': 'child education money back survival benefits',
                    'retirement_planning': 'pension retirement survival benefits annuity',
                    'family_protection': 'death benefit protection term insurance',
                    'tax_saving': 'tax benefits section 80C deductions'
                }
                query_parts.append(goal_mapping.get(user_profile['primary_goal'], ''))

            if user_profile.get('risk_comfort'):
                risk_mapping = {
                    'conservative': 'guaranteed returns endowment traditional',
                    'moderate': 'money back survival benefits balanced',
                    'aggressive': 'unit linked market investment'
                }
                query_parts.append(risk_mapping.get(user_profile['risk_comfort'], ''))

            if user_profile.get('life_stage'):
                stage_mapping = {
                    'single': 'basic protection term insurance',
                    'young_family': 'family protection child benefits',
                    'established_family': 'comprehensive coverage education planning',
                    'pre_retirement': 'pension retirement planning'
                }
                query_parts.append(stage_mapping.get(user_profile['life_stage'], ''))

            query = ' '.join(query_parts)

            # Build filters
            filters = {}
            if user_profile.get('age'):
                filters['age'] = user_profile['age']

            # Perform search
            results = self.semantic_search(query, filters, limit=5)

            # Add recommendation scores based on user profile
            for result in results:
                result['recommendation_score'] = self._calculate_recommendation_score(
                    result, user_profile
                )

            # Sort by recommendation score
            results.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)

            return results[:3]  # Return top 3 recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def _calculate_recommendation_score(self, policy: Dict, user_profile: Dict) -> float:
        """Calculate recommendation score based on user profile match"""
        score = 0.0

        # Age eligibility (mandatory)
        if user_profile.get('age'):
            age = user_profile['age']
            min_age = policy['policy_metadata'].get('eligibility_age_min', 0)
            max_age = policy['policy_metadata'].get('eligibility_age_max', 100)

            if min_age <= age <= max_age:
                score += 40  # High weight for age eligibility
            else:
                return 0  # Disqualify if age ineligible

        # Goal alignment
        goal_keywords = {
            'wealth_creation': ['protection', 'savings', 'guaranteed', 'endowment'],
            'child_education': ['child', 'education', 'money back', 'survival'],
            'retirement_planning': ['pension', 'retirement', 'annuity'],
            'family_protection': ['death benefit', 'protection', 'term'],
            'tax_saving': ['tax', '80C', 'deduction']
        }

        if user_profile.get('primary_goal'):
            keywords = goal_keywords.get(user_profile['primary_goal'], [])
            features = policy.get('features_benefits', '').lower()

            matches = sum(1 for keyword in keywords if keyword in features)
            score += (matches / len(keywords)) * 30 if keywords else 0

        # Risk comfort alignment
        risk_indicators = {
            'conservative': ['guaranteed', 'traditional', 'endowment'],
            'moderate': ['money back', 'balanced', 'survival'],
            'aggressive': ['unit linked', 'market', 'investment']
        }

        if user_profile.get('risk_comfort'):
            indicators = risk_indicators.get(user_profile['risk_comfort'], [])
            features = policy.get('features_benefits', '').lower()

            matches = sum(1 for indicator in indicators if indicator in features)
            score += (matches / len(indicators)) * 20 if indicators else 0

        # Data completeness bonus
        completeness = policy['policy_metadata'].get('data_completeness_score', 0)
        score += completeness * 10

        return score


# Example usage function
def example_rag_usage():
    """Example of how to use the RAG system"""

    # Initialize knowledge base
    kb = LICVectorKnowledgeBase(
        "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    )

    if not kb.connect_to_mongodb():
        return

    # Initialize RAG query engine
    rag_engine = LICRAGQueryEngine(kb)

    # Example user profile
    user_profile = {
        "age": 32,
        "monthly_income": 75000,
        "life_stage": "young_family",
        "dependents": 2,
        "primary_goal": "child_education",
        "risk_comfort": "moderate",
        "decision_style": "research_heavy",
        "timeline": "within_3_months"
    }

    # Get recommendations
    recommendations = rag_engine.get_policy_recommendations(user_profile)

    print("🎯 Policy Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['policy_metadata']['policy_name']}")
        print(f"   Score: {rec.get('recommendation_score', 0):.1f}/100")
        print(f"   Category: {rec['policy_metadata']['category']}")
        print(f"   Features: {rec['features_benefits'][:100]}...")

    kb.close_connection()


if __name__ == "__main__":
    # Uncomment to run example
    # example_rag_usage()
    pass
