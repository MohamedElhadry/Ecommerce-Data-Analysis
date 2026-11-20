
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# =====================================
# 1. Paths
# =====================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "processed"
REPORT_PATH = ROOT / "reports"
CHART_PATH = ROOT / "visualizations"


# =====================================
# 2. Load Required Data
# =====================================

def load_data():

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

    products = pd.read_csv(
        DATA_PATH / "olist_products_dataset.csv"
    )

    sellers = pd.read_csv(
        DATA_PATH / "olist_sellers_dataset.csv"
    )

    reviews = pd.read_csv(
        DATA_PATH / "olist_order_reviews_dataset.csv"
    )

    return orders, items, products, sellers, reviews


# =====================================
# 3. Monthly Average Order Value
# =====================================

def analyze_monthly_aov(orders, items):

    print("\nAnalyzing monthly Average Order Value...")

    valid_orders = orders[
        orders["order_status"].isin(
            ["delivered", "shipped", "invoiced", "processing"]
        )
    ].copy()

    valid_items = items[
        items["order_id"].isin(valid_orders["order_id"])
    ].copy()

    order_revenue = (
        valid_items.groupby("order_id")["price"]
        .sum()
        .reset_index(name="order_revenue")
    )

    order_data = valid_orders.merge(
        order_revenue,
        on="order_id",
        how="left"
    )

    order_data["month"] = (
        order_data["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        order_data.groupby("month")
        .agg(
            revenue=("order_revenue", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    monthly["average_order_value"] = (
        monthly["revenue"] / monthly["orders"]
    )

    monthly.to_csv(
        REPORT_PATH / "monthly_aov.csv",
        index=False
    )

    plt.figure(figsize=(12, 6))
    plt.plot(
        monthly["month"],
        monthly["average_order_value"],
        marker="o"
    )
    plt.title("Monthly Average Order Value")
    plt.xlabel("Month")
    plt.ylabel("Average Order Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_PATH / "monthly_aov.png")
    plt.close()

    print(monthly.tail(10).to_string(index=False))


# =====================================
# 4. Shipping Cost Analysis
# =====================================

def analyze_shipping(items):

    print("\nAnalyzing shipping costs...")

    shipping = pd.DataFrame({
        "Metric": [
            "Total Product Revenue",
            "Total Shipping Cost",
            "Average Shipping Cost",
            "Average Product Price"
        ],
        "Value": [
            items["price"].sum(),
            items["freight_value"].sum(),
            items["freight_value"].mean(),
            items["price"].mean()
        ]
    })

    shipping.to_csv(
        REPORT_PATH / "shipping_analysis.csv",
        index=False
    )

    print(shipping.to_string(index=False))


# =====================================
# 5. Delivery Performance
# =====================================

def analyze_delivery(orders, reviews):

    print("\nAnalyzing delivery performance...")

    delivered = orders[
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].notna()
        & orders["order_estimated_delivery_date"].notna()
    ].copy()

    delivered["delivery_delay_days"] = (
        delivered["order_delivered_customer_date"]
        - delivered["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    delivered["delivery_result"] = (
        delivered["delivery_delay_days"]
        .apply(
            lambda days: "Late" if days > 0 else "On Time or Early"
        )
    )

    # One average review score per order avoids duplicate multiplication
    order_reviews = (
        reviews.groupby("order_id")["review_score"]
        .mean()
        .reset_index()
    )

    delivery_reviews = delivered.merge(
        order_reviews,
        on="order_id",
        how="left"
    )

    delivery_summary = (
        delivery_reviews.groupby("delivery_result")
        .agg(
            orders=("order_id", "nunique"),
            average_delay_days=("delivery_delay_days", "mean"),
            average_review_score=("review_score", "mean")
        )
        .reset_index()
    )

    delivery_summary.to_csv(
        REPORT_PATH / "delivery_performance.csv",
        index=False
    )

    print(delivery_summary.to_string(index=False))

    plt.figure(figsize=(8, 5))
    plt.bar(
        delivery_summary["delivery_result"],
        delivery_summary["average_review_score"]
    )
    plt.title("Average Review Score by Delivery Performance")
    plt.xlabel("Delivery Result")
    plt.ylabel("Average Review Score")
    plt.tight_layout()
    plt.savefig(CHART_PATH / "delivery_reviews.png")
    plt.close()


# =====================================
# 6. Seller Performance
# =====================================

def analyze_sellers(orders, items, sellers):

    print("\nAnalyzing seller performance...")

    valid_orders = orders[
        orders["order_status"].isin(
            ["delivered", "shipped", "invoiced", "processing"]
        )
    ][["order_id"]]

    valid_items = items[
        items["order_id"].isin(valid_orders["order_id"])
    ]

    seller_data = valid_items.merge(
        sellers[["seller_id", "seller_city", "seller_state"]],
        on="seller_id",
        how="left"
    )

    seller_performance = (
        seller_data.groupby("seller_id")
        .agg(
            revenue=("price", "sum"),
            items_sold=("order_item_id", "count"),
            orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    seller_performance.to_csv(
        REPORT_PATH / "seller_performance.csv",
        index=False
    )

    top_sellers = seller_performance.head(10)

    plt.figure(figsize=(12, 6))
    plt.bar(
        top_sellers["seller_id"].astype(str),
        top_sellers["revenue"]
    )
    plt.title("Top 10 Sellers by Revenue")
    plt.xlabel("Seller ID")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_PATH / "top_sellers.png")
    plt.close()

    print(top_sellers.to_string(index=False))


# =====================================
# 7. Generate Business Insights
# =====================================

def generate_insights(orders, items, reviews):

    print("\nGenerating business insights...")

    total_revenue = items["price"].sum()
    total_items = len(items)
    average_item_price = items["price"].mean()

    average_review = reviews["review_score"].mean()

    delivered_orders = orders[
        orders["order_status"] == "delivered"
    ]

    delivery_rate = (
        len(delivered_orders) / len(orders) * 100
        if len(orders) else 0
    )

    insights = [
        "BRAZILIAN E-COMMERCE BUSINESS INSIGHTS",
        "=" * 50,
        "",
        f"Total product revenue: {total_revenue:,.2f}",
        f"Total items sold: {total_items:,}",
        f"Average item price: {average_item_price:,.2f}",
        f"Average customer review score: {average_review:.2f} / 5",
        f"Delivered orders: {len(delivered_orders):,}",
        f"Delivered orders rate: {delivery_rate:.2f}%",
        "",
        "NOTES:",
        "- Revenue here is calculated from product item prices.",
        "- Shipping costs are analyzed separately.",
        "- Delivery analysis includes delivered orders with valid dates.",
        "- Review scores are averaged across available reviews."
    ]

    output_file = REPORT_PATH / "business_insights.txt"

    output_file.write_text(
        "\n".join(insights),
        encoding="utf-8"
    )

    print("\n".join(insights))


# =====================================
# 8. Run All Business Insights
# =====================================

def run_business_insights():

    REPORT_PATH.mkdir(parents=True, exist_ok=True)
    CHART_PATH.mkdir(parents=True, exist_ok=True)

    orders, items, products, sellers, reviews = load_data()

    analyze_monthly_aov(orders, items)

    analyze_shipping(items)

    analyze_delivery(orders, reviews)

    analyze_sellers(orders, items, sellers)

    generate_insights(orders, items, reviews)

    print("\nBUSINESS INSIGHTS COMPLETED!")


if __name__ == "__main__":
    run_business_insights()
