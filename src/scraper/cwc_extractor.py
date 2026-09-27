import pdfplumber
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PDF_DIR = PROJECT_ROOT / "data" / "raw" / "pdfs"


def inspect_pdf(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:

        print("Number of pages:", len(pdf.pages))

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            print("\n" + "=" * 60)
            print(f"PAGE {page_number}")
            print("=" * 60)

            if text:
                print(text[:2000])


if __name__ == "__main__":

    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("No PDF found.")

    latest_pdf = max(
        pdf_files,
        key=lambda file: file.stat().st_mtime
    )

    print("Inspecting:")
    print(latest_pdf)

    inspect_pdf(latest_pdf)