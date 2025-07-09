# test_scraper.py
import asyncio
import re
import sys
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_single_url(url: str):
    """
    Launches a browser, visits a single URL, and prints any emails found.
    """
    print(f"--- Testing URL: {url} ---")
    
    if not url.startswith('http'):
        print("❌ Error: Invalid URL provided. Please include http:// or https://")
        return

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            print("➡️ Navigating to page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            
            print("➡️ Page loaded. Extracting content...")
            html = await page.content()
            
            await browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            page_text = soup.get_text()

            # Regex to find email addresses
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails_found = re.findall(email_pattern, page_text)

            print("-" * 20)
            if emails_found:
                print(f"✅ SUCCESS: Found {len(emails_found)} potential email(s):")
                # Filter out common false positives from image URLs or examples
                for i, email in enumerate(emails_found):
                    if not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                        print(f"  {i+1}: {email}")
                    else:
                        print(f"  {i+1}: (Filtered out as likely image file) {email}")

            else:
                print("🤷‍♂️ No emails found on this page.")
            print("-" * 20)

        except Exception as e:
            print(f"\n❌ An error occurred during scraping: {e}")
            if 'browser' in locals() and browser.is_connected():
                await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_scraper.py <URL_TO_TEST>")
    else:
        target_url = sys.argv[1]
        asyncio.run(test_single_url(target_url))

