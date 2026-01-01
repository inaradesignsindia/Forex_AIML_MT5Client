import streamlit as st
import msal
from pymongo import MongoClient
import os

# --- THEME & CONFIG ---
st.set_page_config(page_title="Inara Designs Forex AI", layout="wide")

# --- AUTHENTICATION (Entra ID) ---
client_id = os.environ["CLIENT_ID"]
tenant_id = os.environ["TENANT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
authority = f"https://login.microsoftonline.com/{tenant_id}"

app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

if "auth_token" not in st.session_state:
    st.title("Inara Designs | Enterprise Forex Portal")
    
    # Check if authorization code is in the URL
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        try:
            result = app.acquire_token_by_authorization_code(code, scopes=["User.Read"], redirect_uri=os.environ.get("REDIRECT_URI", "https://forex-ai-dashboard-xepi.onrender.com"))
            if "access_token" in result:
                st.session_state.auth_token = result
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed. Please try again.")
        except Exception as e:
            st.error(f"Error during login: {str(e)}")
    else:
        auth_url = app.get_authorization_request_url(scopes=["User.Read"], redirect_uri=os.environ.get("REDIRECT_URI", "https://forex-ai-dashboard-xepi.onrender.com"))
        st.link_button("Login with inaradesigns.store", auth_url)
    st.stop()

# --- DATA CONNECTION ---
client = MongoClient(os.environ["MONGO_URL"])
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
    else:
        st.info("No data available. Please ensure the MT5 engine is running on your Windows 365 VM.")
        st.write("**Expected Data:**")
        st.write("- Account balance and equity")
        st.write("- Active trading positions")
        st.write("- AI trading signals")

elif page == "Live Quotes":
    st.header("Live Market Quotes")
    st.info("Live quotes feature coming soon. This will display real-time forex prices.")

elif page == "AI Suggestions":
    st.header("AI Trading Suggestions")
    if live_state and 'suggestion' in live_state:
        st.success(f"Current AI Signal: {live_state['suggestion']}")
        st.metric("AI Confidence", f"{live_state.get('ai_confidence', 0)}%")
    else:
        st.info("No AI suggestions available. Start the MT5 engine to generate signals.")

elif page == "Portfolio":
    st.header("Portfolio Overview")
    if live_state and 'positions' in live_state:
        st.subheader("Open Positions")
        st.dataframe(live_state['positions'])
    else:
        st.info("No portfolio data available.")