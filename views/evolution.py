import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

st.set_page_config(page_title="Evolution View",
                  page_icon="📈",
                  layout="wide")

st.title("📈 Wealth Evolution")

try:
    # Scope & Credentials Object
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets"]
    
    # Get credentials file path
    creds_path = Path(__file__).parent.parent / "cred" / "stmillion-06bb3f0018ea.json"
    if not creds_path.exists():
        st.error("Credentials file not found!")
        st.stop()
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(creds_path), scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet by URL, get data and create dataframe
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1tD6rHaHPCK_Va76QduwS-XKFIabMNrAYB_sGuH95PZM/edit?usp=sharing"
    money_sheet = client.open_by_url(spreadsheet_url)
    money_worksheet = money_sheet.worksheet("database")
    money_data = money_worksheet.get_all_values()
    
    if not money_data:
        st.warning("No data found in the spreadsheet!")
        st.stop()
    
    df = pd.DataFrame(money_data[1:], columns=money_data[0])
    
    # Clean and prepare data
    df['currency usd'] = df['currency usd'].replace('FALSE', float('nan'))
    df['currency usd'] = df['currency usd'].str.replace(',', '').str.strip()
    df['currency usd'] = pd.to_numeric(df['currency usd'], errors='coerce')
    df['currency usd'] = df['currency usd'].fillna(0)
    
    # Calculate key metrics
    df = df.sort_values('date')
    total_by_date = df.groupby('date')['currency usd'].sum()
    
    # Debug information
    with st.expander("Debug Information"):
        st.write("Raw values before processing:")
        st.dataframe(df[['date', 'currency usd', 'sub category']])
        st.write("\nTotal by date:")
        st.dataframe(total_by_date)
    
    if len(total_by_date) >= 2:
        first_value = total_by_date.iloc[0]
        last_value = total_by_date.iloc[-1]
        total_growth = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Initial Amount",
                f"${first_value:,.2f}",
                delta=None
            )
        with col2:
            st.metric(
                "Current Amount",
                f"${last_value:,.2f}",
                delta=f"${last_value - first_value:,.2f}"
            )
        with col3:
            st.metric(
                "Total Growth",
                f"{total_growth:.1f}%",
                delta=None
            )
    
    st.markdown("---")
    
    # Create trend chart
    trend_data = df.groupby('date')['currency usd'].sum().reset_index()
    fig_trend = go.Figure()
    
    # Add actual wealth line
    fig_trend.add_trace(go.Scatter(
        x=trend_data['date'],
        y=trend_data['currency usd'],
        name='Current Wealth',
        line=dict(color='#2ecc71', width=3)
    ))
    
    # Add target line
    target_amount = 1000000
    fig_trend.add_trace(go.Scatter(
        x=trend_data['date'],
        y=[target_amount] * len(trend_data),
        name='Target ($1M)',
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig_trend.update_layout(
        title='Wealth Evolution Over Time',
        xaxis_title='Date',
        yaxis_title='Total USD',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("---")
    
    # Create category evolution chart
    category_data = df.pivot_table(
        index='date',
        columns='sub category',
        values='currency usd',
        aggfunc='sum'
    ).fillna(0)
    
    fig_category = go.Figure()
    
    for category in category_data.columns:
        fig_category.add_trace(go.Scatter(
            x=category_data.index,
            y=category_data[category],
            name=category,
            stackgroup='one',
            mode='lines'
        ))
    
    fig_category.update_layout(
        title='Category Evolution Over Time',
        xaxis_title='Date',
        yaxis_title='USD Amount',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_category, use_container_width=True)
    
    # Show raw data in expander
    with st.expander("View Raw Data"):
        st.dataframe(df)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your Google Sheets credentials and connection.")