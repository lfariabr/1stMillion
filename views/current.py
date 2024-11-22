import streamlit as st
import plotly.express as px
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Evolution",
                    page_icon=":bar_chart:", 
                    layout="wide")

st.title("Current Money Breakdown")

# Scope & Credentials Object
scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("cred/stmillion-06bb3f0018ea.json", scope)
client = gspread.authorize(creds)

# Open the spreadsheet by URL, get data and create dataframe
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1tD6rHaHPCK_Va76QduwS-XKFIabMNrAYB_sGuH95PZM/edit?usp=sharing"
money_sheet = client.open_by_url(spreadsheet_url)
money_worksheet = money_sheet.worksheet("database")
money_data = money_worksheet.get_all_values()
money_df = pd.DataFrame(money_data[1:], columns=money_data[0])

# Filter out the unique periods for the dropdown
unique_periods = money_df['date'].dropna().unique()
selected_period = st.selectbox("Select a period:", unique_periods)
filtered_money_df = money_df[money_df['date'] == selected_period]

# Treatments
# Replace '-' with 0
filtered_money_df.loc[:, 'amount'] = filtered_money_df['amount'].replace('-', 0)
filtered_money_df.loc[:, 'amount'] = filtered_money_df['amount'].str.replace(',', '')
filtered_money_df.loc[:, 'amount'] = filtered_money_df['amount'].str.replace('.', '')
filtered_money_df.loc[:, 'amount'] = pd.to_numeric(filtered_money_df['amount'], errors='coerce')
filtered_money_df.loc[:, 'amount'] = filtered_money_df['amount'].fillna(0)
filtered_money_df.loc[:, 'currency'] = filtered_money_df['currency'].fillna('USD')

desired_currencies = ['AUD', 'BRL', 'EUR', 'USD']
filtered_money_df = filtered_money_df[filtered_money_df['currency'].isin(desired_currencies)]

# Format the total for better readability
filtered_money_df['currency usd'] = filtered_money_df['currency usd'].replace('FALSE', float('nan'))
filtered_money_df['currency usd'] = filtered_money_df['currency usd'].str.replace(',', '')
filtered_money_df['currency usd'] = pd.to_numeric(filtered_money_df['currency usd'], errors='coerce')
filtered_money_df['currency usd'].fillna(0, inplace=True)
total_currency_in_usd = filtered_money_df['currency usd'].sum()

##################
# Progress monitor
col1, col2 = st.columns(2)
with col1:
    st.write("#### Total amount in USD:")
    st.markdown(f"#### U$: {total_currency_in_usd:,.0f}")

    # Create a progress bar
    target_amount = 1000000
    progress_value = total_currency_in_usd / target_amount  # Calculate the progress as a fraction

with col2:
    pending_amount = target_amount - total_currency_in_usd
    st.write(f"#### Pending to achieve {target_amount:,.0f} USD:")
    st.markdown(f"#### U$: {pending_amount:,.0f}")

st.progress(progress_value)  # Update the progress bar

st.markdown("---")

##################
# Currency breakdown
col1, col2 = st.columns(2)
with col1: # Pizza chart currency display
    groupby_currency = filtered_money_df.groupby('currency').agg({'amount': 'sum'}).reset_index()
    fig_currency = px.pie(
        groupby_currency,
        values='amount',
        names='currency',
        title='Currencies you have:',
        labels={'amount': 'Total Amount', 'currency': 'Currency'}
    )
    st.plotly_chart(fig_currency)

with col2: # Bar chart currency x category
    groupby_category = filtered_money_df.groupby(['sub category', 'currency']).agg({'amount': 'sum'}).reset_index()
    fig_category = px.bar(
        groupby_category,
        x='sub category',
        y='amount',
        color='currency',
        title='Amount x Currency x Category',
        labels={'amount': 'Total', 'sub category': 'Category', 'currency': 'Currency'}
    )
    st.plotly_chart(fig_category)

st.markdown("---")

# Show the filtered DataFrame
st.write("Filtered Data:")
st.dataframe(filtered_money_df)