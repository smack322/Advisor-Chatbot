import requests
from bs4 import BeautifulSoup

# URL of the page to scrape

url = "https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io/wp-admin/edit.php?post_status=publish&post_type=page"

# Start a session
session = requests.Session()


# Headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Make the request
response = requests.get(url, headers=headers, timeout=10)
print(response.text)

# Request the target page
response = session.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extracting links with the specific XPath-like structure
links = []
for link in soup.select("td.column-title strong a"):
    href = link.get("href")
    if href and "post.php?post=" in href:
        full_url = f"https://dev-great-valley-ai-taskforce-chatbot.pantheonsite.io{href}"
        links.append(full_url)

# Print the extracted links
for url in links:
    print(url)
