
from pathlib import Path
import pandas as pd


# ==============================
# 1. Project Paths
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
REPORT_PATH = PROJECT_ROOT / "reports"


# ==============================
# 2. Date Columns
# ==============================

DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],

    "olist_order_items_dataset.csv": [
        "shipping_limit_date"
    ],

    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp"
    ]
}


# ==============================
# 3. Data Cleaning
# ==============================

def clean_dataset(file_path):

    print("\n" + "=" * 60)
    print(f"Cleaning: {file_path.name}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    original_rows = len(df)

    # Remove exact duplicate rows
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    removed_rows = original_rows - len(df)

    # Convert date columns
    date_errors = 0

    for column in DATE_COLUMNS.get(file_path.name, []):

        if column in df.columns:

            original_values = df[column].notna()

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            date_errors += int(
                (original_values & df[column].isna()).sum()
            )

    # Check suspicious values without deleting them
    negative_price = 0
    negative_freight = 0
    negative_payment = 0
    invalid_review_scores = 0

    if "price" in df.columns:
        negative_price = int((df["price"] < 0).sum())

    if "freight_value" in df.columns:
        negative_freight = int((df["freight_value"] < 0).sum())

    if "payment_value" in df.columns:
        negative_payment = int((df["payment_value"] < 0).sum())

    if "review_score" in df.columns:
        invalid_review_scores = int(
            (~df["review_score"].between(1, 5)).sum()
        )

    # Save cleaned dataset
    output_file = PROCESSED_PATH / file_path.name
    df.to_csv(output_file, index=False)

    print(f"Original rows: {original_rows:,}")
    print(f"Duplicates removed: {removed_rows:,}")
    print(f"Remaining rows: {len(df):,}")
    print(f"Missing values: {df.isnull().sum().sum():,}")
    print(f"Date conversion errors: {date_errors:,}")
    print(f"Saved to: {output_file}")

    return {
        "dataset": file_path.name,
        "original_rows": original_rows,
        "duplicates_removed": removed_rows,
        "cleaned_rows": len(df),
        "missing_values": int(df.isnull().sum().sum()),
        "date_conversion_errors": date_errors,
        "negative_prices": negative_price,
        "negative_freight_values": negative_freight,
        "negative_payment_values": negative_payment,
        "invalid_review_scores": invalid_review_scores
    }


# ==============================
# 4. Relationship Validation
# ==============================

def check_relationships():

    print("\nChecking relationships between datasets...")

    customers = pd.read_csv(
        PROCESSED_PATH / "olist_customers_dataset.csv",
        usecols=["customer_id"]
    )

    orders = pd.read_csv(
        PROCESSED_PATH / "olist_orders_dataset.csv",
        usecols=["order_id", "customer_id"]
    )

    products = pd.read_csv(
        PROCESSED_PATH / "olist_products_dataset.csv",
        usecols=["product_id"]
    )

    sellers = pd.read_csv(
        PROCESSED_PATH / "olist_sellers_dataset.csv",
        usecols=["seller_id"]
    )

    order_items = pd.read_csv(
        PROCESSED_PATH / "olist_order_items_dataset.csv",
        usecols=["order_id", "product_id", "seller_id"]
    )

    payments = pd.read_csv(
        PROCESSED_PATH / "olist_order_payments_dataset.csv",
        usecols=["order_id"]
    )

    reviews = pd.read_csv(
        PROCESSED_PATH / "olist_order_reviews_dataset.csv",
        usecols=["order_id"]
    )

    # Convert IDs into sets for fast lookup
    customer_ids = set(customers["customer_id"])
    order_ids = set(orders["order_id"])
    product_ids = set(products["product_id"])
    seller_ids = set(sellers["seller_id"])

    checks = [
        {
            "relationship": "Orders -> Customers",
            "unmatched_rows": int(
                (~orders["customer_id"].isin(customer_ids)).sum()
            )
        },
        {
            "relationship": "Order Items -> Orders",
            "unmatched_rows": int(
                (~order_items["order_id"].isin(order_ids)).sum()
            )
        },
        {
            "relationship": "Order Items -> Products",
            "unmatched_rows": int(
                (~order_items["product_id"].isin(product_ids)).sum()
            )
        },
        {
            "relationship": "Order Items -> Sellers",
            "unmatched_rows": int(
                (~order_items["seller_id"].isin(seller_ids)).sum()
            )
        },
        {
            "relationship": "Payments -> Orders",
            "unmatched_rows": int(
                (~payments["order_id"].isin(order_ids)).sum()
            )
        },
        {
            "relationship": "Reviews -> Orders",
            "unmatched_rows": int(
                (~reviews["order_id"].isin(order_ids)).sum()
            )
        }
    ]

    relationship_report = pd.DataFrame(checks)

    output_file = REPORT_PATH / "relationship_report.csv"
    relationship_report.to_csv(output_file, index=False)

    print(relationship_report.to_string(index=False))
    print(f"\nRelationship report saved to: {output_file}")


# ==============================
# 5. Run Full Cleaning Pipeline
# ==============================

def run_cleaning():

    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_PATH.glob("*.csv"))

    if not csv_files:
        print("ERROR: No CSV files found in data/raw!")
        return

    print(f"Found {len(csv_files)} datasets.")

    results = []

    for file_path in csv_files:

        result = clean_dataset(file_path)
        results.append(result)

    # Save data quality report
    quality_report = pd.DataFrame(results)

    report_file = REPORT_PATH / "data_quality_report.csv"

    quality_report.to_csv(report_file, index=False)

    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    print(quality_report.to_string(index=False))

    print(f"\nQuality report saved to: {report_file}")

    # Check relationships
    check_relationships()

    print("\n" + "=" * 60)
    print("DATA CLEANING COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    run_cleaning()
