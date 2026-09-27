import requests
from pathlib import Path

from cwc_discovery import get_latest_pdf


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Where PDFs will be stored
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pdfs"


def download_pdf(pdf_url):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = pdf_url.split("/")[-1]

    output_path = OUTPUT_DIR / filename

    print("\nDownloading:")
    print(pdf_url)

    response = requests.get(
        pdf_url,
        timeout=60
    )

    response.raise_for_status()

    output_path.write_bytes(response.content)

    print("\nDownload successful!")
    print("Saved to:", output_path)
    print(
        "Size:",
        round(len(response.content) / 1024 / 1024, 2),
        "MB"
    )

    return output_path


if __name__ == "__main__":

    pdf_url = get_latest_pdf()

    download_pdf(pdf_url)