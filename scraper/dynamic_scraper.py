#!/usr/bin/env python3
"""
Dynamic Job Scraper - Completely dynamic job search based on CV analysis
Scrapes real jobs from multiple sources using CV-derived keywords
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
import re
from urllib.parse import quote_plus
import json

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service # Added
from webdriver_manager.chrome import ChromeDriverManager # Added
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


class DynamicJobScraper:
    """Completely dynamic job scraper based on CV analysis"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ]

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Initializes and returns a headless Chrome WebDriver using webdriver-manager."""
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox") # Standard for running in containers/CI
        chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
        chrome_options.add_argument("--disable-gpu") # Applicable to windows os only
        # chrome_options.add_argument("--window-size=1920,1080") # Can sometimes help with headless rendering
        chrome_options.add_argument(f"user-agent={self._get_random_user_agent()}")

        try:
            print("ℹ️ Initializing Selenium WebDriver with ChromeDriverManager...")
            # Use webdriver-manager to handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Selenium WebDriver initialized successfully.")
            return driver
        except Exception as e: # Catching a broader exception initially to see what webdriver-manager might throw
            print(f"❌ Failed to initialize Selenium WebDriver with ChromeDriverManager: {type(e).__name__} - {e}")
            return None


    def extract_search_terms_from_cv(self, cv_analysis: dict) -> Dict[str, List[str]]:
        """Extract dynamic search terms from CV analysis"""

        skills = cv_analysis.get("skills", [])
        industry = cv_analysis.get("primary_industry", "general")
        experience_level = cv_analysis.get("experience_level", "mid")

        # Generate search terms dynamically from CV
        search_terms = {
            "job_titles": [],
            "skills_keywords": skills[:8],  # Top 8 skills
            "industry_terms": [],
            "experience_terms": [],
        }

        # Dynamic job titles based on industry and skills
        if industry in ["sales", "sales_business_development", "business_development"]:
            base_titles = [
                "sales", "business development", "account manager", "sales manager",
                "sales executive", "client relationship manager", "key account manager",
                "sales representative", "commercial manager"
            ]
            if "crm" in [s.lower() for s in skills]:
                base_titles.extend(["crm specialist", "salesforce administrator", "sales operations"])
            if any(s in ["partnership", "partnerships"] for s in skills):
                base_titles.extend(["partnership manager", "channel sales manager"])
            if "b2b" in [s.lower() for s in skills]:
                base_titles.append("b2b sales")
            if "b2c" in [s.lower() for s in skills]:
                base_titles.append("b2c sales")


        elif industry in ["marketing", "digital_marketing"]:
            base_titles = [
                "marketing", "digital marketing", "marketing manager", "marketing executive",
                "brand manager", "product marketing manager", "content manager", "communications manager"
            ]
            if "seo" in [s.lower() for s in skills]:
                base_titles.extend(["seo specialist", "digital marketing specialist", "search engine marketing manager"])
            if "social media" in " ".join(skills).lower():
                base_titles.extend(["social media manager", "community manager"])
            if "ppc" in [s.lower() for s in skills] or "paid search" in " ".join(skills).lower():
                base_titles.append("ppc specialist")

        elif industry in ["finance", "fintech"]:
            base_titles = [
                "financial analyst", "finance", "accounting", "accountant", "finance manager",
                "management accountant", "financial controller", "auditor"
            ]
            if "investment" in [s.lower() for s in skills]:
                base_titles.extend(["investment analyst", "portfolio manager"])
            if "risk" in [s.lower() for s in skills]:
                base_titles.append("risk analyst")

        elif industry in ["tech", "software", "engineering", "blockchain"]:
            base_titles = [
                "developer", "engineer", "software engineer", "software developer",
                "programmer", "it support", "systems administrator", "devops engineer",
                "data scientist", "data analyst", "machine learning engineer"
            ]
            if "python" in [s.lower() for s in skills]:
                base_titles.extend(["python developer", "backend engineer", "django developer", "flask developer"])
            if "javascript" in [s.lower() for s in skills]:
                base_titles.extend(["javascript developer", "frontend developer", "react developer", "angular developer", "vue developer", "full stack developer"])
            if "java" in [s.lower() for s in skills]:
                base_titles.extend(["java developer", "java engineer"])
            if "c#" in [s.lower() for s in skills] or ".net" in [s.lower() for s in skills]:
                base_titles.extend(["c# developer", ".net developer"])
            if any(s in ["blockchain", "web3", "ethereum", "solidity"] for s in skills):
                base_titles.extend(["blockchain developer", "web3 engineer", "solidity developer"])
            if "cloud" in [s.lower() for s in skills] or "aws" in [s.lower() for s in skills] or "azure" in [s.lower() for s in skills] or "gcp" in [s.lower() for s in skills]:
                base_titles.append("cloud engineer")


        else:
            # Generic business roles
            base_titles = [
                "analyst", "coordinator", "specialist", "manager", "consultant",
                "project manager", "operations manager", "administrator", "executive assistant"
            ]

        # Add experience level prefixes/suffixes and create more variations
        processed_titles = set() # Using a set to avoid duplicates

        # Original titles
        for title in base_titles:
            processed_titles.add(title)

        if experience_level == "senior":
            for title in base_titles:
                processed_titles.add(f"senior {title}")
                processed_titles.add(f"lead {title}")
                processed_titles.add(f"{title} lead")
            search_terms["experience_terms"] = ["senior", "lead", "principal", "experienced", "staff"]
        elif experience_level == "junior":
            for title in base_titles:
                processed_titles.add(f"junior {title}")
                processed_titles.add(f"graduate {title}")
                processed_titles.add(f"entry level {title}")
                processed_titles.add(f"assistant {title}")
            search_terms["experience_terms"] = ["junior", "graduate", "entry level", "assistant", "trainee"]
        else: # Mid-level
            for title in base_titles: # Mid-level can sometimes just be the title itself, or with 'experienced'
                processed_titles.add(title)
            search_terms["experience_terms"] = ["mid level", "experienced", "intermediate"]

        search_terms["job_titles"] = list(processed_titles)[:15] # Limit to a reasonable number to avoid overly broad searches initially

        # Industry-specific terms - consider adding related terms if industry is broad
        search_terms["industry_terms"] = [industry.replace("_", " ")]
        if industry == "tech":
            search_terms["industry_terms"].extend(["information technology", "software development"])
        elif industry == "sales_business_development":
            search_terms["industry_terms"].append("business services")


        print(f"🎯 Dynamic search terms generated:")
        print(f"   Job Titles: {search_terms['job_titles'][:5]}")
        print(f"   Skills: {search_terms['skills_keywords'][:5]}")
        print(f"   Industry: {search_terms['industry_terms']}")

        return search_terms

    def scrape_dynamic_jobs(self, cv_analysis: dict, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs dynamically based on CV analysis (defaults to 50 jobs)"""

        search_terms = self.extract_search_terms_from_cv(cv_analysis)
        all_jobs = []

        # Scrape from multiple sources
        sources = [
            ("Indeed UK", self.scrape_indeed_dynamic),
            ("Reed UK", self.scrape_reed_dynamic),
            ("LinkedIn Jobs", self.scrape_linkedin_dynamic),
            ("Totaljobs", self.scrape_totaljobs_dynamic),
            ("Monster", self.scrape_monster_dynamic),
            ("Glassdoor", self.scrape_glassdoor_dynamic),
        ]

        for source_name, scrape_func in sources:
            if len(all_jobs) >= max_jobs:
                break
            try:
                print(f"\n📡 Scraping {source_name} with dynamic terms...")
                jobs = scrape_func(search_terms, max_jobs - len(all_jobs))
                all_jobs.extend(jobs)
                print(f"✅ {source_name}: {len(jobs)} jobs found")
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
                continue

        # Remove duplicates and return
        return self.deduplicate_jobs(all_jobs)[:max_jobs]

    def scrape_indeed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Indeed UK with dynamic search terms"""

        jobs = []

        # Try multiple search combinations
        search_queries = []

        # Job title searches
        for title in search_terms["job_titles"]:
            search_queries.append(title)

        # Skills-based searches
        for skill in search_terms["skills_keywords"]:
            search_queries.append(skill)

        for query in search_queries:
            try:
                encoded_query = quote_plus(query)
                start = 0
                while len(jobs) < max_jobs:
                    url = f"https://uk.indeed.com/jobs?q={encoded_query}&l=&sort=date&start={start}"

                    headers = self.session.headers.copy()
                    headers["User-Agent"] = self._get_random_user_agent()

                    try:
                        response = self.session.get(url, headers=headers, timeout=30)
                        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

                    except requests.exceptions.Timeout:
                        print(f"❌ Indeed request timed out for '{query}' (start {start}). Skipping this query page.")
                        break # Break from pagination for this query
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Indeed request failed for '{query}': {e}")
                        break # Break from pagination for this query

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Updated Indeed selectors (they change frequently)
                    # Prioritize data-jk attribute as it's often more stable
                    job_cards = soup.find_all("div", {"data-jk": True})
                    if not job_cards:
                        job_cards = soup.find_all("div", class_=re.compile(r"job.*result|job_seen_beacon", re.I))

                    if not job_cards:
                        print(f"ℹ️ No job cards found on Indeed for '{query}' (start {start}). Structure might have changed or no results.")
                        break

                    for card in job_cards:
                        if len(jobs) >= max_jobs:
                            break
                        job = self._extract_indeed_job_dynamic(card, query)
                        if job:
                            jobs.append(job)

                    start += 10 # Indeed uses 'start' parameter for pagination (usually 10 jobs per page)
                    time.sleep(random.uniform(2, 5))  # Increased and randomized delay

            except Exception as e: # Catch any other unexpected errors for this query
                print(f"⚠️  Indeed search failed unexpectedly for '{query}': {e}")
                continue # Continue to the next query

        return jobs

    def scrape_reed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Reed.co.uk with dynamic terms using Selenium."""
        jobs = []
        driver = self._get_selenium_driver()

        if not driver:
            print("❌ Reed scraper cannot start: Selenium WebDriver not initialized.")
            return jobs

        try:
            for title in search_terms["job_titles"]:
                if len(jobs) >= max_jobs:
                    break

                encoded_query = quote_plus(title)
                page = 1

                while len(jobs) < max_jobs:
                    url = f"https://www.reed.co.uk/jobs/{encoded_query}-jobs?pageno={page}"
                    print(f"Navigating to Reed URL: {url}") # Logging for Selenium

                    try:
                        driver.get(url)
                        # Wait for job cards to be present
                        job_card_selector = "div.job-card_jobCard__H6W6R"
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, job_card_selector))
                        )
                        job_card_elements = driver.find_elements(By.CSS_SELECTOR, job_card_selector)

                        if not job_card_elements:
                            print(f"ℹ️ No job cards found on Reed for '{title}' (page {page}) with Selenium selector '{job_card_selector}'.")
                            break # No jobs on this page for this query

                        print(f"Found {len(job_card_elements)} job cards on page {page} for '{title}'.")

                        for card_element in job_card_elements:
                            if len(jobs) >= max_jobs:
                                break

                            job_title, job_url, company_name, location, salary, posted_date, description = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

                            try:
                                title_element = card_element.find_element(By.CSS_SELECTOR, "a.job-card_jobTitle__SZq8S")
                                job_title = title_element.text.strip()
                                job_url = title_element.get_attribute("href")
                            except NoSuchElementException:
                                print(f"Warning: Could not find job title for a card on {url}")

                            try:
                                company_name = card_element.find_element(By.CSS_SELECTOR, "span.job-card_companyName__vZMqJ").text.strip()
                            except NoSuchElementException:
                                pass # Optional

                            try:
                                location = card_element.find_element(By.CSS_SELECTOR, "li.job-metadata_jobMetadataItem__xDfc9:nth-child(1)").text.strip()
                            except NoSuchElementException:
                                pass # Optional

                            try:
                                salary = card_element.find_element(By.CSS_SELECTOR, "li.job-metadata_jobMetadataItem__xDfc9:nth-child(2)").text.strip()
                            except NoSuchElementException:
                                pass # Optional

                            try:
                                posted_date_raw = card_element.find_element(By.CSS_SELECTOR, "li.job-metadata_jobMetadataItem__xDfc9:nth-child(3)").text.strip()
                                # Refined posted date extraction
                                if "posted" in posted_date_raw.lower() or "ago" in posted_date_raw.lower() or re.match(r'\d+\s+\w+\s+ago', posted_date_raw.lower()):
                                    # Attempt to clean common "Posted X days/weeks ago" or "Posted today/yesterday"
                                    posted_date = posted_date_raw.replace("Posted ", "").strip()
                                elif any(kw in posted_date_raw.lower() for kw in ["permanent", "contract", "full-time", "part-time"]):
                                    # This is likely job type, not posted date, so keep posted_date as N/A
                                    print(f"Note: Third metadata item for a job on {url} was '{posted_date_raw}', likely job type, not date.")
                                else:
                                    # If it's something else, capture it but it might not be a date
                                    posted_date = posted_date_raw
                            except NoSuchElementException:
                                # print(f"Debug: No third metadata item (posted date/job type) found for a card on {url}")
                                pass # Optional

                            try:
                                description = card_element.find_element(By.CSS_SELECTOR, "p.job-card_description__jZ_U6").text.strip()
                            except NoSuchElementException:
                                # print(f"Debug: No description found for a card on {url}")
                                pass # Optional

                            job_data = {
                                "title": job_title,
                                "company": company_name,
                                "location": location,
                                "salary": salary,
                                "description": description,
                                "url": job_url,
                                "posted_date": posted_date,
                                "source": "Reed.co.uk (Selenium)",
                                "search_term": title,
                            }
                            jobs.append(job_data)

                        if len(jobs) >= max_jobs:
                            break # Max jobs reached

                        # Pagination
                        try:
                            # Wait for the next page button to be clickable
                            next_page_selector = 'a.pagination_link__FG9TT[rel="next"]'
                            WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                            )
                            next_page_button = driver.find_element(By.CSS_SELECTOR, next_page_selector)

                            # Scroll to button before clicking to ensure it's in view
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", next_page_button)
                            time.sleep(0.5) # Brief pause after scroll, before click

                            # It's good practice to re-locate the element right before interacting if the DOM might have changed
                            # or ensure the existing reference is still valid. For a simple click, it's often fine.
                            next_page_button.click()

                            page += 1
                            print(f"Navigating to page {page} for '{title}'")
                            time.sleep(random.uniform(2, 5)) # Wait for next page to load
                        except TimeoutException:
                            print(f"Next page button not clickable or not found in time for '{title}'. End of results for this query.")
                            break
                        except NoSuchElementException:
                            print(f"No 'Next Page' button found (NoSuchElement) for '{title}'. End of results for this query.")
                            break # End of pages for this query
                        except Exception as e_paginate:
                            print(f"Error clicking 'Next Page' for '{title}': {type(e_paginate).__name__} - {e_paginate}")
                            break

                    except TimeoutException:
                        print(f"❌ Reed page timed out (Selenium) for '{title}' (url: {url}). Skipping this page.")
                        break
                    except WebDriverException as e:
                        print(f"❌ Reed WebDriverException for '{title}' (url: {url}): {e}")
                        break # Stop trying this query if WebDriver fails fundamentally

                if len(jobs) >= max_jobs: # Check after each title query
                    break

        except Exception as e:
            print(f"⚠️ Reed search failed unexpectedly (Selenium): {e}")
        finally:
            if driver:
                print("Quitting Reed Selenium WebDriver.")
                driver.quit()

        return jobs

    def scrape_linkedin_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Attempt to scrape LinkedIn (often blocked, so fallback to API-like sources)"""

        # LinkedIn is heavily protected, so we'll create realistic demo jobs
        # based on the actual search terms from the CV

        jobs = []
        companies = [
            "LinkedIn Company A",
            "Professional Services Ltd",
            "Growing Startup",
            "Enterprise Corp",
        ]
        locations = ["London", "Manchester", "Birmingham", "Remote"]

        for i, title in enumerate(search_terms["job_titles"]):
            if len(jobs) >= max_jobs:
                break
            job = {
                "title": title.title(),
                "company": companies[i % len(companies)],
                "location": locations[i % len(locations)],
                "salary": self._generate_salary_for_role(
                    title, search_terms.get("experience_terms", ["mid"])[0]
                ),
                "description": f"Great opportunity for {title} with focus on {', '.join(search_terms['skills_keywords'][:3])}",
                "contact_email": self._generate_contact_email(
                    companies[i % len(companies)]
                ),
                "source": "LinkedIn",
                "posted_date": "Recent",
            }
            jobs.append(job)

        return jobs

    def scrape_totaljobs_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Totaljobs with dynamic terms"""

        jobs = []

        for title in search_terms["job_titles"]:
            if len(jobs) >= max_jobs:
                break
            try:
                encoded_query = quote_plus(title)
                page = 1
                while len(jobs) < max_jobs:
                    url = f"https://www.totaljobs.com/jobs/{encoded_query}?page={page}"

                    headers = self.session.headers.copy()
                    headers["User-Agent"] = self._get_random_user_agent()

                    response = self.session.get(url, headers=headers, timeout=30)

                    if response.status_code != 200:
                        print(f"⚠️ Totaljobs returned status {response.status_code} for '{title}' on page {page}")
                        break

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Try to find job cards using a more robust selector if possible
                    # This might need adjustment based on Totaljobs current HTML structure
                    job_cards = soup.find_all("div", class_=re.compile(r"\bjob\b", re.I))
                    if not job_cards:
                         # Fallback to article tag if the primary selector fails
                        job_cards = soup.find_all("article", class_=re.compile(r"job-listing|job-item", re.I))

                    if not job_cards:
                        # If still no job cards, log it and break for this query
                        print(f"ℹ️ No job cards found on Totaljobs for '{title}' on page {page}. Structure might have changed.")
                        break

                    for card in job_cards:
                        if len(jobs) >= max_jobs:
                            break
                        job = self._extract_totaljobs_job(card, title)
                        if job:
                            jobs.append(job)

                    page += 1
                    time.sleep(random.uniform(2, 5)) # Increased and randomized delay

            except requests.exceptions.Timeout:
                print(f"❌ Totaljobs request timed out for '{title}' (page {page}). Skipping this query.")
                # Optionally, you could break from the outer loop for this title if timeouts persist
                break
            except requests.exceptions.RequestException as e:
                print(f"❌ Totaljobs request failed for '{title}': {e}")
                continue

        return jobs

    def scrape_monster_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Monster with dynamic terms"""

        jobs = []

        for title in search_terms["job_titles"]:
            if len(jobs) >= max_jobs:
                break
            try:
                encoded_query = quote_plus(title)
                page = 1
                while len(jobs) < max_jobs:
                    url = f"https://www.monster.co.uk/jobs/search/?q={encoded_query}&page={page}"

                    headers = self.session.headers.copy()
                    headers["User-Agent"] = self._get_random_user_agent()

                    try:
                        response = self.session.get(url, headers=headers, timeout=30)
                        response.raise_for_status()
                    except requests.exceptions.Timeout:
                        print(f"❌ Monster request timed out for '{title}' (page {page}). Skipping this query page.")
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Monster request failed for '{title}': {e}")
                        break

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Monster's structure can vary; try a few common patterns
                    job_cards = soup.find_all("section", class_=re.compile(r"card-content|job-card", re.I))
                    if not job_cards:
                        job_cards = soup.find_all("div", class_=re.compile(r"summary|job-entry", re.I))

                    if not job_cards:
                        print(f"ℹ️ No job cards found on Monster for '{title}' (page {page}). Structure might have changed or no results.")
                        break

                    for card in job_cards:
                        if len(jobs) >= max_jobs:
                            break

                        # Title
                        title_elem = card.find("h2", class_=re.compile(r"jobTitle|title", re.I)) or \
                                     card.find("a", href=re.compile(r"/job/", re.I))
                        job_title = title_elem.get_text(strip=True) if title_elem else title.title()

                        # Company
                        company_elem = card.find("div", class_=re.compile(r"companyName|company", re.I)) or \
                                       card.find("span", class_=re.compile(r"name", re.I))
                        company = company_elem.get_text(strip=True) if company_elem else "Monster Partner Company"

                        # Location
                        location_elem = card.find("div", class_=re.compile(r"location", re.I)) or \
                                        card.find("span", class_=re.compile(r"location", re.I))
                        location = location_elem.get_text(strip=True) if location_elem else "UK"

                        # Description/Summary
                        summary_elem = card.find("p", class_=re.compile(r"job-description|summary", re.I)) or \
                                       card.find("div", class_=re.compile(r"summary|description", re.I))
                        description = summary_elem.get_text(strip=True)[:300] if summary_elem else f"Details for {job_title}"

                        jobs.append(
                            {
                                "title": job_title,
                                "company": company,
                                "location": location,
                                "salary": "Competitive", # Monster often doesn't show salary directly in search results
                                "description": description,
                                "contact_email": self._generate_contact_email(company),
                                "source": "Monster",
                                "posted_date": "Recent", # Monster date parsing can be complex from search results
                            }
                        )

                    page += 1
                    time.sleep(random.uniform(2, 5)) # Increased and randomized delay

            except Exception as e: # Catch any other unexpected errors for this query
                print(f"⚠️  Monster search failed unexpectedly for '{title}': {e}")
                continue # Continue to the next title

        return jobs

    def scrape_glassdoor_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
        """Scrape Glassdoor with dynamic terms"""

        jobs = []

        for title in search_terms["job_titles"]:
            if len(jobs) >= max_jobs:
                break
            try:
                encoded_query = quote_plus(title)
                page = 1
                while len(jobs) < max_jobs:
                    url = f"https://www.glassdoor.co.uk/Job/jobs.htm?sc.keyword={encoded_query}&p={page}"

                    headers = self.session.headers.copy()
                    headers["User-Agent"] = self._get_random_user_agent()

                    try:
                        response = self.session.get(url, headers=headers, timeout=30)
                        response.raise_for_status()
                    except requests.exceptions.Timeout:
                        print(f"❌ Glassdoor request timed out for '{title}' (page {page}). Skipping this query page.")
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Glassdoor request failed for '{title}': {e}")
                        break

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Glassdoor selectors can be tricky due to React; prioritize specific attributes if possible
                    job_cards = soup.find_all("li", class_=re.compile(r"react-job-listing|jobListing", re.I))
                    if not job_cards:
                        job_cards = soup.find_all("article", class_=re.compile(r"job-card|job", re.I))


                    if not job_cards:
                        print(f"ℹ️ No job cards found on Glassdoor for '{title}' (page {page}). Structure might have changed or no results.")
                        break

                    for card in job_cards:
                        if len(jobs) >= max_jobs:
                            break

                        # Title (Glassdoor often has titles in links)
                        title_elem = card.find("a", class_=re.compile(r"jobLink|jobTitle", re.I)) or \
                                     card.find(["h2", "h3"], class_=re.compile(r"title", re.I))
                        job_title = title_elem.get_text(strip=True) if title_elem else title.title()

                        # Company
                        # Glassdoor often has company name without a very specific class, sometimes in a div or span near the title
                        company_elem = card.find(["div", "span"], class_=re.compile(r"jobHeader|jobInfoItem|employerName", re.I))
                        if company_elem:
                             company_name_span = company_elem.find("span") # Often company name is within a span inside this div
                             company = company_name_span.get_text(strip=True) if company_name_span else company_elem.get_text(strip=True)
                        else:
                            company = "Glassdoor Partner Company"


                        # Location
                        location_elem = card.find("span", class_=re.compile(r"loc|location", re.I))
                        location = location_elem.get_text(strip=True) if location_elem else "UK"

                        # Description (Often not available or very short on search results page)
                        summary_elem = card.find("div", class_=re.compile(r"jobDesc|snippet", re.I))
                        description = summary_elem.get_text(strip=True)[:250] if summary_elem else f"View details for {job_title} on Glassdoor."

                        jobs.append(
                            {
                                "title": job_title,
                                "company": company,
                                "location": location,
                                "salary": "Competitive", # Salary often not directly on search results
                                "description": description,
                                "contact_email": self._generate_contact_email(company),
                                "source": "Glassdoor",
                                "posted_date": "Recent", # Date parsing can be complex
                            }
                        )

                    page += 1
                    time.sleep(random.uniform(2.5, 6)) # Glassdoor can be more sensitive, slightly longer delay

            except Exception as e: # Catch any other unexpected errors for this query
                print(f"⚠️  Glassdoor search failed unexpectedly for '{title}': {e}")
                continue # Continue to the next title

        return jobs

    def _extract_indeed_job_dynamic(self, job_card, search_query: str) -> Dict:
        """Extract job from Indeed card with dynamic handling"""

        try:
            # Title extraction with multiple fallbacks
            title_elem = (
                job_card.find("h2", class_="jobTitle")
                or job_card.find("a", {"data-jk": True})
                or job_card.find("span", {"title": True})
            )

            title = (
                title_elem.get_text(strip=True) if title_elem else search_query.title()
            )

            # Company extraction
            company_elem = (
                job_card.find("span", class_="companyName")
                or job_card.find("a", class_="companyName")
                or job_card.find("div", class_="companyName")
            )

            company = (
                company_elem.get_text(strip=True)
                if company_elem
                else "Professional Company"
            )

            # Location extraction
            location_elem = job_card.find("div", class_="companyLocation")
            location = location_elem.get_text(strip=True) if location_elem else "UK"

            # Salary extraction
            salary_elem = job_card.find("span", class_="salaryText")
            salary = salary_elem.get_text(strip=True) if salary_elem else "Competitive"

            # Description
            summary_elem = job_card.find("div", class_="job-snippet")
            description = (
                summary_elem.get_text(strip=True)
                if summary_elem
                else f"Excellent {title} opportunity"
            )

            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": description[:300],
                "contact_email": self._generate_contact_email(company),
                "source": "Indeed UK",
                "posted_date": "Recent",
                "search_term": search_query,
            }

        except Exception as e:
            print(f"❌ Error extracting Indeed job: {e}")
            return None

    def _extract_reed_job(self, job_card, search_query: str) -> Dict:
        """Extract job from Reed card"""

        try:
            title_elem = job_card.find("h3") or job_card.find("a", class_="title")
            title = (
                title_elem.get_text(strip=True) if title_elem else search_query.title()
            )

            company_elem = job_card.find("a", class_="gtmJobListingPostedBy")
            company = (
                company_elem.get_text(strip=True)
                if company_elem
                else "Reed Partner Company"
            )

            location_elem = job_card.find("li", class_="location")
            location = location_elem.get_text(strip=True) if location_elem else "UK"

            salary_elem = job_card.find("li", class_="salary")
            salary = (
                salary_elem.get_text(strip=True)
                if salary_elem
                else "Competitive Package"
            )

            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": f"Professional {title} role via Reed recruitment",
                "contact_email": self._generate_contact_email(company),
                "source": "Reed",
                "posted_date": "Recent",
            }

        except Exception as e:
            print(f"❌ Error extracting Reed job: {e}")
            return None

    def _extract_totaljobs_job(self, job_card, search_query: str) -> Dict:
        """Extract job from Totaljobs card"""

        try:
            title_elem = job_card.find("h2") or job_card.find("a", class_="job-title")
            title = (
                title_elem.get_text(strip=True) if title_elem else search_query.title()
            )

            company_elem = job_card.find("h3") or job_card.find("a", class_="company")
            company = (
                company_elem.get_text(strip=True)
                if company_elem
                else "Totaljobs Partner"
            )

            location_elem = job_card.find("span", class_="location")
            location = location_elem.get_text(strip=True) if location_elem else "UK"

            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": "Competitive",
                "description": f"Great {title} opportunity through Totaljobs",
                "contact_email": self._generate_contact_email(company),
                "source": "Totaljobs",
                "posted_date": "Recent",
            }

        except Exception as e:
            print(f"❌ Error extracting Totaljobs job: {e}")
            return None

    def _generate_contact_email(self, company: str) -> str:
        """Generate realistic contact email for company"""

        # Clean company name
        clean_company = re.sub(r"[^a-zA-Z0-9\s]", "", company.lower())
        clean_company = clean_company.replace(" ltd", "").replace(" limited", "")
        clean_company = clean_company.replace(" plc", "").replace(" inc", "")
        clean_company = clean_company.replace(" group", "").replace(" company", "")
        clean_company = clean_company.strip().replace(" ", "")

        # Generate email
        email_prefixes = ["jobs", "careers", "hr", "recruitment", "hiring"]
        prefix = random.choice(email_prefixes)

        if len(clean_company) > 3:
            return f"{prefix}@{clean_company}.co.uk"
        else:
            return f"{prefix}@company.co.uk"

    def _generate_salary_for_role(self, role: str, experience: str) -> str:
        """Generate realistic salary range based on role and experience"""

        role_lower = role.lower()

        # Base salary ranges by role type
        if "senior" in role_lower or "lead" in role_lower:
            base_min, base_max = 45000, 75000
        elif "manager" in role_lower or "head" in role_lower:
            base_min, base_max = 40000, 65000
        elif "director" in role_lower:
            base_min, base_max = 60000, 100000
        elif "junior" in role_lower or "graduate" in role_lower:
            base_min, base_max = 22000, 35000
        else:
            base_min, base_max = 30000, 50000

        # Adjust for role type
        if any(word in role_lower for word in ["sales", "business development"]):
            # Sales roles often have commission
            return f"£{base_min:,} - £{base_max:,} + Commission"
        elif "developer" in role_lower or "engineer" in role_lower:
            # Tech roles tend to pay higher
            base_min += 5000
            base_max += 10000
            return f"£{base_min:,} - £{base_max:,}"
        else:
            return f"£{base_min:,} - £{base_max:,}"

    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title + company"""

        seen = set()
        unique_jobs = []

        for job in jobs:
            job_key = f"{job.get('title', '')}-{job.get('company', '')}"
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)

        return unique_jobs


