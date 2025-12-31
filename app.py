import streamlit as st
import msal
from pymongo import MongoClient

# --- THEME & CONFIG ---
st.set_page_config(page_title="Inara Designs Forex AI", layout="wide")

# --- AUTHENTICATION (Entra ID) ---
client_id = st.secrets["CLIENT_ID"]
tenant_id = st.secrets["TENANT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]
authority = f"https://login.microsoftonline.com/{tenant_id}"

app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

if "auth_token" not in st.session_state:
    st.title("Inara Designs | Enterprise Forex Portal")
    auth_url = app.get_authorization_request_url(scopes=["User.Read"])
    st.link_button("Login with inaradesigns.store", auth_url)
    st.stop()

# --- DATA CONNECTION ---
client = MongoClient(st.secrets["MONGO_URL"])
db = client.forex_db

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Live Quotes", "AI Suggestions", "Portfolio"])

# --- MAIN DASHBOARD ---
live_state = db.live_state.find_one({"id": "current_state"})

if page == "Overview":
    st.header("Executive Summary")
    if live_state:
        c1, c2, c3 = st.columns(3)
        c1.metric("Account Equity", f"${live_state['account']['equity']:,.2f}")
        c2.metric("Active Trades", len(live_state['positions']))
        c3.metric("AI Confidence", f"{live_state.get('ai_confidence', 0)}%")
        
        st.subheader("Recent Activity")
        st.dataframe(live_state['positions'])