import streamlit as st

st.title("🔍 WhatsApp Chat Analyzer - Diagnostic Mode")
st.write("Testing imports... Please wait...")
st.write("---")

# Test imports
try:
    import pandas as pd
    st.success("✅ pandas imported")
except Exception as e:
    st.error(f"❌ pandas: {e}")

try:
    import plotly.express as px
    st.success("✅ plotly imported")
except Exception as e:
    st.error(f"❌ plotly: {e}")

try:
    from src.analyzers.chatline import Chatline
    st.success("✅ chatline imported")
except Exception as e:
    st.error(f"❌ chatline: {e}")
