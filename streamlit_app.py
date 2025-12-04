import streamlit as st

# ABSOLUTELY FIRST LINE
st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬", layout="wide")

st.title("💬 WhatsApp Chat Analyzer - DIAGNOSTIC MODE")
st.write("Testing each component individually...")

st.success("✅ Streamlit IS WORKING!")

# Test pandas
try:
    import pandas as pd
    st.success("✅ Pandas library loaded")
except ImportError as e:
    st.error(f"❌ Pandas import failed: {e}")

# Test plotly
try:
    import plotly.express as px
    st.success("✅ Plotly library loaded")
except ImportError as e:
    st.error(f"❌ Plotly import failed: {e}")

# Test dotenv
try:
    from dotenv import load_dotenv
    st.success("✅ dotenv library loaded")
except ImportError as e:
    st.error(f"❌ dotenv import failed: {e}")

# Test wordcloud
try:
    from wordcloud import WordCloud
    st.success("✅ wordcloud library loaded")
except ImportError as e:
    st.error(f"❌ wordcloud import failed: {e}")

# Test matplotlib
try:
    import matplotlib.pyplot as plt
    st.success("✅ matplotlib library loaded")
except ImportError as e:
    st.error(f"❌ matplotlib import failed: {e}")

# Test emoji
try:
    import emoji
    st.success("✅ emoji library loaded")
except ImportError as e:
    st.error(f"❌ emoji import failed: {e}")

# Test supabase
try:
    from supabase import create_client
    st.success("✅ supabase library loaded")
except ImportError as e:
    st.error(f"❌ supabase import failed: {e}")

# Test our chatline module
try:
    from src.analyzers.chatline import Chatline
    st.success("✅ Chatline module loaded from src.analyzers")
except ImportError as e:
    st.error(f"❌ Chatline module import failed: {e}")

# Test reply analyzer  
try:
    from src.analyzers.reply_analyzer import ReplyAnalyzer
    st.success("✅ ReplyAnalyzer module loaded from src.analyzers")
except ImportError as e:
    st.error(f"❌ ReplyAnalyzer module import failed: {e}")

# Test supabase client
try:
    from src.database.supabase_client import SupabaseManager
    st.success("✅ SupabaseManager module loaded from src.database")
except ImportError as e:
    st.error(f"❌ SupabaseManager module import failed: {e}")

st.divider()
st.info("✅ All imports above indicate what is working. If all show checkmarks, the app is ready!")
