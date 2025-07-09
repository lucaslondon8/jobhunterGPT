import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict
import os

# Assuming you have a separate file for the Adzuna API client
# from .adzuna_client import AdzunaAPI 

class DynamicJobScraper:
    def __init__(self):
        # self.adzuna_api = AdzunaAPI() # Your Adzuna client
        # For demonstration, we'll mock the Adzuna part if it's not in a separate file
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna API credentials not found.")

    async def _get_email_from_page(self, context, url: str) -> str | None:
        """Uses a real browser page to find an email address."""
        try:
            page = await context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            html = await page.content()
            await page.close()

            soup = BeautifulSoup(html, 'html.parser')
            page_text = soup.get_text()

            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails_found = re.findall(email_pattern, page_text)

            if emails_found:
                # Filter out common false positives from image URLs or examples
                for email in emails_found:
                    if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                        return email
            return None
        except Exception as e:
            # print(f"Could not scrape email from {url}: {e}")
            if 'page' in locals() and not page.is_closed():
                await page.close()
            return None

    def _parse_adzuna_results(self, api_response: Dict) -> List[Dict]:
        """Parses the JSON response from Adzuna."""
        jobs = []
        for item in api_response.get('results', []):
            job = {
                "id": item.get('id'),
                "title": item.get('title'),
                "company": item.get('company', {}).get('display_name'),
                "location": item.get('location', {}).get('display_name'),
                "description": item.get('description'),
                "url": item.get('redirect_url'),
                "source": "Adzuna",
                "contact_email": None
            }
            jobs.append(job)
        return jobs

    async def scrape_jobs_with_keywords(self, keywords: List[str], max_jobs: int = 50) -> List[Dict]:
        """Queries Adzuna, then uses Playwright to scrape each page for a contact email."""
        all_jobs = []
        
        # This section for fetching jobs from Adzuna remains the same.
        # It needs an async http client, which we can create temporarily.
        import httpx
        async with httpx.AsyncClient() as adzuna_client:
            api_url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
            adzuna_tasks = []
            for keyword in keywords[:5]:
                params = {
                    'app_id': self.app_id, 'app_key': self.app_key, 'what': keyword,
                    'where': 'uk', 'results_per_page': 10, 'content-type': 'application/json'
                }
                adzuna_tasks.append(adzuna_client.get(api_url, params=params))
            
            print("🚀 Launching Adzuna API queries...")
            responses = await asyncio.gather(*adzuna_tasks, return_exceptions=True)
            for response in responses:
                if isinstance(response, httpx.Response) and response.status_code == 200:
                    all_jobs.extend(self._parse_adzuna_results(response.json()))

        # --- STAGE 2: Use Playwright to find emails ---
        if not all_jobs:
            print("No jobs found from Adzuna.")
            return []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            
            print(f"📧 Scraping {len(all_jobs)} job pages for contact emails with Playwright...")
            email_tasks = [self._get_email_from_page(context, job['url']) for job in all_jobs]
            scraped_emails = await asyncio.gather(*email_tasks, return_exceptions=True)

            await browser.close()

            # Add the found emails back to our job objects
            for i, email in enumerate(scraped_emails):
                if isinstance(email, str):
                    all_jobs[i]['contact_email'] = email
        
        print(f"Found {len(all_jobs)} jobs. Email scraping complete.")
        return all_jobs[:max_jobs]
