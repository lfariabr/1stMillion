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

    # Convert 'date' to datetime
    data['date'] = pd.to_datetime(data['date'])

    # Fetch conversion rates
    rates = get_conversion_rates()

    # Ensure all necessary columns are present
    if all(col in data.columns for col in ['amount', 'currency']):
        # Convert amounts using conversion rates
        data['currency usd'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'USD', rates), axis=1)
        data['currency brl'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'BRL', rates), axis=1)
        data['currency aud'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'AUD', rates), axis=1)
        data['currency eur'] = data.apply(lambda x: convert_currency(x['amount'], x['currency'], 'EUR', rates), axis=1)

        # DIV 1
        # Displaying the df 
        st.title("Dataframe")
        st.write(data)

        # DIV 2 - CURRENT PERIOD
        # Visualization by Investment Name
        fig_investment = px.bar(
            data,
            x='investment_name',
            y=['currency usd'],
            labels={
                'currency usd': 'USD',
            },
            title="Investment Breakdown by Investment Name",
        )
        st.plotly_chart(fig_investment)

        # DIV 3 - CURRENT PERIOD
        # Visualization by Category 
        fig_category = px.bar(
            data,
            x='category',
            y=['currency usd'],
            labels={
                'currency usd': 'USD',
            },
            title="Investment Breakdown by Category",
        )
        st.plotly_chart(fig_category)

        # DIV 4 - CURRENT PERIOD
        # SEEING TOTALS IN ALL CURRENCIES AND CONVERSION RATES
        # Calculating the totals for visualization
        total_in_usd = data['currency usd'].sum()
        total_in_brl = data['currency brl'].sum()
        total_in_aud = data['currency aud'].sum()
        total_in_eur = data['currency eur'].sum()
        
        # Calculate the total amounts and conversions
        summary_data = {
            'Description': [
                'Total in USD', 
                'Total in EUR', 
                'Total in AUD', 
                'Total in BRL', 
                'Conversion BRL -> AUD', 
                'Conversion BRL -> USD', 
                'Conversion BRL -> EUR'
            ],
            'Amount': [
                total_in_usd,
                total_in_eur,
                total_in_aud,
                total_in_brl,
                total_in_brl / total_in_usd if total_in_usd != 0 else 0,  # Handle division by zero
                total_in_brl / total_in_aud if total_in_aud != 0 else 0,  # Handle division by zero
                total_in_brl / total_in_eur if total_in_eur != 0 else 0   # Handle division by zero
            ]
        }

        # Create a DataFrame for the summary
        summary_df = pd.DataFrame(summary_data)

        # Display the summary table
        st.table(summary_df)

        # Bar chart for total amounts in USD and converted currencies
        total_data = {
            'Currency': ['USD', 'EUR', 'AUD', 'BRL'],
            'Total': [total_in_usd, total_in_eur, total_in_aud, total_in_brl]
        }

        total_df = pd.DataFrame(total_data)

        fig_total = px.bar(
            total_df,
            x='Currency',
            y='Total',
            title='Total Investment Amount by Currency'
        )
        
        st.plotly_chart(fig_total)

        # Groupby amount and currency on the "amount" column
        group_data = data.groupby('currency').agg({'amount': 'sum'}).reset_index()

        # Pizza chart for groupby amount and currency
        fig_group = px.pie(
            group_data,
            values='amount',
            names='currency',
            title='Groupby Amount and Currency'
        )
        
        st.plotly_chart(fig_group)

        # Group by month and sum the total revenue in USD
        data['month'] = data['date'].dt.strftime('%Y-%m')  # Convert to string in format YYYY-MM
        monthly_revenue = data.groupby('month').agg({'currency usd': 'sum'}).reset_index()
        
        #####
        # Testing the display of currency by month
        st.title("In a table")
        #####
        data_month = data.groupby(['month', 'currency']).agg({'amount': 'sum'},).reset_index()
        # Create a new column for 'currency in usd'
        data_month['currency in usd'] = data_month.apply(
            lambda x: convert_currency(x['amount'], x['currency'], 'USD', rates), axis=1
        )
        # Calculate the totals
        total_row = {
            'month': 'Total',  # Label for the total row
            'currency': '',    # Leave currency blank for the total row
            'amount': data_month['amount'].sum(),  # Total amount
            'currency in usd': data_month['currency in usd'].sum()  # Total in USD
        }

        # Create a DataFrame for the total row
        total_row_df = pd.DataFrame([total_row])  # Create DataFrame from the total_row dict

        # Append the total row to the DataFrame using pd.concat
        data_month = pd.concat([data_month, total_row_df], ignore_index=True)
        # Display the DataFrame
        st.write(data_month)



    else:
        st.error("Required columns 'amount' and 'currency' are missing in the uploaded file.")