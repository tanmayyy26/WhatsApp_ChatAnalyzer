"""
🚀 WhatsApp Analyzer - Streamlit Dashboard
Modern UI with all 5 advanced features:
1. Time-series charts (activity over time)
2. Word clouds
3. Calendar heatmaps
4. Better UI (Streamlit)
5. Date range filters
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import io
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

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: white;
    }
    .uploadedFile {
        background: white;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("💬 WhatsApp Analyzer Pro")
st.markdown("### 🚀 Advanced Chat Analysis with Love Score, Time-Series, Word Clouds & More")

# Sidebar
with st.sidebar:
    st.header("📤 Upload Chat")
    uploaded_file = st.file_uploader("Choose WhatsApp chat export (.txt)", type=['txt'])
    
    st.markdown("---")
    st.header("⚙️ Settings")
    
    # Stop words
    stop_words_lang = st.selectbox(
        "Stop Words Language",
        ["None", "english", "spanish", "french", "german", "indonesian", "hindi", "arabic"]
    )
    
    # Date range filter
    st.markdown("### 📅 Date Range Filter")
    use_date_filter = st.checkbox("Enable date filtering")
    
    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
    
    st.markdown("---")
    st.header("📊 Visualizations")
    show_love_score = st.checkbox("💕 Love Score", value=True)
    show_time_series = st.checkbox("📈 Time-Series Charts", value=True)
    show_word_cloud = st.checkbox("☁️ Word Cloud", value=True)
    show_calendar_heatmap = st.checkbox("🔥 Calendar Heatmap", value=True)
    show_statistics = st.checkbox("📊 Statistics", value=True)

def load_stop_words(language):
    """Load stop words for given language"""
    if language == "None":
        return []
    try:
        with open(f'stop-words/{language}.txt', 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except:
        return []

def parse_chat_file(file_content, start_date=None, end_date=None):
    """Parse WhatsApp chat file"""
    chats = []
    lines = file_content.decode('utf-8').split('\n')
    
    for line in lines:
        if line.strip():
            chatline = Chatline(line)
            
            # Date filtering
            if start_date and end_date and chatline.timestamp:
                try:
                    msg_date = datetime.strptime(chatline.timestamp.split(',')[0], '%d/%m/%y')
                    if not (start_date <= msg_date.date() <= end_date):
                        continue
                except:
                    pass
            
            chats.append(chatline)
    
    return chats

def get_basic_stats(chats, stop_words):
    """Calculate basic statistics"""
    total_messages = sum(1 for c in chats if c.line_type == "Chat")
    participants = list(set(c.sender for c in chats if c.sender))
    
    # Words
    all_words = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.body:
            words = re.findall(r'\b[a-zA-Z]+\b', chat.body.lower())
            all_words.extend([w for w in words if w not in stop_words and len(w) > 2])
    
    word_freq = Counter(all_words)
    
    # Emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    all_emojis = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.body:
            emojis = emoji_pattern.findall(chat.body)
            all_emojis.extend(emojis)
    
    emoji_freq = Counter(all_emojis)
    
    # Sender stats
    sender_counts = Counter(c.sender for c in chats if c.line_type == "Chat" and c.sender)
    
    return {
        'total_messages': total_messages,
        'participants': participants,
        'word_freq': word_freq,
        'emoji_freq': emoji_freq,
        'sender_counts': sender_counts,
        'total_words': sum(word_freq.values()),
        'unique_words': len(word_freq),
        'total_emojis': sum(emoji_freq.values())
    }

def create_time_series_data(chats):
    """Create time-series data for activity charts"""
    dates = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.timestamp:
            try:
                # Try different date formats
                for fmt in ['%d/%m/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                    try:
                        dt = datetime.strptime(chat.timestamp, fmt)
                        dates.append(dt.date())
                        break
                    except:
                        continue
            except:
                pass
    
    if not dates:
        return None
    
    # Count messages per day
    date_counts = Counter(dates)
    df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Messages'])
    df = df.sort_values('Date')
    
    return df

def create_hourly_data(chats):
    """Create hourly activity data"""
    hours = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.timestamp:
            try:
                for fmt in ['%d/%m/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                    try:
                        dt = datetime.strptime(chat.timestamp, fmt)
                        hours.append(dt.hour)
                        break
                    except:
                        continue
            except:
                pass
    
    hour_counts = Counter(hours)
    return hour_counts

def create_calendar_heatmap_data(chats):
    """Create calendar heatmap data (GitHub style)"""
    dates = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.timestamp:
            try:
                for fmt in ['%d/%m/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                    try:
                        dt = datetime.strptime(chat.timestamp, fmt)
                        dates.append(dt.date())
                        break
                    except:
                        continue
            except:
                pass
    
    if not dates:
        return None
    
    # Count messages per day
    date_counts = Counter(dates)
    
    # Create DataFrame
    min_date = min(dates)
    max_date = max(dates)
    
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    df = pd.DataFrame({
        'Date': all_dates,
        'Messages': [date_counts.get(d.date(), 0) for d in all_dates]
    })
    
    # Add day of week and week number
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Year'] = df['Date'].dt.year
    
    return df

def generate_word_cloud(chats, stop_words):
    """Generate word cloud from messages"""
    text = []
    for chat in chats:
        if chat.line_type == "Chat" and chat.body:
            words = re.findall(r'\b[a-zA-Z]+\b', chat.body.lower())
            text.extend([w for w in words if w not in stop_words and len(w) > 2])
    
    if not text:
        return None
    
    text_str = ' '.join(text)
    
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        colormap='viridis',
        max_words=100,
        relative_scaling=0.5,
        min_font_size=10
    ).generate(text_str)
    
    return wordcloud

def calculate_love_scores(chats):
    """Calculate love scores for all pairs"""
    participants = list(set(c.sender for c in chats if c.sender and c.line_type == "Chat"))
    
    if len(participants) < 2:
        return None
    
    analyzer = ReplyAnalyzer()
    scores = []
    
    for i, person1 in enumerate(participants):
        for person2 in participants[i+1:]:
            result = analyzer.calculate_love_score(chats, person1, person2)
            scores.append({
                'Person 1': person1,
                'Person 2': person2,
                'Combined Score': result['combined_score'],
                'P1→P2': result['person1_to_person2']['score'],
                'P2→P1': result['person2_to_person1']['score'],
                'Verdict': result['combined_verdict']
            })
    
    return sorted(scores, key=lambda x: x['Combined Score'], reverse=True)

# Main app
if uploaded_file is not None:
    # Load stop words
    stop_words = load_stop_words(stop_words_lang)
    
    # Parse chat
    with st.spinner('📂 Loading chat file...'):
        file_content = uploaded_file.read()
        
        if use_date_filter:
            chats = parse_chat_file(file_content, start_date, end_date)
        else:
            chats = parse_chat_file(file_content)
    
    if not chats:
        st.error("❌ No messages found in the selected date range!")
        st.stop()
    
    st.success(f"✅ Loaded {len([c for c in chats if c.line_type == 'CHAT'])} messages!")
    
    # Calculate statistics
    with st.spinner('🔍 Analyzing chat...'):
        stats = get_basic_stats(chats, stop_words)
    
    # Display statistics
    if show_statistics:
        st.markdown("## 📊 Overview Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💬 Total Messages", f"{stats['total_messages']:,}")
        with col2:
            st.metric("👥 Participants", len(stats['participants']))
        with col3:
            st.metric("📝 Total Words", f"{stats['total_words']:,}")
        with col4:
            st.metric("😊 Total Emojis", f"{stats['total_emojis']:,}")
        
        st.markdown("---")
        
        # Top senders
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👑 Top Senders")
            sender_df = pd.DataFrame(
                stats['sender_counts'].most_common(10),
                columns=['Sender', 'Messages']
            )
            fig = px.bar(sender_df, x='Sender', y='Messages', color='Messages',
                        color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📝 Top Words")
            word_df = pd.DataFrame(
                stats['word_freq'].most_common(10),
                columns=['Word', 'Count']
            )
            fig = px.bar(word_df, x='Word', y='Count', color='Count',
                        color_continuous_scale='Greens')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Time-Series Charts
    if show_time_series:
        st.markdown("---")
        st.markdown("## 📈 Time-Series Analysis")
        
        ts_data = create_time_series_data(chats)
        
        if ts_data is not None and len(ts_data) > 0:
            # Daily activity line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ts_data['Date'],
                y=ts_data['Messages'],
                mode='lines+markers',
                name='Messages per Day',
                line=dict(color='#667eea', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)'
            ))
            
            fig.update_layout(
                title='Daily Message Activity',
                xaxis_title='Date',
                yaxis_title='Number of Messages',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly aggregation
            if len(ts_data) > 7:
                ts_data['Week'] = pd.to_datetime(ts_data['Date']).dt.to_period('W').astype(str)
                weekly = ts_data.groupby('Week')['Messages'].sum().reset_index()
                
                fig2 = px.bar(weekly, x='Week', y='Messages',
                             title='Weekly Message Volume',
                             color='Messages',
                             color_continuous_scale='Purples')
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Hourly heatmap
            hour_data = create_hourly_data(chats)
            if hour_data:
                hour_df = pd.DataFrame(
                    [(h, count) for h, count in sorted(hour_data.items())],
                    columns=['Hour', 'Messages']
                )
                
                fig3 = px.bar(hour_df, x='Hour', y='Messages',
                             title='Hourly Activity Pattern',
                             color='Messages',
                             color_continuous_scale='Reds')
                fig3.update_layout(height=400)
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("⚠️ Could not parse dates for time-series analysis")
    
    # Word Cloud
    if show_word_cloud:
        st.markdown("---")
        st.markdown("## ☁️ Word Cloud")
        
        with st.spinner('Generating word cloud...'):
            wordcloud = generate_word_cloud(chats, stop_words)
        
        if wordcloud:
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout(pad=0)
            st.pyplot(fig)
        else:
            st.warning("⚠️ Not enough text data to generate word cloud")
    
    # Calendar Heatmap
    if show_calendar_heatmap:
        st.markdown("---")
        st.markdown("## 🔥 Calendar Heatmap (GitHub Style)")
        
        cal_data = create_calendar_heatmap_data(chats)
        
        if cal_data is not None and len(cal_data) > 0:
            # Create pivot table for heatmap
            pivot = cal_data.pivot_table(
                values='Messages',
                index='DayOfWeek',
                columns='Week',
                aggfunc='sum',
                fill_value=0
            )
            
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot = pivot.reindex([d for d in days_order if d in pivot.index])
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale='Greens',
                hoverongaps=False,
                hovertemplate='Week: %{x}<br>Day: %{y}<br>Messages: %{z}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Message Activity Heatmap (by Week and Day)',
                xaxis_title='Week Number',
                yaxis_title='Day of Week',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Alternative: Date-based heatmap
            st.markdown("### 📅 Full Calendar View")
            
            # Limit to last 365 days for better visualization
            recent_data = cal_data[cal_data['Date'] >= (cal_data['Date'].max() - pd.Timedelta(days=365))]
            
            fig2 = px.density_heatmap(
                recent_data,
                x=recent_data['Date'].dt.month_name(),
                y=recent_data['Date'].dt.day,
                z='Messages',
                color_continuous_scale='YlOrRd',
                title='Daily Activity by Month'
            )
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("⚠️ Could not create calendar heatmap")
    
    # Love Score Analysis
    if show_love_score:
        st.markdown("---")
        st.markdown("## 💕 Love Score Analysis")
        
        with st.spinner('Calculating love scores...'):
            love_scores = calculate_love_scores(chats)
        
        if love_scores:
            # Display as table
            love_df = pd.DataFrame(love_scores)
            
            # Top pair highlight
            st.markdown("### 🏆 Top Relationship")
            top = love_scores[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Combined Score", f"{top['Combined Score']}/100")
            with col2:
                st.metric(f"{top['Person 1']} → {top['Person 2']}", f"{top['P1→P2']}/100")
            with col3:
                st.metric(f"{top['Person 2']} → {top['Person 1']}", f"{top['P2→P1']}/100")
            
            st.success(f"**Verdict:** {top['Verdict']}")
            
            # All pairs
            st.markdown("### 📊 All Relationship Scores")
            
            # Bar chart
            fig = px.bar(
                love_df.head(10),
                x=love_df.head(10).apply(lambda row: f"{row['Person 1']} & {row['Person 2']}", axis=1),
                y='Combined Score',
                color='Combined Score',
                color_continuous_scale='RdYlGn',
                title='Top 10 Relationships by Love Score'
            )
            fig.update_layout(height=400, xaxis_title='Pair', yaxis_title='Love Score')
            st.plotly_chart(fig, use_container_width=True)
            
            # Full table
            st.dataframe(love_df, use_container_width=True)
        else:
            st.warning("⚠️ Need at least 2 participants for love score analysis")
    
    # Export options
    st.markdown("---")
    st.markdown("## 📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Statistics (JSON)", use_container_width=True):
            export_data = {
                'overview': {
                    'total_messages': stats['total_messages'],
                    'participants': stats['participants'],
                    'total_words': stats['total_words'],
                    'unique_words': stats['unique_words']
                },
                'top_senders': dict(stats['sender_counts'].most_common(10)),
                'top_words': dict(stats['word_freq'].most_common(20)),
                'top_emojis': dict(stats['emoji_freq'].most_common(20))
            }
            
            json_str = str(export_data)
            st.download_button(
                "Download JSON",
                json_str,
                "whatsapp_analysis.json",
                "application/json"
            )
    
    with col2:
        if st.button("💕 Export Love Scores (CSV)", use_container_width=True):
            if love_scores:
                love_df = pd.DataFrame(love_scores)
                csv = love_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "love_scores.csv",
                    "text/csv"
                )
    
    with col3:
        if st.button("☁️ Export Word Cloud (PNG)", use_container_width=True):
            wordcloud = generate_word_cloud(chats, stop_words)
            if wordcloud:
                img_buffer = io.BytesIO()
                wordcloud.to_image().save(img_buffer, format='PNG')
                st.download_button(
                    "Download PNG",
                    img_buffer.getvalue(),
                    "wordcloud.png",
                    "image/png"
                )

else:
    # Welcome screen
    st.markdown("""
    ## 🎯 Welcome to WhatsApp Analyzer Pro!
    
    ### 🚀 Features:
    
    1. **📈 Time-Series Charts** - Track message activity over days, weeks, and months
    2. **☁️ Word Cloud** - Visual representation of most used words
    3. **🔥 Calendar Heatmap** - GitHub-style activity visualization
    4. **📅 Date Range Filter** - Focus on specific time periods
    5. **💕 Love Score** - Measure relationship engagement
    6. **📊 Interactive Charts** - Beautiful Plotly visualizations
    7. **🎨 Modern UI** - Clean Streamlit interface
    
    ### 📝 How to use:
    
    1. Upload your WhatsApp chat export file (.txt) from the sidebar
    2. Select your preferred language for stop words
    3. Enable date filtering if you want to analyze a specific period
    4. Choose which visualizations to display
    5. Explore the interactive charts and insights!
    
    ### 📥 How to export WhatsApp chat:
    
    **Android:**
    - Open chat → Three dots → More → Export chat → Without Media
    
    **iOS:**
    - Open chat → Contact name → Export Chat → Without Media
    
    ---
    
    **Ready to analyze? Upload your chat file from the sidebar! 👈**
    """)
    
    # Sample preview images/placeholders
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📈 Time-Series\nTrack activity trends")
    with col2:
        st.info("☁️ Word Cloud\nVisualize words")
    with col3:
        st.info("🔥 Heatmaps\nFind peak times")

