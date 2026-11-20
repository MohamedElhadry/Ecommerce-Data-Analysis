
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# =====================================
# 1. Project Paths
# =====================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "processed"
REPORT_PATH = ROOT / "reports"
CHART_PATH = ROOT / "visualizations"


# =====================================
# 2. Load Datasets
# =====================================

def load_data():

    print("Loading datasets...")

    orders = pd.read_csv(
        DATA_PATH / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    )

    items = pd.read_csv(
        DATA_PATH / "olist_order_items_dataset.csv"
    )

    payments = pd.read_csv(
        DATA_PATH / "olist_order_payments_dataset.csv"
    )

    products = pd.read_csv(
        DATA_PATH / "olist_products_dataset.csv"
    )

    customers = pd.read_csv(
        DATA_PATH / "olist_customers_dataset.csv"
    )

    reviews = pd.read_csv(
        DATA_PATH / "olist_order_reviews_dataset.csv"
    )

    categories = pd.read_csv(
        DATA_PATH / "product_category_name_translation.csv"
    )

    print("All datasets loaded successfully.")

    return (
        orders,
        items,
        payments,
        products,
        customers,
        reviews,
        categories
    )


# =====================================
# 3. Sales KPIs
# =====================================

def analyze_sales(orders, items):

    print("\nAnalyzing sales...")

    # Only count orders that were not canceled or unavailable
    valid_orders = orders[
        orders["order_status"].isin(
            ["delivered", "shipped", "invoiced", "processing"]
        )
    ]

    valid_items = items[
        items["order_id"].isin(valid_orders["order_id"])
    ]

    revenue = valid_items["price"].sum()
    total_orders = valid_orders["order_id"].nunique()
    total_customers = valid_orders["customer_id"].nunique()

    average_order_value = (
        revenue / total_orders if total_orders else 0
    )

    kpis = pd.DataFrame({
        "Metric": [
            "Total Revenue",
            "Total Orders",
            "Total Customers",
            "Average Order Value"
        ],
        "Value": [
            revenue,
            total_orders,
            total_customers,
            average_order_value
        ]
    })

    kpis.to_csv(
        REPORT_PATH / "sales_kpis.csv",
        index=False
    )

    print(kpis.to_string(index=False))

    return valid_orders, valid_items, kpis


# =====================================
# 4. Monthly Sales Analysis
# =====================================

