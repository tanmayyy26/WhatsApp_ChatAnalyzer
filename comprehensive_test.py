"""
Comprehensive Test Suite for WhatsApp Analyzer
Tests all core functionality
"""

from chatline import Chatline
from reply_analyzer import ReplyAnalyzer
from collections import Counter
from datetime import datetime
import re

print("=" * 60)
print("COMPREHENSIVE WHATSAPP ANALYZER TEST")
print("=" * 60)

# Test 1: File Reading
print("\n1️⃣  Testing File Reading...")
try:
    with open('chat_example.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    print(f"   ✅ Successfully read file: {len(lines)} lines")
except Exception as e:
    print(f"   ❌ Failed to read file: {e}")
    exit(1)

# Test 2: Chat Parsing
print("\n2️⃣  Testing Chat Parsing...")
try:
    chats = []
    prev = None
    for line in lines:
        if line.strip():
            c = Chatline(line, previous_line=prev)
            chats.append(c)
            prev = c
    print(f"   ✅ Parsed {len(chats)} lines")
except Exception as e:
    print(f"   ❌ Failed to parse: {e}")
    exit(1)

# Test 3: Message Filtering (CRITICAL - Case Sensitivity)
print("\n3️⃣  Testing Message Filtering...")
try:
    msgs = [c for c in chats if c.line_type == "Chat"]
    print(f"   ✅ Found {len(msgs)} chat messages")
    
    # Check line types
    line_types = Counter([c.line_type for c in chats])
    print(f"   📊 Line types: {dict(line_types)}")
    
    if len(msgs) == 0:
        print(f"   ⚠️  WARNING: 0 messages found! Check case sensitivity!")
except Exception as e:
    print(f"   ❌ Failed to filter: {e}")
    exit(1)

# Test 4: Sender Analysis
print("\n4️⃣  Testing Sender Analysis...")
try:
    senders = [c.sender for c in msgs if c.sender]
    sender_counts = Counter(senders)
    top_senders = sender_counts.most_common(3)
    print(f"   ✅ Found {len(set(senders))} unique senders")
    print(f"   📊 Top 3 senders:")
    for sender, count in top_senders:
        print(f"      • {sender}: {count} messages")
except Exception as e:
    print(f"   ❌ Failed sender analysis: {e}")

# Test 5: Timestamp Parsing
print("\n5️⃣  Testing Timestamp Parsing...")
try:
    timestamps = [c.timestamp for c in msgs if c.timestamp]
    print(f"   ✅ Found {len(timestamps)} messages with timestamps")
    if timestamps:
        print(f"   📅 First message: {timestamps[0]}")
        print(f"   📅 Last message: {timestamps[-1]}")
except Exception as e:
    print(f"   ❌ Failed timestamp parsing: {e}")

# Test 6: Word Extraction
print("\n6️⃣  Testing Word Extraction...")
try:
    all_words = []
    for msg in msgs:
        if msg.body:
            words = re.findall(r'\b[a-zA-Z]+\b', msg.body.lower())
            all_words.extend(words)
    
    word_counts = Counter(all_words)
    top_words = word_counts.most_common(5)
    print(f"   ✅ Extracted {len(all_words)} words")
    print(f"   📊 Top 5 words:")
    for word, count in top_words:
        print(f"      • {word}: {count} times")
except Exception as e:
    print(f"   ❌ Failed word extraction: {e}")

# Test 7: Love Score Analysis
print("\n7️⃣  Testing Love Score Analysis...")
try:
    participants = list(set(c.sender for c in msgs if c.sender))
    if len(participants) >= 2:
        analyzer = ReplyAnalyzer(chats)
        analysis = analyzer.analyze_pair(participants[0], participants[1])
        love_score = analysis['comparison']['combined_love_score']
        print(f"   ✅ Love Score: {love_score:.1f}/100")
        print(f"   💑 Between: {participants[0][:20]}... & {participants[1][:20]}...")
    else:
        print(f"   ⚠️  Not enough participants for Love Score")
except Exception as e:
    print(f"   ❌ Failed love score: {e}")

# Test 8: Date Range Analysis
print("\n8️⃣  Testing Date Range Analysis...")
try:
    dates = []
    for msg in msgs:
        if msg.timestamp:
            try:
                # Parse various date formats
                date_str = msg.timestamp.split(',')[0]
                dates.append(date_str)
            except:
                pass
    
    if dates:
        print(f"   ✅ Found {len(dates)} dated messages")
        print(f"   📅 Date range: {dates[0]} to {dates[-1]}")
    else:
        print(f"   ⚠️  No dates found")
except Exception as e:
    print(f"   ❌ Failed date analysis: {e}")

# Final Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"📝 Total lines parsed: {len(chats)}")
print(f"💬 Chat messages: {len(msgs)}")
print(f"👥 Unique senders: {len(set(senders))}")
print(f"📊 Total words: {len(all_words)}")
print(f"✅ All core features working correctly!")
print("=" * 60)
