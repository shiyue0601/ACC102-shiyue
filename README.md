International Green Power Utilities Financial Analysis Tool

1. Problem & User
This project provides an interactive financial analysis tool for global green power utilities, enabling investors and researchers to efficiently explore, compare, and evaluate the profitability, stability, and growth of leading renewable energy companies.

2. Data
Source: WRDS Compustat Global Fundamentals Annual
Access Date: April 2026
Key Fields: Revenue, Net Income, Operating Income, Total Assets, Total Liabilities, Equity, ROE, Debt Ratio, Profit Margins, Growth Rates.

3. Methods
Data Ingestion: Load and clean CSV data using Pandas with automated column standardization.
Financial Engineering: Calculate key ratios (ROE, Net Margin, Debt Ratio) and compute growth metrics (YoY Revenue, Net Income, Assets).
Visualization: Build an interactive multi-tabbed dashboard using Streamlit and Plotly for dynamic trend analysis.
Interactivity: Implement company selection, year filtering, and data export functionalities for user-driven exploration.

4. Key Findings
The dashboard enables granular year-by-year trend analysis for revenue, profitability, and leverage.
Cross-company comparison features identify industry leaders in operational efficiency and financial stability.
Visualizations clearly highlight divergent growth patterns and varying risk levels across green power firms.
Calculated financial ratios support consistent evaluation of long-term solvency and asset turnover.

5. How to Run
Ensure dependencies are installed: pip install streamlit pandas plotly
Run the application: streamlit run app.py

6. Product link / Demo
Streamlit App: [Insert your Streamlit Cloud Link here]
Demo Video: [Insert your Loom or YouTube link here]

7. Limitations & next steps
Limitations: Relies on historical annual data (no real-time updates); analysis is limited to the selected companies in the dataset.
Next steps: Integrate quarterly data for higher granularity, add forecasting models (e.g., linear regression), incorporate ESG metrics, and implement automated peer benchmarking.
