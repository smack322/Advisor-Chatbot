import os
import sys
import psutil
import asyncio
import requests
from xml.etree import ElementTree

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,   # corrected from 'verbos=False'
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []        

async def main():
    urls = ['https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5538', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4013', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6386', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6314', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6377', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4548', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6409', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4698', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7227', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6242', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5697', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6596', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4352', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5961', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6494', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2652', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2635', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6778', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4993', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3547', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1926', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5164', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2041', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5680', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1361', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2626', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6774', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7229', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1369', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=57', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5098', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5534', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5455', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6460', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2663', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5968', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5037', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5602', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6104', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3959', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1984', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1616', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1536', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4588', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2977', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4241', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5459', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4182', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6840', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4292', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3303', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3537', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6340', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6766', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6711', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6785', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2298', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1985', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3081', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3905', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6413', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6265', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6876', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1675', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3716', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4896', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6012', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6637', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2615', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2893', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4692', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=58', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4084', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2431', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5259', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6608', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3542', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3015', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6822', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5832', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5381', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6157', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2315', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5312', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6513', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2737', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3287', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6707', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7223', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7231', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5504', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6446', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3667', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1433', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3875', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6770', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4379', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6723', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3248', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4214', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3631', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3691', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6622', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2011', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=60', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1794', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4788', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3535', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6455', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3804', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4193', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6790', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6628', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6049', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6801', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2013', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6226', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=451', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1748', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1761', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1890', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2890', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5647', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6394', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6521', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6529', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3836', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2219', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3877', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4427', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6600', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2397', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2348', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5222', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1439', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3279', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2327', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5196', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2232', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4395', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4816', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1445', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4472', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5387', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1431', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1688', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6519', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6253', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6172', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6442', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5265', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2622', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5821', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4969', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5690', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6714', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4939', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2143', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6192', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6759', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3072', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4814', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5785', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6627', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4823', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6639', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4811', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6337', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2505', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5658', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6705', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=69', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6659', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6587', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6828', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6614', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5877', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6797', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2912', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5996', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6728', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1448', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2557']
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())