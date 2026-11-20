
# Brazilian E-Commerce Data Analysis

## Project Overview

This project analyzes the Brazilian E-Commerce public dataset
provided by Olist.

The goal is to understand e-commerce business performance
through data cleaning, exploratory data analysis,
business insights, and interactive visualization.

## Dataset

The project uses the Olist Brazilian E-Commerce dataset,
which contains information about:

- Customers
- Orders
- Order Items
- Payments
- Reviews
- Products
- Sellers
- Geolocation
- Product Category Translation

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit

## Project Structure

```text
Ecommerce-Data-Analysis/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── data_cleaning.py
│   ├── data_exploration.py
│   ├── eda_analysis.py
│   └── business_insights.py
├── reports/
├── visualizations/
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## Project Workflow

### 1. Data Collection
Load the original CSV datasets.

### 2. Data Cleaning
- Remove exact duplicate rows.
- Convert date columns.
- Inspect missing values.
- Validate relationships between datasets.
- Preserve the original raw files.

### 3. Exploratory Data Analysis
- Sales analysis.
- Monthly revenue.
- Product category performance.
- Customer locations.
- Payment methods.
- Customer reviews.
- Order statuses.

### 4. Business Insights
- Average Order Value.
- Shipping cost analysis.
- Delivery performance.
- Seller performance.
- Business recommendations.

### 5. Interactive Dashboard
Visualize key performance indicators and
analysis results using Streamlit.

## How to Run

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the analysis pipeline:

```bash
python main.py
```

Launch the dashboard:

```bash
streamlit run app.py
```

## Main Outputs

- Data quality reports.
- Sales KPI reports.
- Monthly sales analysis.
- Product category analysis.
- Customer location analysis.
- Payment analysis.
- Delivery performance.
- Seller performance.
- Interactive dashboard.

## Data Source

Olist Brazilian E-Commerce Public Dataset.

Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
