import streamlit as st

st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬")

st.title("🔍 WhatsApp Chat Analyzer")
st.write("Diagnostic Mode - Testing System")
st.write("=" * 50)

# Test 1: Basic Streamlit
st.success("✅ Streamlit is working")

# Test 2: Pandas
try:
    import pandas
    st.success("✅ Pandas imported successfully")
except Exception as e:
    st.error(f"❌ Pandas failed: {str(e)[:100]}")

# Test 3: Plotly
try:
    import plotly
    st.success("✅ Plotly imported successfully")
except Exception as e:
    st.error(f"❌ Plotly failed: {str(e)[:100]}")

# Test 4: Our code
try:
    from src.analyzers.chatline import Chatline
    st.success("✅ Chatline imported successfully")
except Exception as e:
    st.error(f"❌ Chatline failed: {str(e)[:100]}")

st.write("=" * 50)
st.info("If all tests pass, the full app should work!")

