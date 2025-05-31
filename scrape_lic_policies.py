#!/usr/bin/env python3
"""
LIC Policy Scraper - Main Entry Point
Scrapes all LIC policies and generates enhanced_lic_policies_vector_db.csv
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper.enhanced_comprehensive_scraper import EnhancedLICPolicyScraper
from scraper.config import create_directories

def main():
    """Main function to run the LIC policy scraper"""
    print("🚀 Starting LIC Policy Scraper")
    print("=" * 60)
    
    # Create necessary directories
    create_directories()
    
    # Initialize scraper
    scraper = EnhancedLICPolicyScraper()
    
    try:
        # Run comprehensive scraping for all categories
        print("📊 Running comprehensive policy scraping...")

        from scraper.config import POLICY_CATEGORIES
        import os
        from datetime import datetime

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/LIC_Policies_Enhanced_Comprehensive_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        all_policies = []
        total_policies = 0
        successful_policies = 0

        # Scrape each category
        for category, category_url in POLICY_CATEGORIES.items():
            print(f"\n🔍 Scraping category: {category}")
            print(f"🌐 URL: {category_url}")

            # Get policy links from category
            policy_links = scraper.get_policy_links_from_category(category_url)
            print(f"📋 Found {len(policy_links)} policies in {category}")

            # Scrape each policy
            for policy_info in policy_links:
                total_policies += 1
                print(f"📄 Scraping: {policy_info.get('name', 'Unknown Policy')}")

                policy_data = scraper.scrape_single_policy_comprehensive(policy_info, category)

                if policy_data and policy_data.get('scraped_successfully', False):
                    successful_policies += 1
                    all_policies.append(policy_data)
                    print(f"   ✅ Success - Completeness: {policy_data.get('data_completeness_score', 0):.1f}%")
                else:
                    print(f"   ❌ Failed to scrape policy")

        # Save results
        print(f"\n💾 Saving results...")
        scraper.save_enhanced_results(all_policies, output_dir)

        # Generate summary
        success_rate = (successful_policies / total_policies * 100) if total_policies > 0 else 0

        print(f"✅ Scraping completed successfully!")
        print(f"📁 Output saved to: {output_dir}")
        print(f"📄 CSV file: enhanced_lic_policies_vector_db.csv")
        print(f"📊 Total policies: {total_policies}")
        print(f"🎯 Successful: {successful_policies}")
        print(f"📈 Success rate: {success_rate:.1f}%")

        # Move CSV to data directory
        import shutil
        csv_source = f"{output_dir}/enhanced_lic_policies_vector_db.csv"
        csv_dest = "data/enhanced_lic_policies_vector_db.csv"
        if os.path.exists(csv_source):
            shutil.copy2(csv_source, csv_dest)
            print(f"📋 CSV copied to: {csv_dest}")

        print("\n🎉 LIC Policy scraping completed!")
        print("📝 Next step: Run 'python create_vector_database.py' to create MongoDB vector database")
        return True

    except Exception as e:
        print(f"❌ Error during scraping: {str(e)}")
        return False

    finally:
        scraper.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