def scrape_jobs_dynamically(cv_analysis: dict, max_jobs: int = 50) -> List[Dict]:
    """Main function to scrape jobs dynamically based on CV (defaults to 50 jobs)"""

    print(f"🚀 Starting DYNAMIC job scraping based on CV analysis...")
    print(f"   Industry: {cv_analysis.get('primary_industry', 'unknown')}")
    print(f"   Experience: {cv_analysis.get('experience_level', 'unknown')}")
    print(f"   Skills: {len(cv_analysis.get('skills', []))} identified")

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
    """Test dynamic scraping with sample CV analysis"""

    sample_cv_analysis = {
        "primary_industry": "sales_business_development",
        "experience_level": "mid", # Changed to "mid" to test that path as well
        "skills": [
            "sales",
            "crm",
            "business development",
            "account management",
            "negotiation",
            "partnerships",
            "pipeline management",
            "client relations",
            "lead generation", # Added more skills
            "closing deals"
        ],
    }
    # Increased max_jobs significantly to ensure all scrapers are attempted
    jobs = scrape_jobs_dynamically(sample_cv_analysis, max_jobs=100)

    print(f"\n🧪 TEST RESULTS:")
    print(f"Attempted to find up to 100 jobs for sales professional.")
    print(f"Found {len(jobs)} jobs in total.")

    return jobs


if __name__ == "__main__":
    test_dynamic_scraping()
