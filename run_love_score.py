#!/usr/bin/env python3
"""
Interactive WhatsApp Love Score Analyzer
Simply run this script and provide your WhatsApp chat file!
"""

import os
import sys
from pathlib import Path

# Import our analyzer modules
from reply_analyzer import ReplyAnalyzer
from advanced_analyzer import AdvancedAnalyzer
from font_color import Color

# Color constants for easy use
class FontColor:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    RESET = ""

def print_header():
    """Print welcome header"""
    print("\n" + "="*80)
    print("💕 WhatsApp Love Score Analyzer 💕")
    print("="*80)
    print("\nWelcome! This tool analyzes reply patterns to measure relationship interest.")
    print("Based on behavioral psychology and communication patterns.\n")

def get_chat_file():
    """Prompt user for chat file path"""
    print("📂 Please provide your WhatsApp chat export file:")
    print("   (You can drag & drop the file here or type the path)\n")
    
    while True:
        file_path = input("Chat file path: ").strip().strip('"').strip("'")
        
        if not file_path:
            print(f"{FontColor.RED}❌ Please enter a file path{FontColor.RESET}")
            continue
            
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"{FontColor.RED}❌ File not found: {file_path}{FontColor.RESET}")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                sys.exit(0)
            continue
            
        return file_path

def run_analysis(chat_file):
    """Run the Love Score analysis"""
    print(f"\n📂 Loading chat file: {os.path.basename(chat_file)}")
    
    # Parse the chat
    analyzer = AdvancedAnalyzer(chat_file)
    chats = analyzer.parse_chats()
    stats = analyzer.get_statistics()
    
    print(f"✓ Parsed {stats['total_messages']} messages")
    print(f"✓ Found {stats['total_senders']} participants\n")
    
    if stats['total_senders'] < 2:
        print(f"{FontColor.YELLOW}⚠️  Need at least 2 participants for Love Score analysis{FontColor.RESET}")
        return
    
    # Show participants
    print("👥 Participants in this chat:")
    for i, (sender, count) in enumerate(stats['senders'].items(), 1):
        print(f"   {i}. {sender} ({count} messages)")
    
    # Ask analysis type
    print("\n" + "="*80)
    print("Choose analysis type:")
    print("  1. Analyze all pairs (recommended for group chats)")
    print("  2. Analyze specific pair")
    print("="*80)
    
    choice = input("\nYour choice (1 or 2): ").strip()
    
    if choice == "1":
        # Analyze all pairs
        print("\n🔍 Analyzing all participant pairs...\n")
        reply_analyzer = ReplyAnalyzer(chats)
        
        # Get all pairs with scores
        all_pairs = []
        senders = list(stats['senders'].keys())
        
        for i in range(len(senders)):
            for j in range(i + 1, len(senders)):
                sender1, sender2 = senders[i], senders[j]
                
                score1 = reply_analyzer.calculate_love_score(sender1, sender2)
                score2 = reply_analyzer.calculate_love_score(sender2, sender1)
                
                if score1 is not None or score2 is not None:
                    combined = ((score1 or 0) + (score2 or 0)) / 2
                    all_pairs.append((sender1, sender2, score1, score2, combined))
        
        if not all_pairs:
            print(f"{FontColor.YELLOW}⚠️  No reply patterns found between participants{FontColor.RESET}")
            return
        
        # Sort by combined score
        all_pairs.sort(key=lambda x: x[4], reverse=True)
        
        # Show top pairs
        print("="*80)
        print(f"🏆 Top {min(5, len(all_pairs))} Pairs by Combined Love Score:")
        print("="*80 + "\n")
        
        for i, (s1, s2, score1, score2, combined) in enumerate(all_pairs[:5], 1):
            print(f"{i}. {s1} ← → {s2}")
            print(f"   Combined Score: {combined:.1f}/100\n")
        
        # Detailed analysis of top pair
        if all_pairs:
            print("\nAnalyzing top pair in detail...\n")
            s1, s2, _, _, _ = all_pairs[0]
            print_detailed_analysis(reply_analyzer, s1, s2)
            
    elif choice == "2":
        # Specific pair analysis
        print("\n" + "="*80)
        senders_list = list(stats['senders'].keys())
        
        print("Select first person (number):")
        for i, sender in enumerate(senders_list, 1):
            print(f"  {i}. {sender}")
        
        try:
            idx1 = int(input("\nFirst person: ").strip()) - 1
            if idx1 < 0 or idx1 >= len(senders_list):
                print(f"{FontColor.RED}Invalid selection{FontColor.RESET}")
                return
                
            print("\nSelect second person (number):")
            for i, sender in enumerate(senders_list, 1):
                if i - 1 != idx1:
                    print(f"  {i}. {sender}")
            
            idx2 = int(input("\nSecond person: ").strip()) - 1
            if idx2 < 0 or idx2 >= len(senders_list) or idx2 == idx1:
                print(f"{FontColor.RED}Invalid selection{FontColor.RESET}")
                return
            
            sender1 = senders_list[idx1]
            sender2 = senders_list[idx2]
            
            print(f"\n🔍 Analyzing relationship between:")
            print(f"   {sender1} ← → {sender2}\n")
            
            reply_analyzer = ReplyAnalyzer(chats)
            print_detailed_analysis(reply_analyzer, sender1, sender2)
            
        except (ValueError, IndexError):
            print(f"{FontColor.RED}Invalid input{FontColor.RESET}")
            return
    else:
        print(f"{FontColor.RED}Invalid choice{FontColor.RESET}")
        return