def analyze_monthly_sales(valid_orders, valid_items):

    print("\nAnalyzing monthly sales...")

    monthly_revenue = (
        valid_items
        .merge(
            valid_orders[["order_id", "order_purchase_timestamp"]],
            on="order_id",
            how="inner"
        )
        .assign(
            month=lambda df:
            df["order_purchase_timestamp"].dt.to_period("M").astype(str)
        )
        .groupby("month")["price"]
        .sum()
        .reset_index(name="revenue")
    )

    monthly_orders = (
        valid_orders
        .assign(
            month=lambda df:
            df["order_purchase_timestamp"].dt.to_period("M").astype(str)
        )
        .groupby("month")["order_id"]
        .nunique()
        .reset_index(name="orders")
    )

    monthly = monthly_revenue.merge(
        monthly_orders,
        on="month",
        how="outer"
    ).sort_values("month")

    monthly.to_csv(
        REPORT_PATH / "monthly_sales.csv",
        index=False
    )

    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly["month"],
        monthly["revenue"],
        marker="o"
    )
    plt.title("Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_PATH / "monthly_revenue.png")
    plt.close()

    print(monthly.tail(10).to_string(index=False))

    return monthly


# =====================================
# 5. Top Product Categories
# =====================================

def analyze_categories(valid_items, products, categories):

    print("\nAnalyzing product categories...")

    category_data = (
        valid_items
        .merge(
            products[["product_id", "product_category_name"]],
            on="product_id",
            how="left"
        )
        .merge(
            categories,
            on="product_category_name",
            how="left"
        )
    )

    category_data["category_name"] = (
        category_data["product_category_name_english"]
        .fillna(category_data["product_category_name"])
        .fillna("Unknown")
    )

    top_categories = (
        category_data
        .groupby("category_name")
        .agg(
            revenue=("price", "sum"),
            items_sold=("order_item_id", "count")
        )
        .sort_values("revenue", ascending=False)
        .head(10)
        .reset_index()
    )

    top_categories.to_csv(
        REPORT_PATH / "top_categories.csv",
        index=False
    )

    plt.figure(figsize=(12, 6))
    plt.barh(
        top_categories["category_name"],
        top_categories["revenue"]
    )
    plt.title("Top 10 Product Categories by Revenue")
    plt.xlabel("Revenue")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(CHART_PATH / "top_categories.png")
    plt.close()

    print(top_categories.to_string(index=False))

    return top_categories


# =====================================
# 6. Customer Location Analysis
# =====================================

def analyze_locations(valid_orders, customers):

    print("\nAnalyzing customer locations...")

    location_data = valid_orders.merge(
        customers[["customer_id", "customer_state", "customer_city"]],
        on="customer_id",
        how="left"
    )

    top_states = (
        location_data
        .groupby("customer_state")
        .agg(
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique")
        )
        .sort_values("orders", ascending=False)
        .head(10)
        .reset_index()
    )

    top_states.to_csv(
        REPORT_PATH / "top_customer_states.csv",
        index=False
    )

    plt.figure(figsize=(10, 6))
    plt.bar(
        top_states["customer_state"],
        top_states["orders"]
    )
    plt.title("Top 10 States by Number of Orders")
    plt.xlabel("State")
    plt.ylabel("Orders")
    plt.tight_layout()
    plt.savefig(CHART_PATH / "top_states.png")
    plt.close()

    print(top_states.to_string(index=False))

    return top_states


# =====================================
# 7. Payment Methods
# =====================================

def analyze_payments(payments):

    print("\nAnalyzing payment methods...")

    payment_analysis = (
        payments
        .groupby("payment_type")
        .agg(
            total_payments=("payment_value", "count"),
            total_value=("payment_value", "sum")
        )
        .sort_values("total_value", ascending=False)
        .reset_index()
    )

    payment_analysis.to_csv(
        REPORT_PATH / "payment_analysis.csv",
        index=False
    )

    plt.figure(figsize=(9, 6))
    plt.bar(
        payment_analysis["payment_type"],
        payment_analysis["total_value"]
    )
    plt.title("Payment Methods by Total Value")
    plt.xlabel("Payment Method")
    plt.ylabel("Payment Value")
    plt.tight_layout()
    plt.savefig(CHART_PATH / "payment_methods.png")
    plt.close()

    print(payment_analysis.to_string(index=False))

    return payment_analysis


# =====================================
# 8. Customer Reviews
# =====================================

def analyze_reviews(reviews):

    print("\nAnalyzing customer reviews...")

    review_analysis = (
        reviews
        .groupby("review_score")
        .size()
        .reset_index(name="number_of_reviews")
        .sort_values("review_score")
    )

    review_analysis.to_csv(
        REPORT_PATH / "review_analysis.csv",
        index=False
    )

    plt.figure(figsize=(8, 5))
    plt.bar(
        review_analysis["review_score"],
        review_analysis["number_of_reviews"]
    )
    plt.title("Customer Review Scores")
    plt.xlabel("Review Score")
    plt.ylabel("Number of Reviews")
    plt.xticks([1, 2, 3, 4, 5])
    plt.tight_layout()
    plt.savefig(CHART_PATH / "review_scores.png")
    plt.close()

    print(review_analysis.to_string(index=False))

    return review_analysis


# =====================================
# 9. Order Status Analysis
# =====================================

def analyze_order_status(orders):

    print("\nAnalyzing order statuses...")

    status_analysis = (
        orders
        .groupby("order_status")
        .size()
        .reset_index(name="number_of_orders")
        .sort_values("number_of_orders", ascending=False)
    )

    status_analysis.to_csv(
        REPORT_PATH / "order_status_analysis.csv",
        index=False
    )

    print(status_analysis.to_string(index=False))

    return status_analysis


# =====================================
# 10. Run Complete EDA
# =====================================

def run_eda():

    REPORT_PATH.mkdir(parents=True, exist_ok=True)
    CHART_PATH.mkdir(parents=True, exist_ok=True)

    (
        orders,
        items,
        payments,
        products,
        customers,
        reviews,
        categories
    ) = load_data()

    valid_orders, valid_items, kpis = analyze_sales(
        orders,
        items
    )

    analyze_monthly_sales(
        valid_orders,
        valid_items
    )

    analyze_categories(
        valid_items,
        products,
        categories
    )

    analyze_locations(
        valid_orders,
        customers
    )

    analyze_payments(payments)

    analyze_reviews(reviews)

    analyze_order_status(orders)

    print("\n" + "=" * 60)
    print("EDA ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_eda()
