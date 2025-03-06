import os
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Directory for storing output JSON files
OUTPUT_DIR = "scraped_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

async def fetch_html(session, url):
    """Fetch HTML content of a webpage asynchronously."""
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url} (Status: {response.status})")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_data(url, html_content):
    """Extract structured data from the HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract metadata
    page_title = soup.title.string.strip() if soup.title else "No Title"
    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})

    metadata = {
        "title": page_title,
        "description": meta_description["content"].strip() if meta_description else "No description",
        "keywords": meta_keywords["content"].strip() if meta_keywords else "No keywords",
        "url": url
    }

    # Extract headings
    headings = {tag.name: tag.text.strip() for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])}

    # Extract paragraphs
    paragraphs = [p.text.strip() for p in soup.find_all("p") if p.text.strip()]

    # Extract lists
    lists = []
    for ul in soup.find_all("ul"):
        lists.append([li.text.strip() for li in ul.find_all("li") if li.text.strip()])

    # Extract links
    links = [{"text": a.text.strip(), "url": a["href"]} for a in soup.find_all("a", href=True)]

    # Extract images
    images = [{"alt": img.get("alt", "").strip(), "src": img["src"]} for img in soup.find_all("img", src=True)]

    # Extract tables
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.text.strip() for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)

    # Extract JavaScript content
    scripts = [script.text.strip() for script in soup.find_all("script") if script.text.strip()]

    # Structure scraped data
    scraped_data = {
        "metadata": metadata,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "links": links,
        "images": images,
        "tables": tables,
        "scripts": scripts
    }

    return page_title, scraped_data

async def process_url(session, url):
    """Fetch, extract, and save data from a URL asynchronously."""
    html_content = await fetch_html(session, url)
    if html_content:
        course_name, scraped_data = extract_data(url, html_content)

        # Generate a valid filename from the course title
        safe_filename = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in course_name)[:50]
        output_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.json")

        # Save JSON file
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)

        print(f"✅ Scraped data saved: {output_path}")
    else:
        print(f"❌ Failed to process: {url}")

async def main():
    """Main function to handle multiple URLs asynchronously."""
    urls = ['https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5538', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4013', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6386', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6314', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6377', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4548', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6409', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4698', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7227', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6242', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5697', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6596', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4352', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5961', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6494', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2652', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2635', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6778', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4993', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3547', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1926', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5164', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2041', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5680', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1361', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2626', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6774', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7229', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1369', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=57', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5098', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5534', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5455', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6460', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2663', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5968', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5037', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5602', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6104', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3959', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1984', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1616', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1536', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4588', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2977', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4241', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5459', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4182', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6840', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4292', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3303', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3537', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6340', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6766', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6711', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6785', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2298', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1985', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3081', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3905', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6413', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6265', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6876', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1675', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3716', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4896', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6012', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6637', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2615', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2893', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4692', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=58', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4084', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2431', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5259', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6608', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3542', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3015', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6822', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5832', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5381', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6157', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2315', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5312', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6513', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2737', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3287', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6707', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7223', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=7231', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5504', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6446', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3667', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1433', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3875', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6770', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4379', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6723', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3248', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4214', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3631', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3691', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6622', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2011', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=60', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1794', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4788', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3535', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6455', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3804', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4193', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6790', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6628', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6049', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6801', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2013', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6226', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=451', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1748', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1761', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1890', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2890', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5647', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6394', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6521', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6529', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3836', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2219', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3877', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4427', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6600', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2397', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2348', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5222', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1439', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3279', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2327', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5196', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2232', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4395', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4816', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1445', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4472', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5387', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1431', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1688', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6519', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6253', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6172', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6442', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5265', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2622', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5821', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4969', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5690', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6714', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4939', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2143', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6192', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6759', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3072', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4814', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5785', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6627', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4823', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6639', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=4811', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6337', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2505', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5658', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6705', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=69', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6659', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6587', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6828', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6614', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5877', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6797', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2912', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=5996', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=6728', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=1448', 'https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=2557']

    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
