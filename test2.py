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
    
    return {
        'USD': 1.0,
        'BRL': data['rates']['BRL'],
        'AUD': data['rates']['AUD'],
        'EUR': data['rates']['EUR'],
    }

def convert_currency(amount, from_currency, to_currency, rates):
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

    # Convert 'amount' to numeric, forcing errors to NaN
    data['amount'] = pd.to_numeric(data['amount'], errors='coerce')
    data['amount'].fillna(0, inplace=True)

    # Replace NaN values in 'currency' with a default value (e.g., 'USD')
    data['currency'].fillna('USD', inplace=True)

    # Fetch conversion rates
    rates = get_conversion_rates()

    # Ensure all necessary columns are present
    if all(col in data.columns for col in ['amount', 'currency']):
        # Convert amounts using conversion rates
        data['currency usd'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'USD', rates), axis=1)
        data['currency brl'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'BRL', rates), axis=1)
        data['currency aud'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'AUD', rates), axis=1)
        data['currency eu'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'EUR', rates), axis=1)

        # Visualization by Investment Name
        fig_investment = px.bar(
            data,
            x='investment_name',
            y=['currency usd', 'currency brl', 'currency aud', 'currency eu'],
            labels={
                'currency usd': 'USD',
                'currency brl': 'BRL',
                'currency aud': 'AUD',
                'currency eu': 'EUR'
            },
            title="Investment Breakdown by Investment Name",
            barmode='group'
        )
        st.plotly_chart(fig_investment)

        # Visualization by Category
        fig_category = px.bar(
            data,
            x='category',
            y=['currency usd', 'currency brl', 'currency aud', 'currency eu'],
            labels={
                'currency usd': 'USD',
                'currency brl': 'BRL',
                'currency aud': 'AUD',
                'currency eu': 'EUR'
            },
            title="Investment Breakdown by Category",
            barmode='group'
        )
        st.plotly_chart(fig_category)

        

        # Display the DataFrame
        st.write(data)
    else:
        st.error("Required columns 'amount' and 'currency' are missing in the uploaded file.")