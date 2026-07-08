import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Správne načítanie štruktúry zo secrets
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Autorizácia pre gspread
gc = gspread.authorize(credentials)

# Otvorenie tabuľky
sh = gc.open("Databaza_Udalosti")
