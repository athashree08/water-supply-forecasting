import pdfplumber
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "raw" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


COLUMNS = [
    "s_no",
    "reservoir",
    "state",
    "irrigation_cca_th_ha",
    "hydel_mw",
    "frl_m",
    "live_capacity_bcm",
    "latest_date",
    "current_level_m",
    "current_storage_bcm",
    "current_storage_pct",
    "last_year_level_m",
    "last_year_storage_bcm",
    "last_year_storage_pct",
    "normal_storage_bcm",
    "normal_storage_pct",
    "current_vs_last_year_pct",
    "current_vs_normal_pct"
]


def clean_cell(value):
    """Clean text extracted from a PDF cell."""

    if value is None:
        return None

    return " ".join(str(value).split())


def extract_reservoir_data(pdf_path):

    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:

        # Reservoir data is on pages 22, 23 and 24
        for page_number in [22, 23, 24]:

            page = pdf.pages[page_number - 1]

            tables = page.extract_tables()

            if not tables:
                print(f"No table found on page {page_number}")
                continue

            table = tables[0]

            print(
                f"Page {page_number}: "
                f"{len(table)} rows found"
            )

            # Skip:
            # row 0 -> title
            # row 1 -> date
            # row 2 -> headers
            # row 3 -> subheaders
            data_rows = table[4:]

            for row in data_rows:

                # Clean every cell
                row = [clean_cell(cell) for cell in row]

                # Ignore empty rows
                if not row:
                    continue

                # We only want rows having a serial number
                if not row[0]:
                    continue

                # Safety check
                if not row[0].isdigit():
                    continue

                if len(row) != 18:
                    print(
                        f"Skipping unexpected row on page "
                        f"{page_number}:"
                    )
                    print(row)
                    continue

                all_rows.append(row)

    df = pd.DataFrame(
        all_rows,
        columns=COLUMNS
    )

    return df


def convert_numeric_columns(df):

    numeric_columns = [
        "s_no",
        "irrigation_cca_th_ha",
        "hydel_mw",
        "frl_m",
        "live_capacity_bcm",
        "current_level_m",
        "current_storage_bcm",
        "current_storage_pct",
        "last_year_level_m",
        "last_year_storage_bcm",
        "last_year_storage_pct",
        "normal_storage_bcm",
        "normal_storage_pct",
        "current_vs_last_year_pct",
        "current_vs_normal_pct"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["latest_date"] = pd.to_datetime(
        df["latest_date"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    return df


if __name__ == "__main__":

    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF found in data/raw/pdfs/"
        )

    latest_pdf = max(
        pdf_files,
        key=lambda file: file.stat().st_mtime
    )

    print("Processing:")
    print(latest_pdf)

    df = extract_reservoir_data(latest_pdf)

    df = convert_numeric_columns(df)

    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)

    print("Total reservoir rows:", len(df))
    print("Total columns:", len(df.columns))

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nLast 5 rows:")
    print(df.tail())

    print("\nMissing values:")
    print(df.isnull().sum())

    output_path = (
        OUTPUT_DIR /
        "reservoir_data_24_09_2026.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print("\nSaved to:")
    print(output_path)