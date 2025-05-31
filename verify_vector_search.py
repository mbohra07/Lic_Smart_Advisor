#!/usr/bin/env python3
"""
Vector Search Verification - Main Entry Point
Verifies that MongoDB Atlas vector search is working correctly
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vector_db.verify_vector_search_index import VectorSearchVerifier

def main():
    """Main function to verify vector search setup"""
    print("🔍 Verifying MongoDB Atlas Vector Search Setup")
    print("=" * 60)
    
    # Configuration
    MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
    
    # Initialize verifier
    verifier = VectorSearchVerifier(MONGODB_URI)
    
    try:
        # Run comprehensive verification
        success = verifier.run_comprehensive_verification()
        
        if success:
            print("\n🎯 VERIFICATION SUCCESSFUL!")
            print("✅ Your vector search index is working perfectly")
            print("🚀 Ready for production use!")
            print("\n📝 Next steps:")
            print("   1. Integrate with your application")
            print("   2. Test with real user queries")
            print("   3. Monitor performance and user satisfaction")
        else:
            print("\n❌ VERIFICATION FAILED")
            print("Please check the error messages above and:")
            print("1. Verify your Atlas search index configuration")
            print("2. Ensure the index is in 'Ready' status")
            print("3. Check index name matches 'vector_index'")
        
        return success
        
    except Exception as e:
        print(f"❌ Verification failed with error: {str(e)}")
        return False
    
    finally:
        verifier.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
