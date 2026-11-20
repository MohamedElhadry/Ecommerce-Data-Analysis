
from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw"
REPORT_PATH = PROJECT_ROOT / "reports"


def explore_dataset(file_path):
    """Load and explore one CSV dataset."""

    print("\n" + "=" * 70)
    print(f"DATASET: {file_path.name}")
    print("=" * 70)

    try:
        df = pd.read_csv(file_path)

        print(f"\nNumber of rows: {df.shape[0]:,}")
        print(f"Number of columns: {df.shape[1]}")

        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nData types:")
        print(df.dtypes)

        print("\nMissing values:")
        missing = df.isnull().sum()
        missing = missing[missing > 0]

        if missing.empty:
            print("No missing values found.")
        else:
            print(missing.sort_values(ascending=False))

        print("\nDuplicate rows:")
        print(df.duplicated().sum())

        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))

        return {
            "file": file_path.name,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "duplicates": int(df.duplicated().sum()),
            "missing_values": int(df.isnull().sum().sum()),
            "status": "Success"
        }

    except Exception as error:
        print(f"ERROR: {error}")

        return {
            "file": file_path.name,
            "rows": 0,
            "columns": 0,
            "duplicates": 0,
            "missing_values": 0,
            "status": f"Failed: {error}"
        }


def run_exploration():
    """Explore all CSV files in the raw data folder."""

    REPORT_PATH.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(DATA_PATH.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw!")
        return

    print(f"Found {len(csv_files)} CSV files.")

    results = []

    for file_path in csv_files:
        result = explore_dataset(file_path)
        results.append(result)

    summary = pd.DataFrame(results)

    report_file = REPORT_PATH / "exploration_summary.csv"
    summary.to_csv(report_file, index=False)

    print("\n" + "=" * 70)
    print("EXPLORATION SUMMARY")
    print("=" * 70)

    print(summary.to_string(index=False))
    print(f"\nSummary saved to: {report_file}")


if __name__ == "__main__":
    run_exploration()
