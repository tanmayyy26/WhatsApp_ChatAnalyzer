"""
🚀 WhatsApp Analyzer - Streamlit Dashboard (FIXED VERSION)
Modern UI with all 5 advanced features + Better Error Handling
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
import traceback

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
    .stAlert {
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("💬 WhatsApp Analyzer Pro")
st.markdown("### 🚀 Advanced Chat Analysis - Fixed Version")

# Sidebar
with st.sidebar:
    st.header("📤 Upload Chat")
    uploaded_file = st.file_uploader("Choose WhatsApp chat export (.txt)", type=['txt'])
    
    st.markdown("---")
    st.header("⚙️ Settings")
    
    stop_words_lang = st.selectbox(
        "Stop Words Language",
        ["None", "english", "spanish", "french", "german", "indonesian", "hindi", "arabic"]
    )
    
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
    """Load stop words"""
    if language == "None":
        return []
    try:
        with open(f'stop-words/{language}.txt', 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception as e:
        st.warning(f"Could not load stop words: {e}")
        return []

def parse_chat_file(file_content, start_date=None, end_date=None):
    """Parse WhatsApp chat file with error handling"""
    chats = []
    try:
        lines = file_content.decode('utf-8').split('\n')
        
        for line in lines:
            if line.strip():
                try:
                    chatline = Chatline(line)
                    
                    # Date filtering
                    if start_date and end_date and chatline.timestamp:
                        try:
                            # Try multiple date formats
                            for fmt in ['%d/%m/%y', '%m/%d/%y', '%Y-%m-%d']:
                                try:
                                    date_str = chatline.timestamp.split(',')[0].strip()
                                    if '[' in date_str:
                                        date_str = date_str.replace('[', '').split()[0]
                                    msg_date = datetime.strptime(date_str, fmt).date()
                                    if not (start_date <= msg_date <= end_date):
                                        continue
                                    break
                                except:
                                    continue
                        except:
                            pass
                    
                    chats.append(chatline)
                except Exception as e:
                    # Skip lines that can't be parsed
                    continue
        
        return chats
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return []

def get_basic_stats(chats, stop_words):
    """Calculate basic statistics with error handling"""
    try:
        total_messages = sum(1 for c in chats if c.line_type == "Chat")
        participants = list(set(c.sender for c in chats if c.sender))
        
        # Words
        all_words = []
        for chat in chats:
            if chat.line_type == "Chat" and hasattr(chat, 'body') and chat.body:
                words = re.findall(r'\b[a-zA-Z]+\b', chat.body.lower())
                all_words.extend([w for w in words if w not in stop_words and len(w) > 2])
        
        word_freq = Counter(all_words)
        
        # Emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        all_emojis = []
        for chat in chats:
            if chat.line_type == "Chat" and hasattr(chat, 'body') and chat.body:
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
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        st.code(traceback.format_exc())
        return None

def create_time_series_data(chats):
    """Create time-series data"""
    try:
        dates = []
        for chat in chats:
            if chat.line_type == "Chat" and chat.timestamp:
                try:
                    for fmt in ['%d/%m/%y, %H:%M', '%m/%d/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                        try:
                            dt = datetime.strptime(chat.timestamp.strip(), fmt)
                            dates.append(dt.date())
                            break
                        except:
                            continue
                except:
                    pass
        
        if not dates:
            return None
        
        date_counts = Counter(dates)
        df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Messages'])
        df = df.sort_values('Date')
        
        return df
    except Exception as e:
        st.error(f"Error creating time series: {e}")
        return None

def create_hourly_data(chats):
    """Create hourly activity data"""
    try:
        hours = []
        for chat in chats:
            if chat.line_type == "Chat" and chat.timestamp:
                try:
                    for fmt in ['%d/%m/%y, %H:%M', '%m/%d/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                        try:
                            dt = datetime.strptime(chat.timestamp.strip(), fmt)
                            hours.append(dt.hour)
                            break
                        except:
                            continue
                except:
                    pass
        
        if not hours:
            return None
            
        hour_counts = Counter(hours)
        return hour_counts
    except Exception as e:
        st.error(f"Error creating hourly data: {e}")
        return None

def create_calendar_heatmap_data(chats):
    """Create calendar heatmap data"""
    try:
        dates = []
        for chat in chats:
            if chat.line_type == "Chat" and chat.timestamp:
                try:
                    for fmt in ['%d/%m/%y, %H:%M', '%m/%d/%y, %H:%M', '%d/%m/%Y, %H:%M', '[%d/%m/%y %H.%M.%S]']:
                        try:
                            dt = datetime.strptime(chat.timestamp.strip(), fmt)
                            dates.append(dt.date())
                            break
                        except:
                            continue
                except:
                    pass
        
        if not dates:
            return None
        
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
        df['Year'] = df['Date'].dt.year
        
        return df
    except Exception as e:
        st.error(f"Error creating calendar heatmap: {e}")
        return None

def generate_word_cloud(chats, stop_words):
    """Generate word cloud"""
    try:
        text = []
        for chat in chats:
            if chat.line_type == "Chat" and hasattr(chat, 'body') and chat.body:
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
    except Exception as e:
        st.error(f"Error generating word cloud: {e}")
        return None

def calculate_love_scores(chats):
    """Calculate love scores"""
    try:
        participants = list(set(c.sender for c in chats if c.sender and c.line_type == "Chat"))
        
        if len(participants) < 2:
            return None
        
        analyzer = ReplyAnalyzer()
        scores = []
        
        for i, person1 in enumerate(participants):
            for person2 in participants[i+1:]:
                try:
                    result = analyzer.calculate_love_score(chats, person1, person2)
                    scores.append({
                        'Person 1': person1,
                        'Person 2': person2,
                        'Combined Score': result['combined_score'],
                        'P1→P2': result['person1_to_person2']['score'],
                        'P2→P1': result['person2_to_person1']['score'],
                        'Verdict': result['combined_verdict']
                    })
                except Exception as e:
                    st.warning(f"Could not calculate score for {person1} & {person2}: {e}")
                    continue
        
        return sorted(scores, key=lambda x: x['Combined Score'], reverse=True) if scores else None
    except Exception as e:
        st.error(f"Error calculating love scores: {e}")
        st.code(traceback.format_exc())
        return None

# Main app
if uploaded_file is not None:
    try:
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
            st.error("❌ No messages found! Please check your file format.")
            st.info("Expected format: `14/10/18, 11:16 - Contact Name: message`")
            st.stop()
        
        chat_messages = [c for c in chats if c.line_type == "Chat"]
        st.success(f"✅ Loaded {len(chat_messages)} messages from {len(set(c.sender for c in chat_messages if c.sender))} participants!")
        
        # Calculate statistics
        with st.spinner('🔍 Analyzing chat...'):
            stats = get_basic_stats(chats, stop_words)
        
        if not stats:
            st.error("❌ Could not analyze chat data")
            st.stop()
        
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
            
            # Top senders and words
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👑 Top Senders")
                if stats['sender_counts']:
                    sender_df = pd.DataFrame(
                        stats['sender_counts'].most_common(10),
                        columns=['Sender', 'Messages']
                    )
                    fig = px.bar(sender_df, x='Sender', y='Messages', color='Messages',
                                color_continuous_scale='Blues')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 📝 Top Words")
                if stats['word_freq']:
                    word_df = pd.DataFrame(
                        stats['word_freq'].most_common(10),
                        columns=['Word', 'Count']
                    )
                    fig = px.bar(word_df, x='Word', y='Count', color='Count',
                                color_continuous_scale='Greens')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
        
        # Time-Series Charts
        if show_time_series:
            st.markdown("---")
            st.markdown("## 📈 Time-Series Analysis")
            
            ts_data = create_time_series_data(chats)
            
            if ts_data is not None and len(ts_data) > 0:
                # Daily activity
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
                
                st.plotly_chart(fig, width='stretch')
                
                # Hourly pattern
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
                    st.plotly_chart(fig3, width='stretch')
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
            st.markdown("## 🔥 Calendar Heatmap")
            
            cal_data = create_calendar_heatmap_data(chats)
            
            if cal_data is not None and len(cal_data) > 0:
                # Week/Day heatmap
                pivot = cal_data.pivot_table(
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
                    hoverongaps=False,
                    hovertemplate='Week: %{x}<br>Day: %{y}<br>Messages: %{z}<extra></extra>'
                ))
                
                fig.update_layout(
                    title='Message Activity Heatmap',
                    xaxis_title='Week Number',
                    yaxis_title='Day of Week',
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("⚠️ Could not create calendar heatmap")
        
        # Love Score Analysis
        if show_love_score:
            st.markdown("---")
            st.markdown("## 💕 Love Score Analysis")
            
            with st.spinner('Calculating love scores...'):
                love_scores = calculate_love_scores(chats)
            
            if love_scores:
                # Top pair
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
                
                love_df = pd.DataFrame(love_scores)
                
                fig = px.bar(
                    love_df.head(10),
                    x=love_df.head(10).apply(lambda row: f"{row['Person 1']} & {row['Person 2']}", axis=1),
                    y='Combined Score',
                    color='Combined Score',
                    color_continuous_scale='RdYlGn',
                    title='Top 10 Relationships'
                )
                fig.update_layout(height=400, xaxis_title='Pair', yaxis_title='Love Score')
                st.plotly_chart(fig, width='stretch')
                
                st.dataframe(love_df, width='stretch')
            else:
                st.warning("⚠️ Need at least 2 participants for love score analysis")
        
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        st.code(traceback.format_exc())

else:
    # Welcome screen
    st.markdown("""
    ## 🎯 Welcome to WhatsApp Analyzer Pro!
    
    ### 🚀 Features:
    
    1. **📈 Time-Series Charts** - Activity over time
    2. **☁️ Word Cloud** - Visual word frequency
    3. **🔥 Calendar Heatmap** - GitHub-style visualization
    4. **📅 Date Range Filter** - Analyze specific periods
    5. **💕 Love Score** - Relationship engagement metrics
    
    ### 📝 How to use:
    
    1. Upload your WhatsApp chat file (.txt) from the sidebar
    2. Select language for stop words
    3. Enable date filtering if needed
    4. Choose visualizations to display
    5. Explore the interactive charts!
    
    ### 📥 Export WhatsApp chat:
    
    **Android:** Open chat → ⋮ → More → Export chat → Without Media
    
    **iOS:** Open chat → Contact name → Export Chat → Without Media
    
    ---
    
    **Upload your chat file from the sidebar to begin! 👈**
    """)

