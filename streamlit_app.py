import streamlit as st

# MUST be first Streamlit command
st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬", layout="wide")

st.title("🔍 WhatsApp Chat Analyzer - Diagnostic")
st.write("Testing system imports...")
st.divider()

# Test 1: Basic Streamlit
st.success("✅ Streamlit is working")

# Test 2: Pandas
try:
    import pandas
    st.success("✅ Pandas imported")
except Exception as e:
    st.error(f"❌ Pandas: {str(e)[:80]}")

# Test 3: Plotly
try:
    import plotly
    st.success("✅ Plotly imported")
except Exception as e:
    st.error(f"❌ Plotly: {str(e)[:80]}")

# Test 4: Local modules
try:
    from src.analyzers.chatline import Chatline
    st.success("✅ Chatline imported")
except Exception as e:
    st.error(f"❌ Chatline: {str(e)[:80]}")

st.divider()
st.info("All tests completed!")

