import requests
from bs4 import BeautifulSoup
import json

# Define the URL
url = "https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/?page_id=3535"

# Headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Make the request
response = requests.get(url, headers=headers, timeout=10)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Extract metadata (title, description, keywords)
page_title = soup.title.string.strip() if soup.title else "No Title"
meta_description = soup.find("meta", attrs={"name": "description"})
meta_keywords = soup.find("meta", attrs={"name": "keywords"})

metadata = {
    "title": page_title,
    "description": meta_description["content"].strip() if meta_description else "No description",
    "keywords": meta_keywords["content"].strip() if meta_keywords else "No keywords",
    "url": url
}

# Extract all headings (h1-h6)
headings = {tag.name: tag.text.strip() for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])}

# Extract all paragraphs
paragraphs = [p.text.strip() for p in soup.find_all("p") if p.text.strip()]

# Extract all lists
lists = []
for ul in soup.find_all("ul"):
    lists.append([li.text.strip() for li in ul.find_all("li") if li.text.strip()])

# Extract all links
links = []
for a in soup.find_all("a", href=True):
    links.append({"text": a.text.strip(), "url": a["href"]})

# Extract all images
images = []
for img in soup.find_all("img", src=True):
    images.append({"alt": img.get("alt", "").strip(), "src": img["src"]})

# Extract all tables
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

# Structure all scraped data into JSON format
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

# Save to JSON file
output_path = "scraped_full_data.json"
with open(output_path, "w", encoding="utf-8") as json_file:
    json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)

print(f"Scraping completed! Data saved in {output_path}")
