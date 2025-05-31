#!/usr/bin/env python3
"""
Dashboard Setup Script
Automated setup and verification for the LIC Policy Recommendation Dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def check_environment_variables():
    """Check required environment variables"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = ["GROQ_API_KEY"]
    optional_vars = ["GOOGLE_API_KEY", "GOOGLE_CSE_ID"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {missing_required}")
        print("\nPlease set them using:")
        for var in missing_required:
            print(f"export {var}='your_{var.lower()}_here'")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional environment variables: {missing_optional}")
        print("These are not required but enable enhanced features.")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def verify_mongodb_connection():
    """Verify MongoDB Atlas connection"""
    print("\n🗄️ Verifying MongoDB Atlas connection...")
    
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.vector_db.mongodb_vector_knowledge_base import LICVectorKnowledgeBase
        
        # Test connection
        mongodb_uri = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
        kb = LICVectorKnowledgeBase(mongodb_uri)
        
        if kb.connect_to_mongodb():
            print("✅ MongoDB Atlas connection successful")
            
            # Check if policies are loaded
            stats = kb.get_database_stats()
            policy_count = stats.get('total_policies', 0)
            
            if policy_count > 0:
                print(f"✅ Found {policy_count} policies in database")
            else:
                print("⚠️ No policies found in database. Run 'python create_vector_database.py' first.")
            
            kb.close_connection()
            return True
        else:
            print("❌ MongoDB Atlas connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying MongoDB connection: {str(e)}")
        return False

def verify_groq_api():
    """Verify Groq API connection"""
    print("\n🤖 Verifying Groq API connection...")
    
    try:
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found")
            return False
        
        client = Groq(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        if response.choices:
            print("✅ Groq API connection successful")
            return True
        else:
            print("❌ Groq API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying Groq API: {str(e)}")
        return False

def create_streamlit_secrets():
    """Create Streamlit secrets file for deployment"""
    print("\n🔐 Creating Streamlit secrets file...")
    
    secrets_dir = Path(".streamlit")
    secrets_dir.mkdir(exist_ok=True)
    
    secrets_file = secrets_dir / "secrets.toml"
    
    groq_key = os.getenv("GROQ_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    google_cse = os.getenv("GOOGLE_CSE_ID", "")
    
    secrets_content = f'''# Streamlit Secrets Configuration
# This file is used for Streamlit Cloud deployment

GROQ_API_KEY = "{groq_key}"
GOOGLE_API_KEY = "{google_key}"
GOOGLE_CSE_ID = "{google_cse}"

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/"
'''
    
    try:
        with open(secrets_file, 'w') as f:
            f.write(secrets_content)
        print(f"✅ Streamlit secrets file created: {secrets_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating secrets file: {str(e)}")
        return False

def run_dashboard_test():
    """Run a quick dashboard test"""
    print("\n🧪 Running dashboard test...")
    
    try:
        # Import dashboard components
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.dashboard.config import DashboardConfig
        from src.dashboard.user_profile import UserProfileCollector
        from src.dashboard.recommendation_engine import DashboardRecommendationEngine
        
        # Test configuration
        config = DashboardConfig()
        if not config.validate_config():
            print("❌ Dashboard configuration validation failed")
            return False
        
        print("✅ Dashboard components loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🏛️ LIC Policy Recommendation Dashboard Setup")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_environment_variables),
        ("Dependencies", install_dependencies),
        ("MongoDB Connection", verify_mongodb_connection),
        ("Groq API", verify_groq_api),
        ("Streamlit Secrets", create_streamlit_secrets),
        ("Dashboard Test", run_dashboard_test)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("\n🚀 Ready to launch dashboard:")
        print("   streamlit run streamlit_dashboard.py")
        print("\n📖 Access dashboard at: http://localhost:8501")
    else:
        print(f"\n⚠️ Setup incomplete. Please fix the failed checks above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
