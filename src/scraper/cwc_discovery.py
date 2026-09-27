from playwright.sync_api import sync_playwright

CWC_URL = "https://rsms.cwc.gov.in/frameWork/web/bulletin-report-page"


def get_latest_pdf():

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

        # Find all download links
        download_links = page.locator(
            'a[title="download"]'
        )

        count = download_links.count()

        print(f"Found {count} bulletin PDFs on this page.")

        if count == 0:
            browser.close()
            raise Exception("No bulletin PDF links found.")

        # First link = latest bulletin
        latest_link = download_links.nth(0)

        pdf_url = latest_link.get_attribute("href")

        print("Latest PDF:")
        print(pdf_url)

        browser.close()

        return pdf_url


if __name__ == "__main__":

    latest_pdf = get_latest_pdf()

    print("\nLatest bulletin URL:")
    print(latest_pdf)
    