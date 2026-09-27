import pdfplumber
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PDF_DIR = (
    PROJECT_ROOT /
    "data" /
    "raw" /
    "pdfs"
)


FAILED_FILES = [
    "bulletin-02-10-2025-58.pdf",
    "bulletin-12-06-2025-23.pdf",
    "bulletin-16-10-2025-61.pdf",
    "bulletin-23-10-2025-62.pdf",
]


SEARCH_TERMS = [
    "WEEKLY REPORT OF 178 IMPORTANT RESERVOIRS",
    "WEEKLY REPORT",
    "IMPORTANT RESERVOIRS OF INDIA",
]


for filename in FAILED_FILES:

    pdf_path = PDF_DIR / filename

    print("\n" + "=" * 80)
    print(filename)
    print("=" * 80)

    with pdfplumber.open(pdf_path) as pdf:

        print("Total pages:", len(pdf.pages))

        for page_number, page in enumerate(
            pdf.pages,
            start=1
        ):

            text = page.extract_text() or ""

            for term in SEARCH_TERMS:

                if term.lower() in text.lower():

                    print(
                        f"FOUND '{term}' "
                        f"on page {page_number}"
                    )

                    print(
                        text[:500]
                    )

                    print("-" * 60)

                    break