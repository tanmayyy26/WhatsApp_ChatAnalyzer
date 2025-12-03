#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Demo Script for Advanced WhatsApp Analyzer
Demonstrates all the new features
"""

import sys
from pathlib import Path
from advanced_analyzer import AdvancedAnalyzer
from sentiment_analyzer import SentimentAnalyzer

def demo_advanced_analyzer():
    """Demo the advanced analyzer features"""
    print("\n" + "="*70)
    print("🎯 ADVANCED WHATSAPP ANALYZER - FEATURE DEMO")
    print("="*70 + "\n")
    
    # 1. Initialize analyzer
    print("📂 Step 1: Loading chat file...")
    analyzer = AdvancedAnalyzer('chat_example.txt', stop_words=[])
    
    if not analyzer.load_file():
        print("❌ Error loading file")
        return
    
    # 2. Parse and process
    print("\n📊 Step 2: Parsing and analyzing chats...")
    analyzer.parse_chats()
    analyzer.process_data()
    
    # 3. Get statistics
    print("\n📈 Step 3: Generating statistics...")
    stats = analyzer.get_statistics()
    
    # Display overview
    print("\n" + "="*70)
    print("📊 ANALYSIS OVERVIEW")
    print("="*70)
    print(f"✓ Total Messages: {stats['overview']['total_chats']}")
    print(f"✓ Participants: {stats['overview']['unique_senders']}")
    print(f"✓ Unique Words: {stats['overview']['unique_words']}")
    print(f"✓ Unique Emojis: {stats['overview']['unique_emojis']}")
    print(f"✓ Shared Links: {stats['overview']['unique_domains']}")
    print(f"✓ Conversations: {stats['conversations']}")
    print(f"✓ Deleted Messages: {stats['overview']['deleted_messages']}")
    print(f"✓ Attachments: {stats['overview']['total_attachments']}")
    
    # Top senders
    print("\n" + "="*70)
    print("👥 TOP 5 MOST ACTIVE SENDERS")
    print("="*70)
    for i, (sender, count) in enumerate(stats['senders'][:5], 1):
        print(f"{i}. {sender}: {count} messages")
    
    # Response times
    print("\n" + "="*70)
    print("⚡ FASTEST RESPONDERS (Average Response Time)")
    print("="*70)
    if stats['response_times']:
        for i, (sender, avg_time) in enumerate(stats['response_times'][:5], 1):
            minutes = int(avg_time // 60)
            seconds = int(avg_time % 60)
            print(f"{i}. {sender}: {minutes}m {seconds}s")
    else:
        print("No response time data available")
    
    # Peak hours
    print("\n" + "="*70)
    print("🔥 PEAK ACTIVITY HOURS")
    print("="*70)
    for i, (hour, count) in enumerate(stats['peak_hours'][:5], 1):
        print(f"{i}. {hour:02d}:00 - {count} messages")
    
    # Top words
    print("\n" + "="*70)
    print("💬 TOP 10 MOST USED WORDS")
    print("="*70)
    for i, (word, count) in enumerate(stats['words'][:10], 1):
        print(f"{i}. {word}: {count} times")
    
    # Top emojis
    print("\n" + "="*70)
    print("😊 TOP 10 MOST USED EMOJIS")
    print("="*70)
    for i, (emoji_char, count) in enumerate(stats['emojis'][:10], 1):
        print(f"{i}. {emoji_char}: {count} times")
    
    # 4. Export to multiple formats
    print("\n" + "="*70)
    print("💾 Step 4: Exporting results...")
    print("="*70)
    
    json_path = analyzer.export_json()
    csv_path = analyzer.export_csv()
    html_path = analyzer.export_html()
    
    print("\n✅ All exports completed!")
    print(f"\n📁 Files saved to:")
    print(f"   JSON: {json_path}")
    print(f"   CSV:  {csv_path}")
    print(f"   HTML: {html_path}")
    
    # 5. Sentiment Analysis Demo
    print("\n" + "="*70)
    print("😊 Step 5: Sentiment Analysis (Sample)")
    print("="*70)
    
    sa = SentimentAnalyzer(language='en')
    
    sample_texts = [
        "This is amazing! I love it! 😊",
        "That's terrible and disappointing 😢",
        "Just a regular message",
        "Great work everyone! 👏🎉"
    ]
    
    for text in sample_texts:
        result = sa.analyze_text(text)
        print(f"\nText: '{text}'")
        print(f"  → Sentiment: {result['sentiment'].upper()}")
        print(f"  → Score: {result['score']:.2f}")
        print(f"  → Confidence: {result['confidence']:.2f}")
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 DEMO COMPLETED!")
    print("="*70)
    print("\nNext steps:")
    print("1. Open the HTML report in your browser")
    print("2. Try the web dashboard: python web_dashboard.py")
    print("3. Explore the JSON export for raw data")
    print("4. Import CSV into Excel for custom analysis")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        demo_advanced_analyzer()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
