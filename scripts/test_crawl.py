import os
import sys
import json
import psutil
import asyncio
import requests
from xml.etree import ElementTree
from typing import List
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Define output JSON file location
__location__ = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON_FILE = os.path.join(__location__, "crawled_data.json")

def extract_html_elements(html_content: str):
    """Extracts structured elements from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract metadata
    metadata = {meta.get("name", meta.get("property", "")): meta.get("content", "")
                for meta in soup.find_all("meta") if meta.get("content")}

    # Extract headings (h1-h6)
    headings = {f"h{level}": [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]
                for level in range(1, 7)}

    # Extract paragraphs
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

    # Extract lists (unordered and ordered)
    lists = {
        "unordered": [[li.get_text(strip=True) for li in ul.find_all("li")] for ul in soup.find_all("ul")],
        "ordered": [[li.get_text(strip=True) for li in ol.find_all("li")] for ol in soup.find_all("ol")]
    }

    # Extract links
    links = [{"text": a.get_text(strip=True), "href": a.get("href")} for a in soup.find_all("a") if a.get("href")]

    # Extract images
    images = [{"alt": img.get("alt", ""), "src": img.get("src")} for img in soup.find_all("img") if img.get("src")]

    # Extract tables
    tables = []
    for table in soup.find_all("table"):
        table_data = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            table_data.append(cells)
        tables.append(table_data)

    # Extract script sources (for reference, not execution)
    scripts = [script.get("src") for script in soup.find_all("script") if script.get("src")]

    return {
        "metadata": metadata,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "links": links,
        "images": images,
        "tables": tables,
        "scripts": scripts
    }

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    crawled_data = []  # List to store crawled content

    try:
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append((url, task))

            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            results = await asyncio.gather(*(task[1] for task in tasks), return_exceptions=True)

            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            for (url, task), result in zip(tasks, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    html_content = result.content if hasattr(result, "content") else ""
                    
                    structured_data = extract_html_elements(html_content)
                    
                    crawled_data.append({
                        "url": url,
                        "title": result.metadata.get("title", ""),  # Extract title if available
                        **structured_data,  # Include extracted elements
                    })
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

        # Save the crawled data to a JSON file
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(crawled_data, f, indent=4, ensure_ascii=False)

        print(f"Crawled data saved to {OUTPUT_JSON_FILE}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

async def main():
    urls = [
        'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5538',
        'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4013',
        # Add more URLs as needed
    ]
    
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())
