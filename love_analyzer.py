#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Love Score Analyzer - Relationship Interest Analysis
Upload a WhatsApp chat and discover relationship dynamics!
"""

import argparse
import io
import sys
from pathlib import Path
from advanced_analyzer import AdvancedAnalyzer
from reply_analyzer import ReplyAnalyzer
from font_color import Color
import json

def print_love_score_circle(score: int, size: int = 10):
    """Print a visual circular progress for love score"""
    filled = int((score / 100) * size)
    empty = size - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {score}%"

def print_love_analysis(analysis: dict, target_name: str, counterpart_name: str):
    """Print beautiful love score analysis"""
    target = analysis['target']
    counterpart = analysis['counterpart']
    comparison = analysis['comparison']
    
    print("\n" + "="*80)
    print(Color.custom(
        f"💕 LOVE SCORE ANALYSIS: {target_name} ← → {counterpart_name}",
        bold=True, fg_red=True
    ))
    print("="*80 + "\n")
    
    # Target Person Analysis
    print(Color.bold(f"📊 {target['name']} Analysis:"))
    print("-" * 80)
    print(f"   Love Score: {Color.custom(print_love_score_circle(target['love_score'], 20), fg_red=True, bold=True)}")
    print(f"   Verdict: {Color.custom(target['verdict'], fg_red=True, bold=True)}")
    print(f"\n   Reply Statistics:")
    print(f"      • Total Replies: {target['reply_count']}")
    print(f"      • Median Reply Time: {target['median_reply_time']:.1f} minutes")
    print(f"      • Average Reply Time: {target['mean_reply_time']:.1f} minutes")
    print(f"      • Fast Reply Rate: {target['fast_reply_rate']:.1f}% (within 5 min)")
    print(f"      • Consistency (StdDev): {target['std_dev']:.1f} minutes")
    print(f"      • Reply Trend: {'📈 Getting SLOWER' if target['trend_slope'] > 0 else '📉 Getting FASTER'} ({target['trend_slope']:.4f})")
    print(f"      • Trend Strength (R²): {target['trend_r2']:.4f}")
    
    print(f"\n   Score Breakdown:")
    for key, value in target['score_breakdown'].items():
        print(f"      • {key.replace('_', ' ').title()}: {value:.1f} points")
    
    # Counterpart Analysis
    print(f"\n{Color.bold(f'📊 {counterpart['name']} Analysis:')}")
    print("-" * 80)
    print(f"   Love Score: {Color.custom(print_love_score_circle(counterpart['love_score'], 20), fg_blue=True, bold=True)}")
    print(f"   Verdict: {Color.custom(counterpart['verdict'], fg_blue=True, bold=True)}")
    print(f"\n   Reply Statistics:")
    print(f"      • Total Replies: {counterpart['reply_count']}")
    print(f"      • Median Reply Time: {counterpart['median_reply_time']:.1f} minutes")
    print(f"      • Average Reply Time: {counterpart['mean_reply_time']:.1f} minutes")
    print(f"      • Fast Reply Rate: {counterpart['fast_reply_rate']:.1f}% (within 5 min)")
    print(f"      • Consistency (StdDev): {counterpart['std_dev']:.1f} minutes")
    print(f"      • Reply Trend: {'📈 Getting SLOWER' if counterpart['trend_slope'] > 0 else '📉 Getting FASTER'} ({counterpart['trend_slope']:.4f})")
    print(f"      • Trend Strength (R²): {counterpart['trend_r2']:.4f}")
    
    print(f"\n   Score Breakdown:")
    for key, value in counterpart['score_breakdown'].items():
        print(f"      • {key.replace('_', ' ').title()}: {value:.1f} points")
    
    # Comparison
    print(f"\n{Color.bold('⚖️  Head-to-Head Comparison:')}")
    print("-" * 80)
    print(f"   🏃 Faster Replier: {Color.green(comparison['faster_replier'])}")
    print(f"   📏 More Consistent: {Color.green(comparison['more_consistent'])}")
    print(f"   📈 Improving Faster: {Color.green(comparison['improving_faster'])}")
    print(f"   ⏱️  Median Time Difference: {comparison['median_diff']:.1f} minutes")
    
    # Overall interpretation
    print(f"\n{Color.bold('💡 Interpretation:')}")
    print("-" * 80)
    
    score_diff = target['love_score'] - counterpart['love_score']
    if abs(score_diff) < 10:
        print(f"   🤝 Balanced relationship! Both show similar interest levels.")
    elif score_diff > 0:
        print(f"   💖 {target['name']} shows stronger interest in the conversation!")
        print(f"      ({abs(score_diff)} points higher)")
    else:
        print(f"   💖 {counterpart['name']} shows stronger interest in the conversation!")
        print(f"      ({abs(score_diff)} points higher)")
    
    if target['median_reply_time'] < 10 and counterpart['median_reply_time'] < 10:
        print(f"   ⚡ Very responsive conversation - both reply quickly!")
    elif target['median_reply_time'] > 60 or counterpart['median_reply_time'] > 60:
        print(f"   🐌 Slower-paced conversation - messages have longer gaps")
    
    print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='WhatsApp Love Score Analyzer - Measure relationship interest!',
        usage="python love_analyzer.py FILE [-h] [-t TARGET] [-c COUNTERPART] [--all-pairs]"
    )
    
    parser.add_argument('file', metavar='FILE', help='Chat file path')
    parser.add_argument('-t', '--target', help='Target person name')
    parser.add_argument('-c', '--counterpart', help='Counterpart person name')
    parser.add_argument('--all-pairs', action='store_true', help='Analyze all participant pairs')
    parser.add_argument('--top', type=int, default=5, help='Number of top pairs to show (default: 5)')
    parser.add_argument('-e', '--export', help='Export results to JSON file')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(Color.custom("💕 WhatsApp Love Score Analyzer 💕", bold=True, fg_red=True))
    print("="*80 + "\n")
    print("Analyzing reply patterns to measure relationship interest...")
    print("(Inspired by behavioral psychology and communication patterns)\n")
    
    # Load chat
    print(f"📂 Loading chat file: {args.file}")
    try:
        with io.open(args.file, "r", encoding="utf-8") as file:
            lines = file.readlines()
        print(f"✓ Loaded {len(lines)} lines\n")
    except IOError:
        print(f"❌ Error: File '{args.file}' not found")
        sys.exit(1)
    
    # Parse with basic analyzer
    print("🔄 Parsing messages...")
    analyzer = AdvancedAnalyzer(args.file, stop_words=[])
    if not analyzer.load_file():
        print("❌ Failed to load file")
        sys.exit(1)
    
    analyzer.parse_chats()
    print(f"✓ Parsed {analyzer.chat_data['chat_count']} messages\n")
    
    # Get participants
    participants = list(set([m.sender for m in [
        line for line in [analyzer.lines] 
        for m in [line]
        if hasattr(m, 'sender')
    ]]))
    
    # Get unique senders from chat_data
    from collections import Counter
    sender_counts = Counter(analyzer.chat_data['senders'])
    participants = [sender for sender, _ in sender_counts.most_common()]
    
    if len(participants) < 2:
        print("❌ Need at least 2 participants for love score analysis")
        print(f"   Found: {', '.join(participants) if participants else 'No participants'}")
        sys.exit(1)
    
    print(f"👥 Found {len(participants)} participants:")
    for i, p in enumerate(participants[:10], 1):
        count = sender_counts[p]
        print(f"   {i}. {p} ({count} messages)")
    if len(participants) > 10:
        print(f"   ... and {len(participants) - 10} more")
    print()
    
    # Initialize reply analyzer
    # Need to convert to proper message format
    from chatline import Chatline
    messages = []
    previous_line = None
    for line in lines:
        chatline = Chatline(line=line, previous_line=previous_line, debug=False)
        if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
            messages.append(chatline)
        previous_line = chatline
    
    reply_analyzer = ReplyAnalyzer(messages)
    
    # All pairs analysis
    if args.all_pairs:
        print(Color.bold(f"🔍 Analyzing all participant pairs..."))
        print("="*80 + "\n")
        
        best_pairs = reply_analyzer.find_best_pairs(top_n=args.top)
        
        if not best_pairs:
            print("❌ Insufficient data for pair analysis")
            sys.exit(1)
        
        print(Color.bold(f"🏆 Top {len(best_pairs)} Pairs by Combined Love Score:"))
        print("="*80 + "\n")
        
        for i, (person1, person2, score) in enumerate(best_pairs, 1):
            print(f"{i}. {person1} ← → {person2}")
            print(f"   Combined Score: {Color.custom(f'{score:.1f}/100', fg_red=True, bold=True)}")
            print()
        
        print("\nAnalyzing top pair in detail...\n")
        target, counterpart = best_pairs[0][0], best_pairs[0][1]
    
    # Specific pair analysis
    else:
        if args.target and args.counterpart:
            target = args.target
            counterpart = args.counterpart
        else:
            # Use two most active participants
            if len(participants) < 2:
                print("❌ Need at least 2 participants")
                sys.exit(1)
            target = participants[0]
            counterpart = participants[1]
            print(f"ℹ️  No participants specified, using top 2 most active:")
            print(f"   Target: {target}")
            print(f"   Counterpart: {counterpart}\n")
    
    # Analyze the pair
    try:
        analysis = reply_analyzer.analyze_pair(target, counterpart)
    except Exception as e:
        print(f"❌ Error analyzing pair: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print results
    print_love_analysis(analysis, target, counterpart)
    
    # Export if requested
    if args.export:
        export_path = Path(args.export)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✓ Results exported to: {export_path}\n")
    
    print(Color.custom("💡 Pro Tip:", bold=True, fg_green=True))
    print("   Use --all-pairs to find the strongest relationships in group chats!")
    print("   Use -t and -c to analyze specific pairs\n")


if __name__ == "__main__":
    main()
