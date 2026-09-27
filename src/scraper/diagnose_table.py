import pdfplumber
from pathlib import Path

PDF_PATH = Path(
    r"C:\Projects\Water-Supply-Forecasting\data\raw\pdfs\bulletin-31-07-2025-46.pdf"
)

with pdfplumber.open(PDF_PATH) as pdf:

    for page_number in range(1, len(pdf.pages) + 1):

        page = pdf.pages[page_number - 1]

        tables = page.extract_tables()

        for table_index, table in enumerate(tables):

            if not table:
                continue

            # Check whether this table contains numbered rows
            numbered_rows = 0

            for row in table:
                if row and row[0]:
                    value = str(row[0]).strip()

                    if value.isdigit():
                        numbered_rows += 1

            if numbered_rows >= 5:

                print("\n" + "=" * 80)
                print(
                    f"PAGE: {page_number} | "
                    f"TABLE: {table_index} | "
                    f"COLUMNS: {len(table[0])}"
                )
                print("=" * 80)

                for row in table[:8]:
                    print(row)

                print(
                    "\nNumbered rows:",
                    numbered_rows
                )