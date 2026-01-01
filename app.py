import streamlit as st
import msal
from pymongo import MongoClient
import os

# --- THEME & CONFIG ---
st.set_page_config(page_title="Forex AI Dashboard", layout="wide", page_icon="📈")

# Custom CSS for purple theme
st.markdown("""
<style>
    .main-header {color: #7c3aed; font-size: 2.5rem; font-weight: bold;}
    .metric-card {background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .sidebar .sidebar-content {background: #f3f4f6;}
    .stButton>button {background: #7c3aed; color: white; border-radius: 10px;}
    .stButton>button:hover {background: #6d28d9;}
    .card {background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION (Entra ID) ---
client_id = os.environ["CLIENT_ID"]
tenant_id = os.environ["TENANT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
authority = f"https://login.microsoftonline.com/{tenant_id}"

app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

if "auth_token" not in st.session_state:
    st.markdown('<h1 class="main-header">Forex AI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; font-size: 1.1rem;">Enterprise Forex Trading Platform</p>', unsafe_allow_html=True)

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
        st.markdown(f'<a href="{auth_url}" target="_self" style="text-decoration: none;"><button style="background: #7c3aed; color: white; border: none; padding: 10px 20px; border-radius: 10px; font-size: 16px; cursor: pointer;">🔐 Login with Microsoft</button></a>', unsafe_allow_html=True)
    st.stop()

# --- DATA CONNECTION ---
client = MongoClient(os.environ["MONGO_URL"])
db = client.forex_db

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown('<h2 style="color: #7c3aed; font-weight: bold;">Navigation</h2>', unsafe_allow_html=True)
page = st.sidebar.radio("", ["📊 Overview", "💹 Live Quotes", "🤖 AI Suggestions", "📁 Portfolio"], label_visibility="collapsed")

# --- MAIN DASHBOARD ---
live_state = db.live_state.find_one({"id": "current_state"})

if page == "📊 Overview":
    st.markdown('<h2 class="main-header">Executive Summary</h2>', unsafe_allow_html=True)
    if live_state:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card"><div style="font-size: 0.9rem; opacity: 0.9;">Account Equity</div><div style="font-size: 2rem; font-weight: bold;">${:,.2f}</div></div>'.format(live_state['account']['equity']), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><div style="font-size: 0.9rem; opacity: 0.9;">Active Trades</div><div style="font-size: 2rem; font-weight: bold;">{}</div></div>'.format(len(live_state['positions'])), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card"><div style="font-size: 0.9rem; opacity: 0.9;">AI Confidence</div><div style="font-size: 2rem; font-weight: bold;">{}%</div></div>'.format(live_state.get('ai_confidence', 0)), unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card"><div style="font-size: 0.9rem; opacity: 0.9;">Current Signal</div><div style="font-size: 2rem; font-weight: bold;">{}</div></div>'.format(live_state.get('suggestion', 'N/A')), unsafe_allow_html=True)

        st.markdown('<div class="card"><h3 style="color: #7c3aed; margin-bottom: 15px;">Recent Activity</h3></div>', unsafe_allow_html=True)
        st.dataframe(live_state['positions'], use_container_width=True)
    else:
        st.info("📊 No data available. Please ensure the MT5 engine is running on your Windows 365 VM.")
        st.markdown("""
        **Expected Data:**
        - Account balance and equity
        - Active trading positions
        - AI trading signals
        """)

elif page == "💹 Live Quotes":
    st.markdown('<h2 class="main-header">Live Market Quotes</h2>', unsafe_allow_html=True)
    st.markdown('<div class="card"><p style="color: #6b7280;">Live quotes feature coming soon. This will display real-time forex prices.</p></div>', unsafe_allow_html=True)

elif page == "🤖 AI Suggestions":
    st.markdown('<h2 class="main-header">AI Trading Suggestions</h2>', unsafe_allow_html=True)
    if live_state and 'suggestion' in live_state:
        st.success(f"🎯 Current AI Signal: {live_state['suggestion']}")
        st.metric("AI Confidence", f"{live_state.get('ai_confidence', 0)}%")
    else:
        st.info("🤖 No AI suggestions available. Start the MT5 engine to generate signals.")

elif page == "📁 Portfolio":
    st.markdown('<h2 class="main-header">Portfolio Overview</h2>', unsafe_allow_html=True)
    if live_state and 'positions' in live_state:
        st.markdown('<div class="card"><h3 style="color: #7c3aed; margin-bottom: 15px;">Open Positions</h3></div>', unsafe_allow_html=True)
        st.dataframe(live_state['positions'], use_container_width=True)
    else:
        st.info("📁 No portfolio data available.")