import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import os

# Constants
TARGET_AMOUNT = 1_000_000
SUPPORTED_CURRENCIES = ['AUD', 'BRL', 'EUR', 'USD']
BASE_DIR = Path(__file__).parent
CREDS_PATH = BASE_DIR / "cred" / "stmillion-06bb3f0018ea.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1tD6rHaHPCK_Va76QduwS-XKFIabMNrAYB_sGuH95PZM/edit?usp=sharing"

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def get_google_sheet_data():
    """Connect to Google Sheets and retrieve data"""
    try:
        if not CREDS_PATH.exists():
            st.error(f"Credentials file not found at: {CREDS_PATH}")
            st.info("Please make sure your Google Sheets credentials file is in the correct location.")
            return pd.DataFrame()  # Return empty DataFrame
            
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDS_PATH), scope)
        client = gspread.authorize(creds)
        
        try:
            money_sheet = client.open_by_url(SPREADSHEET_URL)
            money_worksheet = money_sheet.worksheet("database")
            money_data = money_worksheet.get_all_values()
            
            if not money_data:
                st.warning("No data found in the spreadsheet.")
                return pd.DataFrame()
                
            return pd.DataFrame(money_data[1:], columns=money_data[0])
            
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("Spreadsheet not found. Please check the URL.")
            return pd.DataFrame()
        except gspread.exceptions.WorksheetNotFound:
            st.error("Worksheet 'database' not found in the spreadsheet.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return pd.DataFrame()

def clean_money_data(df):
    """Clean and preprocess money data"""
    df = df.copy()
    
    # Clean amount column
    df.loc[:, 'amount'] = (df['amount']
                          .replace('-', '0')
                          .str.replace(',', '')
                          .str.replace('.', ''))
    df.loc[:, 'amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df.loc[:, 'amount'] = df['amount'].fillna(0)
    
    # Clean currency columns
    df.loc[:, 'currency'] = df['currency'].fillna('USD')
    df = df[df['currency'].isin(SUPPORTED_CURRENCIES)]
    
    # Clean USD conversion column
    df['currency usd'] = (df['currency usd']
                         .replace('FALSE', float('nan'))
                         .str.replace(',', ''))
    df['currency usd'] = pd.to_numeric(df['currency usd'], errors='coerce')
    df['currency usd'] = df['currency usd'].fillna(0)
    
    return df

def format_currency(amount, currency="USD"):
    """Format currency values for display"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "BRL":
        return f"R${amount:,.2f}"
    elif currency == "AUD":
        return f"A${amount:,.2f}"
    return f"{amount:,.2f}"

def calculate_progress(current_amount):
    """Calculate progress towards target amount"""
    progress = current_amount / TARGET_AMOUNT
    pending = TARGET_AMOUNT - current_amount
    return progress, pending

def setup_page(title, icon=":chart_with_upwards_trend:"):
    """Setup page configuration"""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
