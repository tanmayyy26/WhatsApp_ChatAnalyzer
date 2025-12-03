#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Feature Demo - Shows ALL advanced features including Love Score
"""

from advanced_analyzer import AdvancedAnalyzer
from reply_analyzer import ReplyAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from chatline import Chatline
import io

def demo_all_features():
    """Comprehensive demo of all features"""
    
    print("\n" + "="*80)
    print("🌟 COMPLETE FEATURE DEMO - WhatsApp Analyzer Advanced + Love Score")
    print("="*80 + "\n")
    
    file_path = 'chat_example.txt'
    
    # 1. Basic Analysis
    print("📊 1. BASIC ANALYSIS")
    print("-" * 80)
    analyzer = AdvancedAnalyzer(file_path, stop_words=[])
    analyzer.load_file()
    analyzer.parse_chats()
    analyzer.process_data()
    
    stats = analyzer.get_statistics()
    print(f"✓ Messages: {stats['overview']['total_chats']}")
    print(f"✓ Participants: {stats['overview']['unique_senders']}")
    print(f"✓ Conversations: {stats['conversations']}")
    print()
    
    # 2. Export Features
    print("📊 2. EXPORT FEATURES")
    print("-" * 80)
    json_path = analyzer.export_json()
    csv_path = analyzer.export_csv()
    html_path = analyzer.export_html()
    print(f"✓ JSON: {json_path.name}")
    print(f"✓ CSV: {csv_path.name}")
    print(f"✓ HTML: {html_path.name}")
    print()
    
    # 3. Sentiment Analysis
    print("📊 3. SENTIMENT ANALYSIS")
    print("-" * 80)
    sa = SentimentAnalyzer(language='en')
    
    test_messages = [
        "I love this so much! 😊",
        "This is terrible 😢",
        "Just a normal message"
    ]
    
    for msg in test_messages:
        result = sa.analyze_text(msg)
        print(f"'{msg[:30]}...' → {result['sentiment'].upper()} ({result['score']:.2f})")
    print()
    
    # 4. Love Score Analysis
    print("📊 4. LOVE SCORE ANALYSIS")
    print("-" * 80)
    
    # Parse messages for reply analyzer
    with io.open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    messages = []
    previous_line = None
    for line in lines:
        chatline = Chatline(line=line, previous_line=previous_line, debug=False)
        if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
            messages.append(chatline)
        previous_line = chatline
    
    reply_analyzer = ReplyAnalyzer(messages)
    
    # Find best pairs
    best_pairs = reply_analyzer.find_best_pairs(top_n=3)
    
    if best_pairs:
        print(f"Top 3 Relationship Pairs:")
        for i, (p1, p2, score) in enumerate(best_pairs, 1):
            print(f"  {i}. {p1} ← → {p2}")
            print(f"     Combined Love Score: {score:.1f}/100")
        
        # Detailed analysis of top pair
        print(f"\nDetailed Analysis of Top Pair:")
        person1, person2, _ = best_pairs[0]
        analysis = reply_analyzer.analyze_pair(person1, person2)
        
        print(f"\n  {person1}:")
        print(f"    • Love Score: {analysis['target']['love_score']}/100")
        print(f"    • Verdict: {analysis['target']['verdict']}")
        print(f"    • Median Reply: {analysis['target']['median_reply_time']:.1f} min")
        print(f"    • Fast Reply Rate: {analysis['target']['fast_reply_rate']:.1f}%")
        
        print(f"\n  {person2}:")
        print(f"    • Love Score: {analysis['counterpart']['love_score']}/100")
        print(f"    • Verdict: {analysis['counterpart']['verdict']}")
        print(f"    • Median Reply: {analysis['counterpart']['median_reply_time']:.1f} min")
        print(f"    • Fast Reply Rate: {analysis['counterpart']['fast_reply_rate']:.1f}%")
        
        print(f"\n  Winner: {analysis['comparison']['faster_replier']} (faster replier)")
    print()
    
    # 5. Advanced Metrics
    print("📊 5. ADVANCED METRICS")
    print("-" * 80)
    if stats['response_times']:
        print("Fastest Responders:")
        for sender, time in stats['response_times'][:3]:
            print(f"  • {sender}: {int(time//60)}m {int(time%60)}s")
    
    if stats['peak_hours']:
        print("\nPeak Activity Hours:")
        for hour, count in stats['peak_hours'][:3]:
            print(f"  • {hour:02d}:00 - {count} messages")
    print()
    
    # Summary
    print("="*80)
    print("✅ DEMO COMPLETE!")
    print("="*80)
    print("\nAvailable Tools:")
    print("  1. py whatsapp_analyzer.py <file>         - Original analyzer")
    print("  2. py advanced_analyzer.py <file> --export - Advanced with exports")
    print("  3. py love_analyzer.py <file> --all-pairs - Love score analysis")
    print("  4. py web_dashboard.py                    - Web interface")
    print("  5. py demo_advanced.py                    - Feature demo")
    print()
    print("Documentation:")
    print("  • README_ADVANCED.md    - Full feature guide")
    print("  • LOVE_SCORE_GUIDE.md   - Love score documentation")
    print("  • QUICKSTART.md         - Quick reference")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        demo_all_features()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
