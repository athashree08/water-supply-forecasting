from playwright.sync_api import sync_playwright
from datetime import datetime
import re
CWC_URL = "https://rsms.cwc.gov.in/frameWork/web/bulletin-report-page"

def extract_bulletin_date(url):

    filename = url.split("/")[-1]

    # Matches dates like:
    # bulletin-24-09-2026-121.pdf
    # bulletin-08-05-2025-10.pdf

    match = re.search(
        r"bulletin-(\d{2}-\d{2}-\d{4})",
        filename
    )

    if not match:
        return None

    return datetime.strptime(
        match.group(1),
        "%d-%m-%Y"
    )
def get_all_pdf_urls():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Opening CWC bulletin page...")

        page.goto(
            CWC_URL,
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_timeout(2000)

        all_urls = []
        page_number = 1

        while True:

            print(f"\nChecking page {page_number}...")

            # Find PDF download links
            download_links = page.locator(
                'a[title="download"]'
            )

            count = download_links.count()

            print(f"Found {count} PDFs")

            # Collect URLs
            for i in range(count):

                href = download_links.nth(i).get_attribute("href")

                if href:
                    all_urls.append(href)

            # Current first PDF
            old_first_url = (
                download_links.nth(0).get_attribute("href")
                if count > 0
                else None
            )

            # Find Next link
            next_link = page.locator(
                "a"
            ).filter(
                has_text="Next"
            ).first

            if next_link.count() == 0:

                print("No Next link found.")
                break

            print("Clicking Next...")

            next_link.click()

            # Wait for dynamically loaded table
            new_first_url = None

            for _ in range(20):

                page.wait_for_timeout(500)

                new_download_links = page.locator(
                    'a[title="download"]'
                )

                if new_download_links.count() == 0:
                    continue

                new_first_url = (
                    new_download_links
                    .nth(0)
                    .get_attribute("href")
                )

                if new_first_url != old_first_url:
                    break

            # Check whether page actually changed
            if new_first_url == old_first_url:

                print("Page did not change.")
                break

            print(
                "New first PDF:",
                new_first_url
            )

            page_number += 1

        browser.close()

    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(all_urls))

    print("\nTotal links collected:", len(all_urls))
    print("Unique URLs:", len(unique_urls))

    # Find duplicates
    duplicates = [
        url
        for url in set(all_urls)
        if all_urls.count(url) > 1
    ]

    if duplicates:

        print("\nDuplicate URLs found:")

        for url in duplicates:
            print(url)

    pdf_urls = unique_urls

        # Project start date
    start_date = datetime.strptime(
        "08-05-2025",
        "%d-%m-%Y"
    )

    # Keep only bulletins from project start onward
    filtered_urls = [
        url
        for url in pdf_urls
        if extract_bulletin_date(url)
        and extract_bulletin_date(url) >= start_date
    ]

    # Sort chronologically: oldest → newest
    filtered_urls.sort(
        key=extract_bulletin_date
    )

    print("\n" + "=" * 60)
    print("PROJECT DATE FILTER")
    print("=" * 60)

    print(
        "Project start:",
        start_date.strftime("%d-%m-%Y")
    )

    print(
        "Bulletins in project period:",
        len(filtered_urls)
    )

    print("\nOldest bulletin:")
    print(filtered_urls[0] if filtered_urls else "None")

    print("\nNewest bulletin:")
    print(filtered_urls[-1] if filtered_urls else "None")

    return filtered_urls

    print("\n" + "=" * 60)
    print("DISCOVERY COMPLETE")
    print("=" * 60)

    print(
        "Total PDF URLs found:",
        len(pdf_urls)
    )

    print("\nFirst 10 PDFs:")

    for url in pdf_urls[:10]:
        print(url)

    print("\nLast 10 PDFs:")

    for url in pdf_urls[-10:]:
        print(url)

    return pdf_urls


if __name__ == "__main__":

    urls = get_all_pdf_urls()

    print("\nFirst PDF:")
    print(urls[0] if urls else "None")

    print("\nLast PDF:")
    print(urls[-1] if urls else "None")