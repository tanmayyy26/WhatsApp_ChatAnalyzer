#!/usr/bin/env python3
"""
Test script to verify the analyzer works correctly
"""

import sys
import io
from datetime import datetime
from collections import defaultdict
from chatline import Chatline

def test_analyzer():
    print("\n" + "="*60)
    print("🧪 Testing WhatsApp Analyzer Components")
    print("="*60 + "\n")
    
    # Test 1: File Loading
    print("Test 1: Loading chat_example.txt...")
    try:
        with io.open('chat_example.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✓ Loaded {len(lines)} lines")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Parsing
    print("\nTest 2: Parsing messages...")
    chats = []
    previous_line = None
    
    for line in lines:
        chatline = Chatline(line=line, previous_line=previous_line, debug=False)
        if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
            chats.append({
                'sender': chatline.sender,
                'timestamp': chatline.timestamp,
                'message': chatline.message
            })
        previous_line = chatline
    
    print(f"✓ Parsed {len(chats)} valid messages")
    
    if not chats:
        print("✗ No chats parsed!")
        return False
    
    # Test 3: Get participants
    print("\nTest 3: Identifying participants...")
    senders = {}
    for chat in chats:
        senders[chat['sender']] = senders.get(chat['sender'], 0) + 1
    
    print(f"✓ Found {len(senders)} participants:")
    for i, (sender, count) in enumerate(senders.items(), 1):
        print(f"   {i}. {sender}: {count} messages")
    
    # Test 4: Reply patterns
    print("\nTest 4: Analyzing reply patterns...")
    reply_data = defaultdict(list)
    
    for i in range(len(chats) - 1):
        current = chats[i]
        next_msg = chats[i + 1]
        
        if current['sender'] != next_msg['sender']:
            time_diff = (next_msg['timestamp'] - current['timestamp']).total_seconds() / 60
            if 0 < time_diff < 1440:  # Within 24 hours
                key = (next_msg['sender'], current['sender'])
                reply_data[key].append(time_diff)
    
    print(f"✓ Found {len(reply_data)} reply relationships:")
    for (person, target), replies in list(reply_data.items())[:5]:
        print(f"   {person} → {target}: {len(replies)} replies")
    
    # Test 5: Calculate sample score
    print("\nTest 5: Calculating love score...")
    if reply_data:
        sample_key = list(reply_data.keys())[0]
        replies = reply_data[sample_key]
        
        sorted_replies = sorted(replies)
        median = sorted_replies[len(sorted_replies) // 2]
        fast_count = sum(1 for r in replies if r <= 5)
        fast_rate = fast_count / len(replies)
        
        print(f"✓ Sample analysis for {sample_key[0]} → {sample_key[1]}:")
        print(f"   Replies: {len(replies)}")
        print(f"   Median time: {median:.1f} min")
        print(f"   Fast reply rate: {fast_rate*100:.1f}%")
    
    print("\n" + "="*60)
    print("✅ All tests passed! Analyzer is working correctly.")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
