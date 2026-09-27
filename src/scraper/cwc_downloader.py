import requests
from pathlib import Path

from cwc_discovery import get_all_pdf_urls


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT /
    "data" /
    "raw" /
    "pdfs"
)


def download_pdf(pdf_url):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = pdf_url.split("/")[-1]

    output_path = OUTPUT_DIR / filename

    # Don't download files we already have
    if output_path.exists():

        print(
            f"Already exists: {filename}"
        )

        return output_path

    print(
        f"Downloading: {filename}"
    )

    response = requests.get(
        pdf_url,
        timeout=60
    )

    response.raise_for_status()

    output_path.write_bytes(
        response.content
    )

    size_mb = len(response.content) / (
        1024 * 1024
    )

    print(
        f"Downloaded: {size_mb:.2f} MB"
    )

    return output_path


def download_all_pdfs():

    pdf_urls = get_all_pdf_urls()

    print("\n" + "=" * 60)
    print("STARTING BULK DOWNLOAD")
    print("=" * 60)

    print(
        f"Total PDFs to download: {len(pdf_urls)}"
    )

    successful = 0
    failed = []

    for index, pdf_url in enumerate(
        pdf_urls,
        start=1
    ):

        print(
            f"\n[{index}/{len(pdf_urls)}]"
        )

        try:

            download_pdf(pdf_url)

            successful += 1

        except Exception as e:

            print(
                f"FAILED: {pdf_url}"
            )

            print(
                f"Error: {e}"
            )

            failed.append(
                pdf_url
            )

    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)

    print(
        "Successful:",
        successful
    )

    print(
        "Failed:",
        len(failed)
    )

    if failed:

        print("\nFailed URLs:")

        for url in failed:
            print(url)


if __name__ == "__main__":

    download_all_pdfs()