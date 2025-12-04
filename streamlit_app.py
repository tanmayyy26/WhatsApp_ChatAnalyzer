#!/usr/bin/env python3
"""
WhatsApp Chat Analyzer - Streamlit App
Minimal version for Streamlit Cloud deployment
"""

try:
    import streamlit as st
    
    # ABSOLUTELY FIRST STREAMLIT COMMAND
    st.set_page_config(
        page_title="WhatsApp Analyzer",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 WhatsApp Chat Analyzer")
    st.write("App loaded successfully!")
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
