import requests
from bs4 import BeautifulSoup
url = "https://rsms.cwc.gov.in/frameWork/web/bulletin-report-page"

response = requests.get(url, timeout=15)

print(response.status_code)
print("Content type:", response.headers.get("Content-Type"))
print("Page size", len(response.text))

print(response.text[:500])

soup = BeautifulSoup(response.text, "html.parser")

for link in soup.find_all("a", href=True):
    href = link["href"]

    if ".pdf" in href.lower() or "bulletin" in href.lower():
        print(href)

print("\n--- SCRIPT FILES ---")

for script in soup.find_all("script", src=True):
    print(script["src"])

print("\n--- API-RELATED TEXT ---")

text = response.text.lower()

for keyword in ["api", "bulletin", "download", "report"]:
    print(keyword, "->", keyword in text)