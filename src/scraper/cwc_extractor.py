import pdfplumber
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "raw" / "pdfs"


def inspect_tables(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:

        for page_number in [22, 23, 24]:

            page = pdf.pages[page_number - 1]

            print("\n" + "=" * 80)
            print(f"PAGE {page_number}")
            print("=" * 80)

            tables = page.extract_tables()

            print(f"Number of tables found: {len(tables)}")

            for table_number, table in enumerate(tables, start=1):

                print(f"\n--- TABLE {table_number} ---")
                print(f"Rows: {len(table)}")

                for row in table[:8]:
                    print(row)


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

    inspect_tables(latest_pdf)