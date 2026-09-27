import pdfplumber
import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PDF_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "pdfs"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# EXPECTED COLUMNS
# ============================================================

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


# ============================================================
# CLEAN CELL
# ============================================================

def clean_cell(value):

    if value is None:
        return None

    return " ".join(
        str(value).split()
    )


# ============================================================
# EXTRACT BULLETIN DATE FROM FILENAME
# ============================================================

def extract_bulletin_date(pdf_path):

    filename = pdf_path.name

    # Example:
    # bulletin-24-09-2026-121.pdf

    parts = filename.split("-")

    if len(parts) < 4:
        return None

    date_string = "-".join(
        parts[1:4]
    )

    return pd.to_datetime(
        date_string,
        format="%d-%m-%Y",
        errors="coerce"
    )


# ============================================================
# FIND RESERVOIR REPORT PAGES
# ============================================================

def find_reservoir_pages(pdf):
    reservoir_pages = []

    search_text = "WEEKLY REPORT OF"

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""

        if search_text.lower() in text.lower():

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                # Actual reservoir-level table has 18 columns
                if len(table[0]) == 18:
                    reservoir_pages.append(page_number)
                    break

    return reservoir_pages

# ============================================================
# CHECK WHETHER ROW IS A VALID RESERVOIR ROW
# ============================================================

def is_valid_reservoir_row(row):

    if not row:
        return False

    if len(row) < 1:
        return False

    first_value = row[0]

    if first_value is None:
        return False

    first_value = clean_cell(
        first_value
    )

    if not first_value:
        return False

    # Reservoir rows start with S.No.
    # Examples: 1, 2, 19, 178
    return first_value.isdigit()


# ============================================================
# EXTRACT ONE PDF
# ============================================================

