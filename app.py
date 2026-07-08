import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Načítanie prihlasovacích údajov priamo zo Streamlit Secrets
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Pripojenie k službe
gc = gspread.authorize(credentials)

# Otvorenie tabuľky
sh = gc.open("Databaza_Udalosti")
