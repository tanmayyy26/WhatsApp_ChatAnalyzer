"""
WhatsApp Analyzer - WITH SUPABASE INTEGRATION
Store and retrieve chat analysis from cloud database!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import Counter
import re
import os
from dotenv import load_dotenv

# Load environment variables FIRST before importing supabase_client
load_dotenv()

from chatline import Chatline
from reply_analyzer import ReplyAnalyzer
from supabase_client import supabase_manager

st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬", layout="wide")

st.title("💬 WhatsApp Analyzer")
st.markdown("Upload your chat file to see the magic! ✨")

# Supabase connection check (silent - no UI message)

# Sidebar
uploaded_file = st.sidebar.file_uploader("📤 Upload WhatsApp chat (.txt)", type=['txt'])

if uploaded_file:
    # Auto-save file to Supabase Storage bucket (silently)
    if supabase_manager.is_connected():
        file_bytes = uploaded_file.getvalue()
        supabase_manager.save_file(uploaded_file.name, file_bytes)
    
    # Parse with proper previous_line handling
    content = uploaded_file.getvalue().decode('utf-8')
    lines = content.split('\n')
    
    chats = []
    previous_chat = None
    for line in lines:
        if line.strip():
            try:
                chat = Chatline(line, previous_line=previous_chat)
                chats.append(chat)
                previous_chat = chat
            except:
                pass
    
    # Filter chat messages
    msgs = [c for c in chats if c.line_type == "Chat"]
    
    st.success(f"✅ Found {len(msgs)} messages!")
    
    if len(msgs) == 0:
        st.error("No messages found!")
        st.stop()
    
    # Basic stats
    senders = [c.sender for c in msgs if c.sender]
    sender_counts = Counter(senders)
    
    # Words
    words = []
    for msg in msgs:
        if hasattr(msg, 'body') and msg.body:
            w = re.findall(r'\b[a-zA-Z]{3,}\b', msg.body.lower())
            words.extend(w)
    
    word_counts = Counter(words)
    
    # Display
    st.header("📊 Statistics")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Messages", len(msgs))
    c2.metric("Participants", len(set(senders)))
    c3.metric("Words", len(words))
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👑 Top Senders")
        if sender_counts:
            df = pd.DataFrame(sender_counts.most_common(10), columns=['Sender', 'Count'])
            st.bar_chart(df.set_index('Sender'))
    
    with col2:
        st.subheader("📝 Top Words")
        if word_counts:
            df = pd.DataFrame(word_counts.most_common(10), columns=['Word', 'Count'])
            st.bar_chart(df.set_index('Word'))
    
    st.markdown("---")
    
    # Love Score
    st.header("💕 Love Score")
    
    participants = list(set(senders))
    
    if len(participants) >= 2:
        analyzer = ReplyAnalyzer(chats)
        
        scores = []
        for i in range(len(participants)):
            for j in range(i+1, len(participants)):
                try:
                    result = analyzer.analyze_pair(participants[i], participants[j])
                    combined_score = (result['target']['love_score'] + result['counterpart']['love_score']) / 2
                    scores.append({
                        'Person 1': participants[i],
                        'Person 2': participants[j],
                        'Score': combined_score
                    })
                except:
                    pass
        
        if scores:
            scores.sort(key=lambda x: x['Score'], reverse=True)
            
            # Top
            top = scores[0]
            st.success(f"🏆 **Top Pair:** {top['Person 1']} & {top['Person 2']}")
            st.metric("Combined Love Score", f"{top['Score']}/100")
            
            # Table
            st.dataframe(pd.DataFrame(scores))
    else:
        st.info("Need at least 2 participants")
    
    st.markdown("---")
    
    # Time Series
    st.header("📈 Activity Over Time")
    
    dates = []
    for msg in msgs:
        if msg.timestamp:
            try:
                # Parse datetime object directly from timestamp
                if isinstance(msg.timestamp, datetime):
                    dates.append(msg.timestamp.date())
                elif isinstance(msg.timestamp, str):
                    # Try to parse string timestamp
                    ts = msg.timestamp.strip().replace('[', '').replace(']', '')
                    # Try common formats (US format first since chat_example.txt uses M/D/YY)
                    for fmt in ['%m/%d/%y, %H:%M', '%d/%m/%y, %H:%M', '%Y-%m-%d %H:%M:%S', '%d/%m/%y %H.%M.%S']:
                        try:
                            dt = datetime.strptime(ts, fmt)
                            dates.append(dt.date())
                            break
                        except:
                            continue
            except:
                pass
    
    if dates:
        date_counts = Counter(dates)
        df = pd.DataFrame(sorted(date_counts.items()), columns=['Date', 'Messages'])
        st.line_chart(df.set_index('Date'))
    else:
        st.warning("Could not parse dates")
    
    st.markdown("---")
    
    # Word Cloud Data
    st.header("☁️ Most Used Words")
    if word_counts:
        top_words = word_counts.most_common(20)
        for word, count in top_words[:10]:
            st.text(f"{word}: {count}")
    


else:
    st.info("👈 Upload a WhatsApp chat file from the sidebar to begin!")
    
    st.markdown("""
    ### How to export WhatsApp chat:
    
    **Android:**
    - Open chat → ⋮ → More → Export chat → Without Media
    
    **iOS:**
    - Open chat → Contact name → Export Chat → Without Media
    """)
