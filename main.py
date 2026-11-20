
from src.data_cleaning import run_cleaning
from src.eda_analysis import run_eda
from src.business_insights import run_business_insights


def main():

    print("=" * 60)
    print("BRAZILIAN E-COMMERCE DATA ANALYSIS")
    print("=" * 60)

    print("\nSTEP 1: DATA CLEANING")
    run_cleaning()

    print("\nSTEP 2: EXPLORATORY DATA ANALYSIS")
    run_eda()

    print("\nSTEP 3: BUSINESS INSIGHTS")
    run_business_insights()

    print("\nALL PROJECT STEPS COMPLETED!")


if __name__ == "__main__":
    main()
