"""
WhatsApp Analyzer - Main Application
A modern Streamlit application for analyzing WhatsApp chat exports
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import Counter
import re
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import local modules
from src.analyzers.chatline import Chatline
from src.analyzers.reply_analyzer import ReplyAnalyzer
from src.database.supabase_client import supabase_manager

# Page configuration
st.set_page_config(
    page_title="WhatsApp Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 600;
        color: #31333F;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("💬 WhatsApp Chat Analyzer")
st.markdown("Upload your WhatsApp chat export to discover insights! ✨")

# Sidebar
st.sidebar.header("📤 Upload Chat File")
uploaded_file = st.sidebar.file_uploader(
    "Choose a .txt file", 
    type=['txt'],
    help="Export your WhatsApp chat without media"
)

# Initialize date filter in session state
if 'date_filter_enabled' not in st.session_state:
    st.session_state.date_filter_enabled = False

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📖 How to Export Chat

**📱 Android:**
1. Open chat → ⋮ (menu)
2. More → Export chat
3. Without Media

**🍎 iOS:**
1. Open chat → Contact name
2. Export Chat
3. Without Media
""")

# Main application logic
if uploaded_file:
    # Auto-save to Supabase (silently)
    if supabase_manager.is_connected():
        file_bytes = uploaded_file.getvalue()
        supabase_manager.save_file(uploaded_file.name, file_bytes)
    
    # Parse chat file
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
    
    if len(msgs) == 0:
        st.error("❌ No messages found in the file!")
        st.stop()
    
    st.success(f"✅ Analyzed {len(msgs):,} messages successfully!")
    
    # Extract basic information
    senders = [c.sender for c in msgs if c.sender]
    sender_counts = Counter(senders)
    dates = [c.timestamp for c in msgs if hasattr(c, 'timestamp') and c.timestamp]
    
    # === DATE RANGE FILTER (SIDEBAR) ===
    if dates:
        min_date = min(dates).date()
        max_date = max(dates).date()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Date Range Filter")
        
        enable_filter = st.sidebar.checkbox("Enable date filtering", value=False)
        
        if enable_filter:
            date_range = st.sidebar.date_input(
                "Select date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Apply filter if range is selected
            if len(date_range) == 2:
                start_date, end_date = date_range
                msgs = [m for m in msgs if hasattr(m, 'timestamp') and m.timestamp and 
                       start_date <= m.timestamp.date() <= end_date]
                senders = [c.sender for c in msgs if c.sender]
                sender_counts = Counter(senders)
                dates = [c.timestamp for c in msgs if hasattr(c, 'timestamp') and c.timestamp]
                
                st.sidebar.success(f"Filtered: {len(msgs)} messages")
    
    # === METRICS SECTION ===
    st.header("📊 Quick Overview")
    st.markdown("### Key Chat Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Total Messages", f"{len(msgs):,}")
    
    with col2:
        st.metric("👥 Participants", len(sender_counts))
    
    with col3:
        if dates:
            days = (max(dates) - min(dates)).days + 1
            st.metric("📅 Duration (Days)", f"{days}")
        else:
            st.metric("📅 Duration", "N/A")
    
    with col4:
        if dates and len(dates) > 0:
            avg_per_day = len(msgs) / ((max(dates) - min(dates)).days + 1)
            st.metric("📈 Avg Messages/Day", f"{avg_per_day:.1f}")
        else:
            st.metric("📈 Avg Messages/Day", "N/A")
    
    st.markdown("---")
    
    # === TOP SENDERS SECTION ===
    st.header("👥 Top Contributors")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart
        top_senders_df = pd.DataFrame(
            sender_counts.most_common(10),
            columns=['Sender', 'Messages']
        )
        fig = px.bar(
            top_senders_df,
            x='Messages',
            y='Sender',
            orientation='h',
            title='Top 10 Message Senders',
            color='Messages',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("### 📊 Message Statistics")
        st.markdown("#### Top 5 Senders")
        for idx, (sender, count) in enumerate(sender_counts.most_common(5), 1):
            percentage = (count / len(msgs)) * 100
            st.markdown(f"""
            **#{idx} {sender}**  
            📨 {count:,} messages ({percentage:.1f}%)
            """)
            st.progress(percentage / 100)
    
    st.markdown("---")
    
    # === WORD CLOUD SECTION ===
    st.header("☁️ Word Cloud")
    
    # Extract words
    words = []
    for msg in msgs:
        if hasattr(msg, 'body') and msg.body:
            text = str(msg.body).lower()
            text = re.sub(r'[^\w\s]', '', text)
            words.extend(text.split())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                  'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                  'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
                  'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your',
                  'his', 'her', 'its', 'our', 'their', 'me', 'him', 'us', 'them'}
    
    filtered_words = [w for w in words if len(w) > 2 and w not in stop_words]
    word_counts = Counter(filtered_words)
    
    if word_counts:
        # Show word cloud in expandable section
        with st.expander("🎨 Click to View Word Cloud Visualization", expanded=False):
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            
            wordcloud = WordCloud(
                width=1200,
                height=400,
                background_color='white',
                colormap='viridis',
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(word_counts)
            
            fig, ax = plt.subplots(figsize=(15, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        
        # Top words table - always visible
        st.markdown("### 🔤 Most Frequently Used Words")
        top_words_df = pd.DataFrame(
            word_counts.most_common(20),
            columns=['Word', 'Frequency']
        )
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 1-10:**")
            st.dataframe(top_words_df.head(10), width="stretch", hide_index=True)
        with col2:
            st.markdown("**Top 11-20:**")
            st.dataframe(top_words_df.tail(10), width="stretch", hide_index=True)
    
    st.markdown("---")
    
    # === TIME SERIES ANALYSIS ===
    st.header("📅 Activity Patterns Over Time")
    
    if dates:
        # Daily activity
        date_counts = Counter([d.date() for d in dates])
        dates_df = pd.DataFrame(
            [(date, count) for date, count in sorted(date_counts.items())],
            columns=['Date', 'Messages']
        )
        
        fig = px.line(
            dates_df,
            x='Date',
            y='Messages',
            title='Daily Message Activity',
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, width="stretch")
        
        # Hourly activity
        hour_counts = Counter([d.hour for d in dates if hasattr(d, 'hour')])
        hours_df = pd.DataFrame(
            [(hour, hour_counts.get(hour, 0)) for hour in range(24)],
            columns=['Hour', 'Messages']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                hours_df,
                x='Hour',
                y='Messages',
                title='Activity by Hour of Day',
                color='Messages',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Day of week activity
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = Counter([d.weekday() for d in dates if hasattr(d, 'weekday')])
            days_df = pd.DataFrame(
                [(day_names[day], day_counts.get(day, 0)) for day in range(7)],
                columns=['Day', 'Messages']
            )
            
            fig = px.bar(
                days_df,
                x='Day',
                y='Messages',
                title='Activity by Day of Week',
                color='Messages',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    # === LOVE SCORE ANALYSIS ===
    st.header("❤️ Love Score Analysis")
    st.info("📊 **Love Score** measures engagement level based on reply speed, frequency, and consistency")
    
    try:
        analyzer = ReplyAnalyzer(msgs)
        scores = analyzer.get_love_scores()
        
        if scores and len(scores) >= 2:
            # Calculate average love score as relationship interest indicator
            avg_score = sum(s['love_score'] for s in scores) / len(scores)
            
            # Display overall relationship score
            st.subheader("💝 Overall Relationship Interest")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Determine interest level
                if avg_score >= 75:
                    verdict = "🔥 Very High Interest"
                    color = "#196127"
                elif avg_score >= 60:
                    verdict = "💚 High Interest"
                    color = "#239a3b"
                elif avg_score >= 45:
                    verdict = "💛 Moderate Interest"
                    color = "#7bc96f"
                elif avg_score >= 30:
                    verdict = "💙 Low Interest"
                    color = "#c6e48b"
                else:
                    verdict = "💔 Very Low Interest"
                    color = "#ebedf0"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background-color: {color}; border-radius: 15px; color: white;">
                    <h1 style="margin: 0; font-size: 60px;">{avg_score:.1f}%</h1>
                    <h3 style="margin: 10px 0 0 0;">{verdict}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Individual scores
            st.subheader("📊 Individual Engagement Scores")
            cols = st.columns(len(scores))
            for col, score_data in zip(cols, scores):
                with col:
                    st.metric(
                        score_data['sender'][:15],
                        f"{score_data['love_score']:.1f}%",
                        f"{score_data['message_count']} msgs"
                    )
            
            # Detailed chart
            with st.expander("📈 View Detailed Score Comparison"):
                scores_df = pd.DataFrame(scores)
                fig = px.bar(
                    scores_df,
                    x='sender',
                    y='love_score',
                    title='Individual Love Scores (%)',
                    color='love_score',
                    color_continuous_scale='RdYlGn',
                    text='love_score',
                    labels={'love_score': 'Love Score (%)', 'sender': 'Participant'}
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=400, yaxis_title="Love Score (%)")
                st.plotly_chart(fig, width="stretch")
        else:
            st.info("Not enough data for love score analysis (need at least 2 participants)")
    
    except Exception as e:
        st.warning(f"Love score analysis unavailable: {str(e)}")
    
    st.markdown("---")
    
    # === CALENDAR HEATMAP ===
    st.header("🗓️ Activity Calendar Heatmap")
    st.markdown("### GitHub-Style Contribution Calendar")
    
    if dates:
        import plotly.graph_objects as go
        import numpy as np
        
        date_counts = Counter([d.date() for d in dates])
        
        # Prepare data
        dates_list = sorted(date_counts.keys())
        if dates_list:
            min_date = min(dates_list)
            max_date = max(dates_list)
            
            # Create complete date range
            date_range = pd.date_range(min_date, max_date)
            
            # Build matrix data with proper alignment
            # Start from Monday
            start_weekday = date_range[0].weekday()
            
            # Prepare weeks data
            weeks_data = []
            week_labels = []
            current_week = [0] * start_weekday  # Pad start
            week_num = 0
            
            for d in date_range:
                count = date_counts.get(d.date(), 0)
                current_week.append(count)
                
                if d.weekday() == 6:  # Sunday
                    # Pad end if needed
                    while len(current_week) < 7:
                        current_week.append(0)
                    weeks_data.append(current_week)
                    week_labels.append(f"Week {week_num + 1}")
                    current_week = []
                    week_num += 1
            
            # Add last incomplete week
            if current_week:
                while len(current_week) < 7:
                    current_week.append(0)
                weeks_data.append(current_week)
                week_labels.append(f"Week {week_num + 1}")
            
            # Transpose for proper display
            z_data = list(map(list, zip(*weeks_data)))
            
            # Day labels
            day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Create beautiful heatmap
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=week_labels,
                y=day_labels,
                colorscale=[
                    [0, '#ebedf0'],      # Very light gray (no activity)
                    [0.2, '#c6e48b'],    # Light green
                    [0.4, '#7bc96f'],    # Medium green
                    [0.6, '#239a3b'],    # Dark green
                    [1, '#196127']       # Very dark green
                ],
                showscale=True,
                hovertemplate='<b>%{y}</b><br>Week: %{x}<br>Messages: %{z}<extra></extra>',
                colorbar=dict(
                    title=dict(text="Messages", side="right"),
                    thickness=15,
                    len=0.7
                )
            ))
            
            fig.update_layout(
                title={
                    'text': f'📅 Chat Activity from {min_date.strftime("%b %d, %Y")} to {max_date.strftime("%b %d, %Y")}',
                    'x': 0.5,
                    'xanchor': 'center'
                },
                height=350,
                xaxis={
                    'title': '',
                    'side': 'bottom',
                    'tickangle': -45
                },
                yaxis={
                    'title': '',
                    'autorange': 'reversed'
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # Add summary stats below heatmap
            col1, col2, col3 = st.columns(3)
            with col1:
                busiest_day = max(date_counts.items(), key=lambda x: x[1])
                st.metric("🔥 Most Active Day", busiest_day[0].strftime("%b %d, %Y"), f"{busiest_day[1]} messages")
            with col2:
                total_days = len(date_counts)
                st.metric("📆 Active Days", f"{total_days}", f"out of {(max_date - min_date).days + 1} days")
            with col3:
                avg_messages = sum(date_counts.values()) / len(date_counts)
                st.metric("📊 Average per Active Day", f"{avg_messages:.1f}", "messages/day")

else:
    # Welcome screen
    st.info("👈 Upload a WhatsApp chat file from the sidebar to begin analysis!")
    
    st.markdown("""
    ### 🌟 Features
    
    - 📊 **Message Statistics**: Total messages, participants, activity metrics
    - 👥 **Top Contributors**: See who sends the most messages
    - ☁️ **Word Cloud**: Visualize most common words
    - 📅 **Time Analysis**: Daily, hourly, and weekly patterns
    - ❤️ **Love Score**: Measure engagement between participants
    - 🗓️ **Calendar Heatmap**: Visualize activity over time
    
    ### 🚀 Get Started
    
    Export your WhatsApp chat and upload the `.txt` file to see the magic!
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit | WhatsApp Analyzer v2.0"
    "</div>",
    unsafe_allow_html=True
)
