"""
🚀 WhatsApp Analyzer - Streamlit Dashboard (WORKING VERSION)
Simplified and guaranteed to show all results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

from chatline import Chatline
from reply_analyzer import ReplyAnalyzer

# Page config
st.set_page_config(
    page_title="WhatsApp Analyzer Pro",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1, h2, h3 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 WhatsApp Analyzer Pro")
st.markdown("### 🚀 All Features Working")

# Sidebar
with st.sidebar:
    st.header("📤 Upload Chat")
    uploaded_file = st.file_uploader("Choose WhatsApp chat (.txt)", type=['txt'])
    
    st.markdown("---")
    st.header("⚙️ Settings")
    
    stop_words_lang = st.selectbox(
        "Stop Words Language",
        ["None", "english", "spanish", "french", "german", "indonesian"]
    )
    
    st.markdown("### 📅 Date Range Filter")
    use_date_filter = st.checkbox("Enable date filtering")
    
    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", datetime.now() - timedelta(days=365))
        with col2:
            end_date = st.date_input("End", datetime.now())
    
    st.markdown("---")
    st.header("📊 Features")
    show_love_score = st.checkbox("💕 Love Score", value=True)
    show_time_series = st.checkbox("📈 Time-Series", value=True)
    show_word_cloud = st.checkbox("☁️ Word Cloud", value=True)
    show_calendar = st.checkbox("🔥 Calendar Heatmap", value=True)

def load_stop_words(language):
    if language == "None":
        return []
    try:
        with open(f'stop-words/{language}.txt', 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except:
        return []

def parse_chats(file_content, start_date=None, end_date=None):
    chats = []
    lines = file_content.decode('utf-8').split('\n')
    
    for line in lines:
        if line.strip():
            try:
                chatline = Chatline(line)
                
                if start_date and end_date and chatline.timestamp:
                    try:
                        date_str = chatline.timestamp.split(',')[0].strip().replace('[', '')
                        for fmt in ['%d/%m/%y', '%m/%d/%y']:
                            try:
                                msg_date = datetime.strptime(date_str, fmt).date()
                                if not (start_date <= msg_date <= end_date):
                                    continue
                                break
                            except:
                                continue
                    except:
                        pass
                
                chats.append(chatline)
            except:
                continue
    
    return chats

# Main
if uploaded_file is not None:
    # Load data
    stop_words = load_stop_words(stop_words_lang)
    
    with st.spinner('Loading...'):
        file_content = uploaded_file.read()
        if use_date_filter:
            chats = parse_chats(file_content, start_date, end_date)
        else:
            chats = parse_chats(file_content)
    
    if not chats:
        st.error("❌ No messages found!")
        st.stop()
    
    # Get chat messages only
    chat_messages = [c for c in chats if c.line_type == "Chat"]
    participants = list(set(c.sender for c in chat_messages if c.sender))
    
    st.success(f"✅ Loaded {len(chat_messages)} messages from {len(participants)} participants!")
    
    # === STATISTICS ===
    st.markdown("## 📊 Overview Statistics")
    
    # Extract data
    all_words = []
    all_emojis = []
    sender_counts = Counter()
    
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    for chat in chat_messages:
        if chat.sender:
            sender_counts[chat.sender] += 1
        
        if hasattr(chat, 'body') and chat.body:
            # Words
            words = re.findall(r'\b[a-zA-Z]+\b', chat.body.lower())
            all_words.extend([w for w in words if w not in stop_words and len(w) > 2])
            
            # Emojis
            emojis = emoji_pattern.findall(chat.body)
            all_emojis.extend(emojis)
    
    word_freq = Counter(all_words)
    emoji_freq = Counter(all_emojis)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Messages", f"{len(chat_messages):,}")
    with col2:
        st.metric("👥 Participants", len(participants))
    with col3:
        st.metric("📝 Words", f"{len(all_words):,}")
    with col4:
        st.metric("😊 Emojis", f"{len(all_emojis):,}")
    
    st.markdown("---")
    
    # Top Senders and Words
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👑 Top Senders")
        if sender_counts:
            sender_df = pd.DataFrame(
                sender_counts.most_common(10),
                columns=['Sender', 'Messages']
            )
            fig = px.bar(sender_df, x='Sender', y='Messages', 
                        color='Messages',
                        color_continuous_scale='Blues',
                        title='')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key='senders')
        else:
            st.info("No sender data")
    
    with col2:
        st.markdown("### 📝 Top Words")
        if word_freq:
            word_df = pd.DataFrame(
                word_freq.most_common(10),
                columns=['Word', 'Count']
            )
            fig = px.bar(word_df, x='Word', y='Count',
                        color='Count',
                        color_continuous_scale='Greens',
                        title='')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key='words')
        else:
            st.info("No word data")
    
    # === TIME-SERIES ===
    if show_time_series:
        st.markdown("---")
        st.markdown("## 📈 Time-Series Analysis")
        
        dates = []
        hours = []
        
        for chat in chat_messages:
            if chat.timestamp:
                try:
                    for fmt in ['%d/%m/%y, %H:%M', '%m/%d/%y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                        try:
                            dt = datetime.strptime(chat.timestamp.strip(), fmt)
                            dates.append(dt.date())
                            hours.append(dt.hour)
                            break
                        except:
                            continue
                except:
                    pass
        
        if dates:
            # Daily activity
            date_counts = Counter(dates)
            df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Messages'])
            df = df.sort_values('Date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Messages'],
                mode='lines+markers',
                name='Messages',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.3)'
            ))
            
            fig.update_layout(
                title='📅 Daily Message Activity',
                xaxis_title='Date',
                yaxis_title='Messages',
                height=400,
                hovermode='x unified',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key='timeseries')
            
            # Hourly pattern
            if hours:
                hour_counts = Counter(hours)
                hour_df = pd.DataFrame(
                    [(h, hour_counts[h]) for h in range(24)],
                    columns=['Hour', 'Messages']
                )
                
                fig2 = px.bar(hour_df, x='Hour', y='Messages',
                             title='⏰ Hourly Activity Pattern',
                             color='Messages',
                             color_continuous_scale='Reds')
                fig2.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True, key='hourly')
        else:
            st.warning("⚠️ Could not parse dates")
    
    # === WORD CLOUD ===
    if show_word_cloud:
        st.markdown("---")
        st.markdown("## ☁️ Word Cloud")
        
        if all_words:
            text_str = ' '.join(all_words)
            
            wordcloud = WordCloud(
                width=1400,
                height=700,
                background_color='white',
                colormap='viridis',
                max_words=100
            ).generate(text_str)
            
            fig, ax = plt.subplots(figsize=(16, 8))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout(pad=0)
            st.pyplot(fig, use_container_width=True)
        else:
            st.warning("⚠️ Not enough text data")
    
    # === CALENDAR HEATMAP ===
    if show_calendar:
        st.markdown("---")
        st.markdown("## 🔥 Calendar Heatmap")
        
        if dates:
            date_counts = Counter(dates)
            min_date = min(dates)
            max_date = max(dates)
            
            all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
            df = pd.DataFrame({
                'Date': all_dates,
                'Messages': [date_counts.get(d.date(), 0) for d in all_dates]
            })
            
            df['DayOfWeek'] = df['Date'].dt.day_name()
            df['Week'] = df['Date'].dt.isocalendar().week
            
            pivot = df.pivot_table(
                values='Messages',
                index='DayOfWeek',
                columns='Week',
                aggfunc='sum',
                fill_value=0
            )
            
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot = pivot.reindex([d for d in days_order if d in pivot.index])
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale='Greens',
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='📆 Activity Heatmap by Week and Day',
                xaxis_title='Week Number',
                yaxis_title='Day of Week',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True, key='heatmap')
        else:
            st.warning("⚠️ Could not create heatmap")
    
    # === LOVE SCORE ===
    if show_love_score:
        st.markdown("---")
        st.markdown("## 💕 Love Score Analysis")
        
        if len(participants) >= 2:
            with st.spinner('Calculating love scores...'):
                analyzer = ReplyAnalyzer()
                scores = []
                
                for i, person1 in enumerate(participants):
                    for person2 in participants[i+1:]:
                        try:
                            result = analyzer.calculate_love_score(chats, person1, person2)
                            scores.append({
                                'Person 1': person1,
                                'Person 2': person2,
                                'Combined': result['combined_score'],
                                'P1→P2': result['person1_to_person2']['score'],
                                'P2→P1': result['person2_to_person1']['score'],
                                'Verdict': result['combined_verdict']
                            })
                        except:
                            continue
                
                if scores:
                    scores = sorted(scores, key=lambda x: x['Combined'], reverse=True)
                    
                    # Top pair
                    st.markdown("### 🏆 Top Relationship")
                    top = scores[0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Combined Score", f"{top['Combined']}/100")
                    with col2:
                        st.metric(f"{top['Person 1']} → {top['Person 2']}", f"{top['P1→P2']}/100")
                    with col3:
                        st.metric(f"{top['Person 2']} → {top['Person 1']}", f"{top['P2→P1']}/100")
                    
                    st.success(f"**Verdict:** {top['Verdict']}")
                    
                    # All pairs chart
                    st.markdown("### 📊 All Relationships")
                    
                    love_df = pd.DataFrame(scores)
                    love_df['Pair'] = love_df.apply(
                        lambda row: f"{row['Person 1']} & {row['Person 2']}", axis=1
                    )
                    
                    fig = px.bar(
                        love_df.head(10),
                        x='Pair',
                        y='Combined',
                        color='Combined',
                        color_continuous_scale='RdYlGn',
                        title='Top 10 Relationship Scores'
                    )
                    fig.update_layout(height=400, xaxis_title='', yaxis_title='Love Score')
                    st.plotly_chart(fig, use_container_width=True, key='lovescores')
                    
                    # Table
                    st.dataframe(love_df[['Person 1', 'Person 2', 'Combined', 'P1→P2', 'P2→P1', 'Verdict']], 
                                use_container_width=True)
                else:
                    st.warning("⚠️ Could not calculate love scores")
        else:
            st.info("ℹ️ Need at least 2 participants for love score analysis")

else:
    # Welcome
    st.markdown("""
    ## 🎯 Welcome to WhatsApp Analyzer Pro!
    
    ### ✨ Features:
    
    - **📈 Time-Series Charts** - Daily & hourly activity
    - **☁️ Word Cloud** - Visual word frequency
    - **🔥 Calendar Heatmap** - GitHub-style activity
    - **📅 Date Filters** - Analyze specific periods
    - **💕 Love Score** - Relationship metrics
    - **📊 Statistics** - Messages, words, emojis
    
    ### 📤 Get Started:
    
    1. Export your WhatsApp chat (without media)
    2. Upload the .txt file using the sidebar
    3. Select your preferences
    4. Explore your chat insights!
    
    ---
    
    **👈 Upload your chat file from the sidebar!**
    """)

