import sys
import streamlit as st

# ABSOLUTELY FIRST - No other imports before this!
st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬", layout="wide")

st.title("💬 WhatsApp Chat Analyzer - SUPER MINIMAL DIAGNOSTIC")
st.write("If you see this, Streamlit IS working!")
st.success("✅ Streamlit initialization successful!")

# Now test pandas AFTER page config
st.subheader("Testing libraries...")
try:
    import pandas
    st.success("✅ Pandas OK")
except Exception as e:
    st.error(f"❌ Pandas: {e}")

# Test plotly
try:
    import plotly
    st.success("✅ Plotly OK")
except Exception as e:
    st.error(f"❌ Plotly: {e}")

# Test our modules
try:
    import src
    st.success("✅ src package OK")
except Exception as e:
    st.error(f"❌ src package: {e}")
