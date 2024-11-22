import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px

def get_conversion_rates():
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    my_request = requests.get(url)
    content = my_request.content
    data = json.loads(content)
    
    exchange_rates = {
        'USD': 1.0,  # Include USD in the rates
        'BRL': data['rates']['BRL'],
        'AUD': data['rates']['AUD'],
        'EUR': data['rates']['EUR'],
    }
    return exchange_rates

def convert_currency(amount, from_currency, to_currency, rates):
    # Ensure from_currency is valid
    if pd.isna(from_currency) or from_currency not in rates:
        return 0  # Or handle as necessary
    if from_currency == "USD":
        return amount * rates[to_currency]
    else:
        return (amount / rates[from_currency]) * rates[to_currency]

# Streamlit UI
st.title('Investment Portfolio Tracker')

uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    # Strip whitespace from column names
    data.columns = data.columns.str.strip()

    # Display the columns to check their names
    st.write("Columns in the uploaded file:", data.columns.tolist())
    st.write("Preview of the data:")
    st.write(data.head())

    # Convert 'amount' to numeric, forcing errors to NaN
    data['amount'] = pd.to_numeric(data['amount'], errors='coerce')

    # Replace NaN values in 'amount' with 0
    data['amount'].fillna(0, inplace=True)

    # Display unique currency values
    st.write("Unique currency values in the dataset:", data['currency'].unique())

    # Replace NaN values in 'currency' with a default value (e.g., 'USD')
    data['currency'].fillna('USD', inplace=True)  # Adjust as needed

    # Fetch conversion rates
    rates = get_conversion_rates()
    
    # Display fetched conversion rates
    st.write("Conversion rates fetched:", rates)

    # Ensure all necessary columns are present
    if all(col in data.columns for col in ['amount', 'currency']):
        # Convert amounts using conversion rates
        data['currency usd'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'USD', rates), axis=1)
        data['currency brl'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'BRL', rates), axis=1)
        data['currency aud'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'AUD', rates), axis=1)
        data['currency eu'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'EUR', rates), axis=1)

        # Add conversion rates to the DataFrame
        data['conv usd-brl'] = rates['BRL']
        data['conv usd-aud'] = rates['AUD']
        data['conv usd-eur'] = rates['EUR']

        # Visualization
        fig = px.bar(
            data,
            x='investment_name',
            y=['currency usd', 'currency brl', 'currency aud', 'currency eu'],
            labels={
                'currency usd': 'USD',
                'currency brl': 'BRL',
                'currency aud': 'AUD',
                'currency eu': 'EUR'
            },
            title="Investment Breakdown in All Currencies",
            barmode='group'
        )
        st.plotly_chart(fig)

        # Display the DataFrame
        st.write(data)
    else:
        st.error("Required columns 'amount' and 'currency' are missing in the uploaded file.")