def extract_single_pdf(pdf_path):

    all_rows = []

    bulletin_date = extract_bulletin_date(
        pdf_path
    )

    print("\n" + "=" * 70)

    print(
        f"Processing: {pdf_path.name}"
    )

    print(
        f"Bulletin date: {bulletin_date}"
    )

    try:

        with pdfplumber.open(pdf_path) as pdf:

            # ------------------------------------------------
            # Find reservoir report pages dynamically
            # ------------------------------------------------

            reservoir_pages = find_reservoir_pages(
                pdf
            )

            print(
                "Reservoir report pages:",
                reservoir_pages
            )

            if not reservoir_pages:

                print(
                    "WARNING: Reservoir report not found."
                )

                return pd.DataFrame()

            # ------------------------------------------------
            # Process every reservoir report page
            # ------------------------------------------------

            for page_number in reservoir_pages:

                page = pdf.pages[
                    page_number - 1
                ]

                tables = page.extract_tables()

                if not tables:

                    print(
                        f"Page {page_number}: "
                        "No table found"
                    )

                    continue

                page_rows = 0

                # There should normally be one table,
                # but process all tables safely.

                for table in tables:

                    if not table:
                        continue

                    for row in table:

                        # Clean cells
                        row = [
                            clean_cell(cell)
                            for cell in row
                        ]

                        # Skip empty/header rows
                        if not is_valid_reservoir_row(
                            row
                        ):
                            continue

                        # We expect 18 columns
                        if len(row) != 18:

                            print(
                                f"Page {page_number}: "
                                f"Skipping row with "
                                f"{len(row)} columns"
                            )

                            continue

                        all_rows.append(row)

                        page_rows += 1

                print(
                    f"Page {page_number}: "
                    f"{page_rows} reservoir rows"
                )

    except Exception as e:

        print(
            f"ERROR processing "
            f"{pdf_path.name}: {e}"
        )

        return pd.DataFrame()

    # --------------------------------------------------------
    # No rows extracted
    # --------------------------------------------------------

    if not all_rows:

        print(
            "No reservoir rows extracted."
        )

        return pd.DataFrame()

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(
        all_rows,
        columns=COLUMNS
    )

    # Add bulletin date
    df["bulletin_date"] = bulletin_date

    return df


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

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

    # Convert dates

    df["latest_date"] = pd.to_datetime(
        df["latest_date"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    df["bulletin_date"] = pd.to_datetime(
        df["bulletin_date"],
        errors="coerce"
    )

    return df


# ============================================================
# REMOVE DUPLICATE ROWS
# ============================================================

def remove_duplicate_rows(df):

    before = len(df)

    df = df.drop_duplicates(
        subset=[
            "bulletin_date",
            "s_no"
        ]
    )

    after = len(df)

    print(
        f"\nDuplicate rows removed: "
        f"{before - after}"
    )

    return df


# ============================================================
# EXTRACT ALL BULLETINS
# ============================================================

def extract_all_bulletins():

    pdf_files = sorted(
        PDF_DIR.glob(
            "bulletin-*.pdf"
        )
    )

    print(
        f"Found {len(pdf_files)} PDFs."
    )

    all_data = []

    failed_files = []

    # --------------------------------------------------------
    # Process every PDF
    # --------------------------------------------------------

    for index, pdf_path in enumerate(
        pdf_files,
        start=1
    ):

        print(
            f"\n[{index}/{len(pdf_files)}]"
        )

        df = extract_single_pdf(
            pdf_path
        )

        if df.empty:

            failed_files.append(
                pdf_path.name
            )

            continue

        all_data.append(df)

    # --------------------------------------------------------
    # Check whether anything was extracted
    # --------------------------------------------------------

    if not all_data:

        raise RuntimeError(
            "No reservoir data was extracted."
        )

    # --------------------------------------------------------
    # Combine all PDFs
    # --------------------------------------------------------

    master_df = pd.concat(
        all_data,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Convert data types
    # --------------------------------------------------------

    master_df = convert_numeric_columns(
        master_df
    )

    # --------------------------------------------------------
    # Remove duplicate reservoir rows
    # --------------------------------------------------------

    master_df = remove_duplicate_rows(
        master_df
    )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    master_df = master_df.sort_values(
        [
            "bulletin_date",
            "s_no"
        ]
    ).reset_index(
        drop=True
    )

    return (
        master_df,
        failed_files
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "CWC HISTORICAL RESERVOIR EXTRACTION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    df, failed_files = (
        extract_all_bulletins()
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "EXTRACTION COMPLETE"
    )
    print("=" * 70)

    print(
        "\nTotal records:",
        len(df)
    )

    print(
        "Total columns:",
        len(df.columns)
    )

    print(
        "Unique bulletin dates:",
        df["bulletin_date"].nunique()
    )

    print(
        "Unique reservoirs:",
        df["reservoir"].nunique()
    )

    # --------------------------------------------------------
    # Date range
    # --------------------------------------------------------

    print("\nDate range:")

    print(
        df["bulletin_date"].min(),
        "→",
        df["bulletin_date"].max()
    )

    # --------------------------------------------------------
    # Records per bulletin
    # --------------------------------------------------------

    print(
        "\nRecords per bulletin:"
    )

    print(
        df.groupby(
            "bulletin_date"
        ).size().to_string()
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print(
        "\nMissing values:"
    )

    print(
        df.isnull().sum()
    )

    # --------------------------------------------------------
    # Failed PDFs
    # --------------------------------------------------------

    print(
        "\nFailed PDFs:"
    )

    if failed_files:

        for filename in failed_files:

            print(
                filename
            )

    else:

        print(
            "None"
        )

    # --------------------------------------------------------
    # Save master dataset
    # --------------------------------------------------------

    output_path = (
        OUTPUT_DIR /
        "reservoir_master.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nSaved to:"
    )

    print(
        output_path
    )

    # --------------------------------------------------------
    # Preview
    # --------------------------------------------------------

    print(
        "\nFirst 5 rows:"
    )

    print(
        df.head()
    )

    print(
        "\nLast 5 rows:"
    )

    print(
        df.tail()
    )