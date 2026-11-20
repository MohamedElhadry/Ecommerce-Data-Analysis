
from pathlib import Path
import pandas as pd
import streamlit as st


# =====================================
# 1. Configuration
# =====================================

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
CHARTS = ROOT / "visualizations"

st.set_page_config(
    page_title="Brazilian E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)


# =====================================
# 2. Load Reports
# =====================================

@st.cache_data
def load_report(filename):

    path = REPORTS / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


# =====================================
# 3. Dashboard Header
# =====================================

st.title("🛒 Brazilian E-Commerce Analytics")
st.caption(
    "Business performance dashboard based on the Olist dataset"
)

st.divider()


# =====================================
# 4. Load KPI Data
# =====================================

kpis = load_report("sales_kpis.csv")
shipping = load_report("shipping_analysis.csv")
reviews = load_report("review_analysis.csv")
delivery = load_report("delivery_performance.csv")

if kpis.empty:
    st.error(
        "Reports not found. Run 'python main.py' first."
    )
    st.stop()


def get_kpi(metric_name):

    result = kpis.loc[
        kpis["Metric"] == metric_name,
        "Value"
    ]

    if result.empty:
        return 0

    return float(result.iloc[0])


revenue = get_kpi("Total Revenue")
orders = get_kpi("Total Orders")
customers = get_kpi("Total Customers")
aov = get_kpi("Average Order Value")


# =====================================
# 5. Main KPIs
# =====================================

st.subheader("Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Product Revenue",
    f"R$ {revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{orders:,.0f}"
)

col3.metric(
    "Total Customers",
    f"{customers:,.0f}"
)

col4.metric(
    "Average Order Value",
    f"R$ {aov:,.2f}"
)

st.divider()


# =====================================
# 6. Monthly Sales
# =====================================

st.subheader("Monthly Sales Performance")

monthly = load_report("monthly_sales.csv")

if not monthly.empty:

    monthly = monthly.sort_values("month")

    st.line_chart(
        monthly.set_index("month")[["revenue"]]
    )

    st.bar_chart(
        monthly.set_index("month")[["orders"]]
    )

else:
    st.warning("Monthly sales report is missing.")


# =====================================
# 7. Product Categories
# =====================================

st.divider()
st.subheader("Top Product Categories")

categories = load_report("top_categories.csv")

if not categories.empty:

    st.bar_chart(
        categories.set_index("category_name")[["revenue"]]
    )

    st.dataframe(
        categories,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 8. Customer Locations
# =====================================

st.divider()
st.subheader("Customer Locations")

states = load_report("top_customer_states.csv")

if not states.empty:

    st.bar_chart(
        states.set_index("customer_state")[["orders"]]
    )

    st.dataframe(
        states,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 9. Payment Analysis
# =====================================

st.divider()
st.subheader("Payment Methods")

payments = load_report("payment_analysis.csv")

if not payments.empty:

    st.bar_chart(
        payments.set_index("payment_type")[["total_value"]]
    )

    st.dataframe(
        payments,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 10. Customer Reviews
# =====================================

st.divider()
st.subheader("Customer Review Scores")

if not reviews.empty:

    st.bar_chart(
        reviews.set_index("review_score")[["number_of_reviews"]]
    )

    average_review = (
        (reviews["review_score"] * reviews["number_of_reviews"]).sum()
        / reviews["number_of_reviews"].sum()
    )

    st.metric(
        "Average Review Score",
        f"{average_review:.2f} / 5"
    )


# =====================================
# 11. Delivery Performance
# =====================================

st.divider()
st.subheader("Delivery Performance")

if not delivery.empty:

    st.dataframe(
        delivery,
        use_container_width=True,
        hide_index=True
    )

    if "average_review_score" in delivery.columns:

        chart_data = delivery.set_index("delivery_result")[
            ["average_review_score"]
        ]

        st.bar_chart(chart_data)


# =====================================
# 12. Shipping Analysis
# =====================================

st.divider()
st.subheader("Shipping Cost Analysis")

if not shipping.empty:

    st.dataframe(
        shipping,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 13. Seller Performance
# =====================================

st.divider()
st.subheader("Top 10 Sellers")

sellers = load_report("seller_performance.csv")

if not sellers.empty:

    top_sellers = sellers.head(10).copy()

    top_sellers["seller_id"] = (
        top_sellers["seller_id"].astype(str).str[:12]
    )

    st.bar_chart(
        top_sellers.set_index("seller_id")[["revenue"]]
    )

    st.dataframe(
        top_sellers,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 14. Business Insights
# =====================================

st.divider()
st.subheader("Business Insights")

insights_file = REPORTS / "business_insights.txt"

if insights_file.exists():

    insights_text = insights_file.read_text(
        encoding="utf-8"
    )

    st.text(insights_text)

else:
    st.info("Business insights report is not available.")


# =====================================
# 15. Footer
# =====================================

st.divider()

st.caption(
    "Brazilian E-Commerce Data Analysis | "
    "Data source: Olist Brazilian E-Commerce Dataset"
)