def print_detailed_analysis(reply_analyzer, sender1, sender2):
    """Print detailed Love Score analysis for a pair"""
    print("="*80)
    print(f"💕 LOVE SCORE ANALYSIS: {sender1} ← → {sender2}")
    print("="*80 + "\n")
    
    for person, target in [(sender1, sender2), (sender2, sender1)]:
        score = reply_analyzer.calculate_love_score(person, target)
        stats = reply_analyzer.get_reply_stats(person, target)
        
        if score is None:
            print(f"📊 {person} → {target}:")
            print(f"   {FontColor.YELLOW}No replies found{FontColor.RESET}\n")
            continue
        
        # Determine verdict
        if score >= 80:
            verdict = "Strong interest 💕"
            color = FontColor.GREEN
        elif score >= 60:
            verdict = "Moderate interest 💗"
            color = FontColor.YELLOW
        elif score >= 40:
            verdict = "Some interest 💛"
            color = FontColor.YELLOW
        else:
            verdict = "Low interest 💙"
            color = FontColor.BLUE
        
        # Progress bar
        filled = int(score / 5)
        bar = "█" * filled + "░" * (20 - filled)
        
        print(f"📊 {person} Analysis:")
        print("-" * 80)
        print(f"   Love Score: [{bar}] {int(score)}%")
        print(f"   Verdict: {color}{verdict}{FontColor.RESET}\n")
        
        if stats:
            print(f"   Reply Statistics:")
            print(f"      • Total Replies: {stats['count']}")
            print(f"      • Median Reply Time: {stats['median_minutes']:.1f} minutes")
            print(f"      • Average Reply Time: {stats['mean_minutes']:.1f} minutes")
            print(f"      • Fast Reply Rate: {stats['fast_rate']*100:.1f}% (within 5 min)")
            print(f"      • Consistency (StdDev): {stats['std_minutes']:.1f} minutes")
            
            trend_emoji = "📉" if stats['slope'] < 0 else "📈"
            trend_text = "Getting FASTER" if stats['slope'] < 0 else "Getting SLOWER"
            print(f"      • Reply Trend: {trend_emoji} {trend_text} ({stats['slope']:.4f})")
            print(f"      • Trend Strength (R²): {stats['r_squared']:.4f}")
        
        print()
    
    # Head-to-head comparison
    score1 = reply_analyzer.calculate_love_score(sender1, sender2)
    score2 = reply_analyzer.calculate_love_score(sender2, sender1)
    stats1 = reply_analyzer.get_reply_stats(sender1, sender2)
    stats2 = reply_analyzer.get_reply_stats(sender2, sender1)
    
    if score1 and score2 and stats1 and stats2:
        print("⚖️  Head-to-Head Comparison:")
        print("-" * 80)
        
        faster = sender1 if stats1['median_minutes'] < stats2['median_minutes'] else sender2
        more_consistent = sender1 if stats1['std_minutes'] < stats2['std_minutes'] else sender2
        improving_faster = sender1 if stats1['slope'] < stats2['slope'] else sender2
        time_diff = abs(stats1['median_minutes'] - stats2['median_minutes'])
        
        print(f"   🏃 Faster Replier: {faster}")
        print(f"   📏 More Consistent: {more_consistent}")
        print(f"   📈 Improving Faster: {improving_faster}")
        print(f"   ⏱️  Median Time Difference: {time_diff:.1f} minutes\n")
        
        print("💡 Interpretation:")
        print("-" * 80)
        if abs(score1 - score2) < 10:
            print(f"   💚 Both show similar interest levels! (difference: {abs(score1 - score2):.0f} points)")
        else:
            stronger = sender1 if score1 > score2 else sender2
            diff = abs(score1 - score2)
            print(f"   💖 {stronger} shows stronger interest in the conversation!")
            print(f"      ({diff:.0f} points higher)")
    
    print("\n" + "="*80)

def main():
    """Main entry point"""
    try:
        print_header()
        chat_file = get_chat_file()
        run_analysis(chat_file)
        
        print("\n\n💡 Pro Tips:")
        print("   • Export your WhatsApp chat: Open chat → ⋮ → More → Export chat → Without media")
        print("   • For best results, analyze chats with at least 20-30 messages")
        print("   • The algorithm looks for reply patterns (who responds to whom)")
        print("   • Lower reply times = higher interest score!\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{FontColor.YELLOW}Analysis cancelled by user{FontColor.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{FontColor.RED}❌ Error: {str(e)}{FontColor.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
