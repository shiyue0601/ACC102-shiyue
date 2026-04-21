"""
Enhanced International Green Power Utilities Financial Analysis Tool
Simplified version - removed unnecessary sections
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up the page
st.set_page_config(
    page_title="Green Power Financial Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #43A047;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1rem;
        padding: 10px 16px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header"> International Green Power Utilities Financial Analysis</h1>', unsafe_allow_html=True)
st.markdown("**Comprehensive analysis of leading green energy companies' financial performance**")

# Function to clean column names
def clean_column_name(col):
    if '(' in str(col) and ')' in str(col):
        start = str(col).find('(') + 1
        end = str(col).find(')')
        return str(col)[start:end].strip()
    return str(col).strip()

# Load data with caching
@st.cache_data
def load_data():
    url = "https://coze-user-file.tos-cn-beijing.volces.com/327014814850268/7618493623633821705/green_power_data.csv?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTNjU0ZGJiM2IyN2E1NGExZWFiMDdmMzQ1NTAzZjlhOGU%2F20260420%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20260420T164241Z&X-Tos-Expires=604800&X-Tos-Signature=59d0e54e569312606a2c61f03b7ed260312af3bd5ae78edb7a03876c3ab7d523&X-Tos-SignedHeaders=host"
    
    try:
        df = pd.read_csv(url)
        
        # Clean column names
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # Rename columns
        column_mapping = {
            'conm': 'Company',
            'fyear': 'Year',
            'at': 'Total_Assets',
            'lt': 'Total_Liabilities',
            'oiadp': 'Operating_Income',
            'seq': 'Equity',
            'nicon': 'Net_Income',
            'revt': 'Revenue',
            'cogs': 'Cost_of_Goods_Sold',
            'xint': 'Interest_Expense',
            'capx': 'Capital_Expenditure',
            'act': 'Current_Assets',
            'lct': 'Current_Liabilities'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert to numeric
        numeric_cols = ['Total_Assets', 'Total_Liabilities', 'Operating_Income', 
                       'Equity', 'Net_Income', 'Revenue', 'Cost_of_Goods_Sold',
                       'Interest_Expense', 'Capital_Expenditure', 'Current_Assets',
                       'Current_Liabilities']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate financial ratios
        # Profitability Ratios
        if 'Net_Income' in df.columns and 'Equity' in df.columns:
            df['ROE'] = df['Net_Income'] / df['Equity']
        
        if 'Net_Income' in df.columns and 'Operating_Income' in df.columns:
            df['Net_Margin'] = df['Net_Income'] / df['Operating_Income']
        
        if 'Revenue' in df.columns and 'Cost_of_Goods_Sold' in df.columns:
            df['Gross_Margin'] = (df['Revenue'] - df['Cost_of_Goods_Sold']) / df['Revenue']
        
        if 'Operating_Income' in df.columns and 'Revenue' in df.columns:
            df['Operating_Margin'] = df['Operating_Income'] / df['Revenue']
        
        # Liquidity Ratios
        if 'Current_Assets' in df.columns and 'Current_Liabilities' in df.columns:
            df['Current_Ratio'] = df['Current_Assets'] / df['Current_Liabilities']
        
        # Solvency Ratios
        if 'Total_Liabilities' in df.columns and 'Total_Assets' in df.columns:
            df['Debt_Ratio'] = df['Total_Liabilities'] / df['Total_Assets']
            df['Debt_to_Equity'] = df['Total_Liabilities'] / df['Equity']
        
        if 'Interest_Expense' in df.columns and 'Operating_Income' in df.columns:
            df['Interest_Coverage'] = df['Operating_Income'] / df['Interest_Expense']
        
        # Efficiency Ratios
        if 'Revenue' in df.columns and 'Total_Assets' in df.columns:
            df['Asset_Turnover'] = df['Revenue'] / df['Total_Assets']
        
        # Growth Metrics
        df = df.sort_values(['Company', 'Year'])
        for col in ['Revenue', 'Operating_Income', 'Net_Income', 'Total_Assets']:
            if col in df.columns:
                df[f'{col}_Growth'] = df.groupby('Company')[col].pct_change() * 100
        
        # Handle any errors in calculations
        df = df.replace([np.inf, -np.inf], np.nan)
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load the data
with st.spinner('Loading and processing financial data...'):
    data = load_data()

# Sidebar Configuration
st.sidebar.header("Analysis Configuration")

# Data Overview in Sidebar
st.sidebar.markdown("### Data Overview")
if not data.empty:
    st.sidebar.metric("Total Records", f"{len(data):,}")
    if 'Year' in data.columns:
        min_year = int(data['Year'].min())
        max_year = int(data['Year'].max())
        st.sidebar.metric("Year Range", f"{min_year} - {max_year}")
    
    if 'Company' in data.columns:
        companies = sorted(data['Company'].unique())
        st.sidebar.metric("Companies", len(companies))
        
        # Company selection with search
        st.sidebar.markdown("### Company Selection")
        selected_company = st.sidebar.selectbox(
            "Select Company",
            companies,
            index=0,
            help="Choose a company to analyze"
        )
        
        # Year range selection
        st.sidebar.markdown("### Year Range")
        years = sorted(data['Year'].unique())
        year_range = st.sidebar.slider(
            "Select Year Range",
            min_value=int(min(years)),
            max_value=int(max(years)),
            value=(int(min(years)), int(max(years))),
            step=1
        )

# Main Content Area
if not data.empty:
    # Filter data based on selections
    filtered_data = data[(data['Year'] >= year_range[0]) & (data['Year'] <= year_range[1])]
    company_data = filtered_data[filtered_data['Company'] == selected_company]
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", 
        "Financial Analysis", 
        "Ratios & Metrics", 
        "Industry Comparison",
        "Data Explorer"
    ])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Company Overview</h2>', unsafe_allow_html=True)
        
        # Key Metrics Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if not company_data.empty and 'Revenue' in company_data.columns:
                latest_rev = company_data.iloc[-1]['Revenue']
                rev_growth = company_data.iloc[-1]['Revenue_Growth'] if 'Revenue_Growth' in company_data.columns else 0
                st.metric(
                    "Revenue",
                    f"${latest_rev:,.0f}",
                    f"{rev_growth:.1f}%"
                )
        
        with col2:
            if not company_data.empty and 'Net_Income' in company_data.columns:
                latest_ni = company_data.iloc[-1]['Net_Income']
                ni_growth = company_data.iloc[-1]['Net_Income_Growth'] if 'Net_Income_Growth' in company_data.columns else 0
                st.metric(
                    "Net Income",
                    f"${latest_ni:,.0f}",
                    f"{ni_growth:.1f}%"
                )
        
        with col3:
            if not company_data.empty and 'ROE' in company_data.columns:
                latest_roe = company_data.iloc[-1]['ROE']
                st.metric("ROE", f"{latest_roe:.2%}")
        
        with col4:
            if not company_data.empty and 'Debt_Ratio' in company_data.columns:
                latest_debt = company_data.iloc[-1]['Debt_Ratio']
                st.metric("Debt Ratio", f"{latest_debt:.2%}")
        
        # Company Performance Dashboard
        st.markdown('<h3 class="sub-header">Performance Dashboard</h3>', unsafe_allow_html=True)
        
        # Create subplots for comprehensive view
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue & Net Income', 'Profitability Ratios', 
                          'Liquidity & Solvency', 'Growth Trends'),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Chart 1: Revenue and Net Income
        if 'Revenue' in company_data.columns and 'Net_Income' in company_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Revenue'],
                    name='Revenue',
                    mode='lines+markers',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Net_Income'],
                    name='Net Income',
                    mode='lines+markers',
                    line=dict(color='#2ca02c', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
        
        # Chart 2: Profitability Ratios
        if 'ROE' in company_data.columns and 'Net_Margin' in company_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['ROE'] * 100,
                    name='ROE',
                    mode='lines+markers',
                    line=dict(color='#d62728', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Net_Margin'] * 100,
                    name='Net Margin',
                    mode='lines+markers',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=2
            )
        
        # Chart 3: Liquidity and Solvency
        if 'Current_Ratio' in company_data.columns and 'Debt_Ratio' in company_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Current_Ratio'],
                    name='Current Ratio',
                    mode='lines+markers',
                    line=dict(color='#9467bd', width=3),
                    marker=dict(size=8)
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Debt_Ratio'] * 100,
                    name='Debt Ratio',
                    mode='lines+markers',
                    line=dict(color='#8c564b', width=3),
                    marker=dict(size=8)
                ),
                row=2, col=1
            )
        
        # Chart 4: Growth Trends
        if 'Revenue_Growth' in company_data.columns and 'Net_Income_Growth' in company_data.columns:
            fig.add_trace(
                go.Bar(
                    x=company_data['Year'],
                    y=company_data['Revenue_Growth'],
                    name='Revenue Growth',
                    marker_color='#17becf'
                ),
                row=2, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    x=company_data['Year'],
                    y=company_data['Net_Income_Growth'],
                    name='Net Income Growth',
                    marker_color='#bcbd22'
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Financial Summary
        st.markdown('<h3 class="sub-header">Financial Summary</h3>', unsafe_allow_html=True)
        
        if not company_data.empty:
            summary_cols = st.columns(3)
            
            with summary_cols[0]:
                st.markdown("**Profitability**")
                if 'ROE' in company_data.columns:
                    avg_roe = company_data['ROE'].mean()
                    st.write(f"Average ROE: {avg_roe:.2%}")
                
                if 'Net_Margin' in company_data.columns:
                    avg_margin = company_data['Net_Margin'].mean()
                    st.write(f"Average Net Margin: {avg_margin:.2%}")
            
            with summary_cols[1]:
                st.markdown("**Liquidity**")
                if 'Current_Ratio' in company_data.columns:
                    avg_current = company_data['Current_Ratio'].mean()
                    st.write(f"Average Current Ratio: {avg_current:.2f}")
                
                if 'Debt_Ratio' in company_data.columns:
                    avg_debt = company_data['Debt_Ratio'].mean()
                    st.write(f"Average Debt Ratio: {avg_debt:.2%}")
            
            with summary_cols[2]:
                st.markdown("**Growth**")
                if 'Revenue_Growth' in company_data.columns:
                    avg_rev_growth = company_data['Revenue_Growth'].mean()
                    st.write(f"Average Revenue Growth: {avg_rev_growth:.1f}%")
                
                if 'Net_Income_Growth' in company_data.columns:
                    avg_ni_growth = company_data['Net_Income_Growth'].mean()
                    st.write(f"Average Net Income Growth: {avg_ni_growth:.1f}%")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Detailed Financial Analysis</h2>', unsafe_allow_html=True)
        
        # Income Statement Analysis
        st.markdown("### Income Statement Analysis")
        income_cols = ['Year', 'Revenue', 'Operating_Income', 'Net_Income']
        income_cols = [col for col in income_cols if col in company_data.columns]
        
        if income_cols:
            income_data = company_data[income_cols].copy()
            
            # Format for display
            for col in ['Revenue', 'Operating_Income', 'Net_Income']:
                if col in income_data.columns:
                    income_data[col] = income_data[col].apply(
                        lambda x: f"${x:,.0f}" if pd.notnull(x) and x != 0 else "-"
                    )
            
            st.dataframe(income_data, use_container_width=True)
            
            # Income composition chart
            if 'Revenue' in company_data.columns and 'Operating_Income' in company_data.columns and 'Net_Income' in company_data.columns:
                fig_income = go.Figure()
                
                fig_income.add_trace(go.Bar(
                    x=company_data['Year'],
                    y=company_data['Revenue'],
                    name='Revenue',
                    marker_color='#1f77b4'
                ))
                
                fig_income.add_trace(go.Bar(
                    x=company_data['Year'],
                    y=company_data['Operating_Income'],
                    name='Operating Income',
                    marker_color='#2ca02c'
                ))
                
                fig_income.add_trace(go.Bar(
                    x=company_data['Year'],
                    y=company_data['Net_Income'],
                    name='Net Income',
                    marker_color='#d62728'
                ))
                
                fig_income.update_layout(
                    title='Income Statement Components',
                    barmode='group',
                    height=400
                )
                
                st.plotly_chart(fig_income, use_container_width=True)
        
        # Balance Sheet Analysis
        st.markdown("### Balance Sheet Analysis")
        balance_cols = ['Year', 'Total_Assets', 'Total_Liabilities', 'Equity', 'Current_Assets', 'Current_Liabilities']
        balance_cols = [col for col in balance_cols if col in company_data.columns]
        
        if balance_cols:
            balance_data = company_data[balance_cols].copy()
            
            # Format for display
            for col in ['Total_Assets', 'Total_Liabilities', 'Equity', 'Current_Assets', 'Current_Liabilities']:
                if col in balance_data.columns:
                    balance_data[col] = balance_data[col].apply(
                        lambda x: f"${x:,.0f}" if pd.notnull(x) and x != 0 else "-"
                    )
            
            st.dataframe(balance_data, use_container_width=True)
            
            # Asset composition chart
            if 'Total_Assets' in company_data.columns and 'Total_Liabilities' in company_data.columns and 'Equity' in company_data.columns:
                fig_balance = go.Figure()
                
                # Calculate percentages
                company_data['Assets_Pct'] = 100
                company_data['Liabilities_Pct'] = (company_data['Total_Liabilities'] / company_data['Total_Assets']) * 100
                company_data['Equity_Pct'] = (company_data['Equity'] / company_data['Total_Assets']) * 100
                
                fig_balance.add_trace(go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Liabilities_Pct'],
                    name='Liabilities %',
                    mode='lines+markers',
                    line=dict(color='#ff7f0e', width=3)
                ))
                
                fig_balance.add_trace(go.Scatter(
                    x=company_data['Year'],
                    y=company_data['Equity_Pct'],
                    name='Equity %',
                    mode='lines+markers',
                    line=dict(color='#9467bd', width=3)
                ))
                
                fig_balance.update_layout(
                    title='Capital Structure (% of Total Assets)',
                    yaxis_title='Percentage (%)',
                    height=400
                )
                
                st.plotly_chart(fig_balance, use_container_width=True)
    
    with tab3:
        st.markdown('<h2 class="sub-header">Financial Ratios & Metrics</h2>', unsafe_allow_html=True)
        
        # All financial ratios table
        ratio_cols = ['Year', 'ROE', 'Net_Margin', 'Gross_Margin', 'Operating_Margin', 
                     'Current_Ratio', 'Debt_Ratio', 'Debt_to_Equity', 'Interest_Coverage',
                     'Asset_Turnover']
        
        ratio_cols = [col for col in ratio_cols if col in company_data.columns]
        
        if ratio_cols:
            ratio_data = company_data[ratio_cols].copy()
            
            # Format percentages
            for col in ['ROE', 'Net_Margin', 'Gross_Margin', 'Operating_Margin', 'Debt_Ratio', 'Debt_to_Equity']:
                if col in ratio_data.columns:
                    ratio_data[col] = ratio_data[col].apply(
                        lambda x: f"{x:.2%}" if pd.notnull(x) and x != 0 else "-"
                    )
            
            # Format other ratios
            for col in ['Current_Ratio', 'Interest_Coverage', 'Asset_Turnover']:
                if col in ratio_data.columns:
                    ratio_data[col] = ratio_data[col].apply(
                        lambda x: f"{x:.2f}" if pd.notnull(x) and x != 0 else "-"
                    )
            
            st.dataframe(ratio_data, use_container_width=True)
            
            # Ratio trend analysis
            st.markdown("### Ratio Trend Analysis")
            
            # Select ratios to plot
            available_ratios = [col for col in ['ROE', 'Net_Margin', 'Current_Ratio', 'Debt_Ratio'] 
                              if col in company_data.columns]
            
            if available_ratios:
                selected_ratios = st.multiselect(
                    "Select ratios to compare:",
                    available_ratios,
                    default=available_ratios[:2] if len(available_ratios) >= 2 else available_ratios
                )
                
                if selected_ratios:
                    fig_ratios = go.Figure()
                    
                    for ratio in selected_ratios:
                        if ratio in ['ROE', 'Net_Margin', 'Debt_Ratio']:
                            # Convert to percentage
                            y_values = company_data[ratio] * 100
                            y_label = 'Percentage (%)'
                        else:
                            y_values = company_data[ratio]
                            y_label = 'Ratio Value'
                        
                        fig_ratios.add_trace(go.Scatter(
                            x=company_data['Year'],
                            y=y_values,
                            name=ratio.replace('_', ' '),
                            mode='lines+markers',
                            line=dict(width=3)
                        ))
                    
                    fig_ratios.update_layout(
                        title='Financial Ratio Trends',
                        xaxis_title='Year',
                        yaxis_title=y_label,
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_ratios, use_container_width=True)
    
    with tab4:
        st.markdown('<h2 class="sub-header">Industry Comparison</h2>', unsafe_allow_html=True)
        
        # Select companies to compare
        st.markdown("### Select Companies for Comparison")
        compare_companies = st.multiselect(
            "Choose companies:",
            companies,
            default=[selected_company],
            max_selections=5
        )
        
        if len(compare_companies) > 0:
            compare_data = filtered_data[filtered_data['Company'].isin(compare_companies)]
            
            # Comparison metrics
            st.markdown("### Key Metrics Comparison")
            
            # Get latest year data for each company
            latest_comparison = []
            for company in compare_companies:
                company_latest = compare_data[compare_data['Company'] == company].iloc[-1]
                metrics = {'Company': company}
                
                # Add available metrics
                for metric in ['Revenue', 'Net_Income', 'ROE', 'Net_Margin', 'Current_Ratio', 'Debt_Ratio']:
                    if metric in company_latest:
                        metrics[metric] = company_latest[metric]
                
                latest_comparison.append(metrics)
            
            if latest_comparison:
                comparison_df = pd.DataFrame(latest_comparison)
                
                # Format for display
                display_comparison = comparison_df.copy()
                
                # Format currency
                for col in ['Revenue', 'Net_Income']:
                    if col in display_comparison.columns:
                        display_comparison[col] = display_comparison[col].apply(
                            lambda x: f"${x:,.0f}" if pd.notnull(x) and x != 0 else "-"
                        )
                
                # Format percentages
                for col in ['ROE', 'Net_Margin', 'Debt_Ratio']:
                    if col in display_comparison.columns:
                        display_comparison[col] = display_comparison[col].apply(
                            lambda x: f"{x:.2%}" if pd.notnull(x) and x != 0 else "-"
                        )
                
                # Format ratios
                if 'Current_Ratio' in display_comparison.columns:
                    display_comparison['Current_Ratio'] = display_comparison['Current_Ratio'].apply(
                        lambda x: f"{x:.2f}" if pd.notnull(x) and x != 0 else "-"
                    )
                
                st.dataframe(display_comparison, use_container_width=True)
                
                # Visual comparison charts
                st.markdown("### Visual Comparison")
                
                # Select metric for bar chart
                bar_metrics = [col for col in ['Revenue', 'Net_Income', 'ROE', 'Net_Margin'] 
                             if col in comparison_df.columns]
                
                if bar_metrics:
                    selected_metric = st.selectbox(
                        "Select metric for comparison chart:",
                        bar_metrics
                    )
                    
                    fig_comparison = px.bar(
                        comparison_df,
                        x='Company',
                        y=selected_metric,
                        title=f'{selected_metric.replace("_", " ")} Comparison',
                        color='Company',
                        text=selected_metric
                    )
                    
                    # Format based on metric type
                    if selected_metric in ['ROE', 'Net_Margin', 'Debt_Ratio']:
                        fig_comparison.update_layout(
                            yaxis_tickformat='.2%',
                            height=500
                        )
                        fig_comparison.update_traces(
                            texttemplate='%{text:.2%}',
                            textposition='outside'
                        )
                    elif selected_metric in ['Revenue', 'Net_Income']:
                        fig_comparison.update_layout(
                            yaxis_tickformat='$,.0f',
                            height=500
                        )
                        fig_comparison.update_traces(
                            texttemplate='$%{text:,.0f}',
                            textposition='outside'
                        )
                    else:
                        fig_comparison.update_layout(height=500)
                        fig_comparison.update_traces(
                            texttemplate='%{text:.2f}',
                            textposition='outside'
                        )
                    
                    st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab5:
        st.markdown('<h2 class="sub-header">Data Explorer</h2>', unsafe_allow_html=True)
        
        # Raw data explorer
        st.markdown("### Raw Data Explorer")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            explore_company = st.selectbox(
                "Select company:",
                ["All Companies"] + list(companies),
                key="explore_company"
            )
        
        with col2:
            explore_years = st.multiselect(
                "Select years:",
                sorted(data['Year'].unique()),
                default=sorted(data['Year'].unique())[-3:]
            )
        
        # Apply filters
        explore_data = data.copy()
        
        if explore_company != "All Companies":
            explore_data = explore_data[explore_data['Company'] == explore_company]
        
        if explore_years:
            explore_data = explore_data[explore_data['Year'].isin(explore_years)]
        
        # Display data
        st.dataframe(explore_data, use_container_width=True)
        
        # Data statistics
        st.markdown("### Data Statistics")
        
        if not explore_data.empty:
            stats_cols = st.columns(3)
            
            with stats_cols[0]:
                st.markdown("**Basic Statistics**")
                st.write(f"Records: {len(explore_data):,}")
                st.write(f"Companies: {explore_data['Company'].nunique()}")
                st.write(f"Years: {explore_data['Year'].nunique()}")
            
            with stats_cols[1]:
                st.markdown("**Numeric Columns**")
                numeric_cols = explore_data.select_dtypes(include=[np.number]).columns.tolist()
                st.write(f"Count: {len(numeric_cols)}")
                if numeric_cols:
                    st.write(f"Example: {numeric_cols[0]}")
            
            with stats_cols[2]:
                st.markdown("**Data Quality**")
                total_cells = explore_data.shape[0] * explore_data.shape[1]
                missing_cells = explore_data.isnull().sum().sum()
                missing_pct = (missing_cells / total_cells) * 100
                st.write(f"Missing Values: {missing_pct:.1f}%")
        
        # Data export
        st.markdown("### Export Data")
        
        export_cols = st.columns(3)
        
        with export_cols[0]:
            if st.button("Export Current View"):
                csv_data = explore_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="green_power_data_export.csv",
                    mime="text/csv"
                )
        
        with export_cols[1]:
            if st.button("Export All Data"):
                csv_data = data.to_csv(index=False)
                st.download_button(
                    label="Download All Data",
                    data=csv_data,
                    file_name="all_green_power_data.csv",
                    mime="text/csv"
                )
        
        with export_cols[2]:
            if st.button("Export Selected Company"):
                if not company_data.empty:
                    csv_data = company_data.to_csv(index=False)
                    st.download_button(
                        label=f"Download {selected_company}",
                        data=csv_data,
                        file_name=f"{selected_company}_data.csv",
                        mime="text/csv"
                    )

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: gray;">
    <p>International Green Power Utilities Financial Analysis Tool</p>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)