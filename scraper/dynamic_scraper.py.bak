#!/usr/bin/env python3
"""
Dynamic Job Scraper - Refactored to use a professional scraping API
Scrapes real jobs from multiple sources using CV-derived keywords
"""

import os
import requests
import time
import random
from typing import List, Dict
import re
from urllib.parse import quote_plus
import json

class DynamicJobScraper:
    """
    Completely dynamic job scraper based on CV analysis.
    Refactored to use a scraping API for robustness and to avoid getting blocked.
    """

    def __init__(self):
        """Initializes the scraper and gets API credentials from environment variables."""
        self.api_user = os.getenv("OXY_USER")
        self.api_pass = os.getenv("OXY_PASS")
        if not self.api_user or not self.api_pass:
            raise ValueError("Scraping API credentials (OXY_USER, OXY_PASS) were not found in environment variables.")

    def _scrape_target_with_api(self, target_url: str) -> List[Dict]:
        """
        A single, reusable function to scrape any URL using a professional scraping API.
        This replaces all previous requests/Selenium logic.
        """
        api_endpoint = "https://realtime.oxylabs.io/v1/queries"
        
        # The payload sent to the scraping API.
        # 'parse': True tells the API to try and return structured JSON data, not just raw HTML.
        payload = {
            'source': 'universal',
            'url': target_url,
            'geo_location': 'GB',  # Ensure we get UK-based results
            'parse': True
        }

        print(f"📡 Sending API request to scrape: {target_url}")
        try:
            response = requests.post(
                api_endpoint,
                auth=(self.api_user, self.api_pass),
                json=payload,
                timeout=180  # Increase timeout for complex pages that require parsing
            )
            # Raise an exception for bad status codes (4xx client errors, 5xx server errors)
            response.raise_for_status()

            print(f"✅ API Response OK.")
            # The API response nests the actual data inside a 'results' key
            return response.json().get('results', [])

        except requests.exceptions.Timeout:
            print(f"❌ API request timed out for {target_url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API Request Failed: {e}")
            return None

    def _parse_api_results(self, api_results: List[Dict], source: str) -> List[Dict]:
        """
        Parses the JSON response from the scraping API into our desired job format.
        """
        jobs = []
        if not api_results:
            return jobs

        # The API returns a list, the main parsed content is usually in the first item
        parsed_data = api_results[0].get('content', {})
        # The actual list of jobs is often under a key like 'jobs', 'results', or 'items'
        job_listings = parsed_data.get('jobs', parsed_data.get('results', []))

        if not job_listings:
            print(f"⚠️  API returned data, but no job listings found in the parsed content for {source}.")
            return jobs

        for item in job_listings:
            job = {
                "title": item.get('title', 'N/A'),
                "company": item.get('company_name', 'N/A'),
                "location": item.get('location', 'UK'),
                "salary": item.get('salary', 'Competitive'),
                "description": item.get('description', item.get('snippet', ''))[:300],
                "url": item.get('url', ''),
                "posted_date": item.get('posted_at', 'Recent'),
                "source": source
            }
            jobs.append(job)
        
        return jobs

    def extract_search_terms_from_cv(self, cv_analysis: dict) -> Dict[str, List[str]]:
        """
        Extract dynamic search terms from CV analysis.
        This well-designed function is kept from the original code.
        """
        # ... (This entire function remains unchanged from your original code) ...
        skills = cv_analysis.get("skills", [])
        industry = cv_analysis.get("primary_industry", "general")
        experience_level = cv_analysis.get("experience_level", "mid")
        search_terms = { "job_titles": [], "skills_keywords": skills[:8], "industry_terms": [], "experience_terms": [] }
        if industry in ["sales", "sales_business_development", "business_development"]:
            base_titles = [ "sales", "business development", "account manager", "sales manager", "sales executive", "client relationship manager", "key account manager", "sales representative", "commercial manager" ]
        elif industry in ["marketing", "digital_marketing"]:
            base_titles = [ "marketing", "digital marketing", "marketing manager", "marketing executive", "brand manager", "product marketing manager", "content manager", "communications manager" ]
        elif industry in ["finance", "fintech"]:
            base_titles = [ "financial analyst", "finance", "accounting", "accountant", "finance manager", "management accountant", "financial controller", "auditor" ]
        elif industry in ["tech", "software", "engineering", "blockchain"]:
            base_titles = [ "developer", "engineer", "software engineer", "software developer", "programmer", "it support", "systems administrator", "devops engineer", "data scientist", "data analyst", "machine learning engineer" ]
        else:
            base_titles = [ "analyst", "coordinator", "specialist", "manager", "consultant", "project manager", "operations manager", "administrator", "executive assistant" ]
        processed_titles = set()
        for title in base_titles: processed_titles.add(title)
        if experience_level == "senior":
            for title in base_titles:
                processed_titles.add(f"senior {title}")
                processed_titles.add(f"lead {title}")
            search_terms["experience_terms"] = ["senior", "lead", "principal"]
        elif experience_level == "junior":
            for title in base_titles:
                processed_titles.add(f"junior {title}")
                processed_titles.add(f"graduate {title}")
            search_terms["experience_terms"] = ["junior", "graduate", "entry level"]
        else:
            search_terms["experience_terms"] = ["mid level", "experienced"]
        search_terms["job_titles"] = list(processed_titles)[:15]
        search_terms["industry_terms"] = [industry.replace("_", " ")]
        print(f"🎯 Dynamic search terms generated:")
        print(f"   Job Titles: {search_terms['job_titles'][:5]}")
        return search_terms

    def scrape_dynamic_jobs(self, cv_analysis: dict, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs dynamically by calling the respective API-based scraper methods."""
        search_terms = self.extract_search_terms_from_cv(cv_analysis)
        all_jobs = []

        sources = [
            ("Indeed UK", self.scrape_indeed_dynamic),
            ("Reed UK", self.scrape_reed_dynamic),
            ("LinkedIn", self.scrape_linkedin_dynamic),
            # Add other sources here as you implement them
        ]

        for source_name, scrape_func in sources:
            if len(all_jobs) >= max_jobs:
                break
            try:
                jobs = scrape_func(search_terms, max_jobs - len(all_jobs))
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"✅ {source_name}: {len(jobs)} jobs found and processed.")
                time.sleep(1) # Small delay between API calls
            except Exception as e:
                print(f"❌ Scraping function for {source_name} failed: {e}")
                continue

        return self.deduplicate_jobs(all_jobs)[:max_jobs]

    # --- REFACTORED SCRAPER: INDEED UK ---
    def scrape_indeed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Indeed UK by building a URL and sending it to the scraping API."""
        if not search_terms.get("job_titles"):
            return []
            
        # We can create more sophisticated logic here later, but for now, use the top search terms.
        query = search_terms['job_titles'][0]
        encoded_query = quote_plus(query)
        target_url = f"https://uk.indeed.com/jobs?q={encoded_query}&sort=date"
        
        # The old, complex code is replaced by these two lines:
        api_results = self._scrape_target_with_api(target_url)
        jobs = self._parse_api_results(api_results, "Indeed UK")

        return jobs[:max_jobs]

    # --- PLACEHOLDERS FOR OTHER SCRAPERS ---
    def scrape_reed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        print("ℹ️ Reed scraper not implemented in this version. Skipping.")
        # TODO: Implement this by building a Reed URL and calling _scrape_target_with_api
        return []

    def scrape_linkedin_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        print("ℹ️ LinkedIn scraper not implemented in this version. Skipping.")
        # NOTE: LinkedIn is extremely difficult. Use their official API if possible,
        # or accept that reliable scraping may not be feasible.
        return []

    def scrape_totaljobs_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        print("ℹ️ Totaljobs scraper not implemented in this version. Skipping.")
        # TODO: Implement this by building a Totaljobs URL and calling _scrape_target_with_api
        return []

    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on a key of title + company."""
        seen = set()
        unique_jobs = []
        for job in jobs:
            job_key = f"{job.get('title', '').lower().strip()}-{job.get('company', '').lower().strip()}"
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        return unique_jobs

# Main execution function
def scrape_jobs_dynamically(cv_analysis: dict, max_jobs: int = 50) -> List[Dict]:
    """Main function to scrape jobs dynamically based on CV."""
    print(f"🚀 Starting DYNAMIC job scraping based on CV analysis...")
    scraper = DynamicJobScraper()
    jobs = scraper.scrape_dynamic_jobs(cv_analysis, max_jobs)

    print(f"\n🎯 Dynamic scraping complete!")
    print(f"📊 Found {len(jobs)} relevant jobs")
    if jobs:
        print(f"🏆 Top matches:")
        for i, job in enumerate(jobs[:3]):
            print(f"   {i+1}. {job['title']} at {job['company']} - {job['source']}")
    return jobs

# Test function
def test_dynamic_scraping():
    """Test dynamic scraping with sample CV analysis."""
    sample_cv_analysis = {
        "primary_industry": "sales_business_development",
        "experience_level": "senior",
        "skills": ["sales", "crm", "business development", "account management", "negotiation"],
    }
    jobs = scrape_jobs_dynamically(sample_cv_analysis, max_jobs=20)
    print(f"\n🧪 TEST RESULTS: Found {len(jobs)} jobs in total.")
    # Pretty print the first result if available
    if jobs:
        print("\n--- Example Job Data ---")
        print(json.dumps(jobs[0], indent=2))
    return jobs

if __name__ == "__main__":
    test_dynamic_scraping()
