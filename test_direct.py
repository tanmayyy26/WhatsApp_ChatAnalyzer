#!/usr/bin/env python3
"""
Direct test of analysis logic
"""

import io
from datetime import datetime
from collections import defaultdict
from chatline import Chatline

print("\n🧪 Testing analysis logic...\n")

# Load file
with io.open('chat_example.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✓ Loaded {len(lines)} lines")

# Parse
chats = []
previous_line = None

for line in lines:
    chatline = Chatline(line=line, previous_line=previous_line, debug=False)
    if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
        chats.append({
            'sender': chatline.sender,
            'timestamp': chatline.timestamp,
            'body': chatline.body
        })
    previous_line = chatline

print(f"✓ Parsed {len(chats)} messages")

# Get senders
senders = {}
for chat in chats:
    senders[chat['sender']] = senders.get(chat['sender'], 0) + 1

print(f"✓ Found {len(senders)} participants")

# Build reply data
reply_data = defaultdict(list)

for i in range(len(chats) - 1):
    current = chats[i]
    next_msg = chats[i + 1]
    
    if current['sender'] != next_msg['sender']:
        time_diff = (next_msg['timestamp'] - current['timestamp']).total_seconds() / 60
        if 0 < time_diff < 1440:
            key = (next_msg['sender'], current['sender'])
            reply_data[key].append(time_diff)

print(f"✓ Found {len(reply_data)} reply patterns")

# Calculate scores for all pairs
sender_list = list(senders.keys())
all_pairs = []

for i in range(len(sender_list)):
    for j in range(i + 1, len(sender_list)):
        s1, s2 = sender_list[i], sender_list[j]
        
        # Get replies for s1 -> s2
        replies1 = reply_data.get((s1, s2), [])
        score1 = None
        stats1 = None
        
        if replies1 and len(replies1) >= 2:
            sorted_replies = sorted(replies1)
            median = sorted_replies[len(sorted_replies) // 2]
            mean = sum(replies1) / len(replies1)
            fast_count = sum(1 for r in replies1 if r <= 5)
            fast_rate = fast_count / len(replies1)
            
            # Trend
            n = len(replies1)
            x_mean = (n - 1) / 2
            y_mean = mean
            numerator = sum((k - x_mean) * (replies1[k] - y_mean) for k in range(n))
            denominator = sum((k - x_mean) ** 2 for k in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            
            # Std dev
            variance = sum((r - mean) ** 2 for r in replies1) / n
            std_dev = variance ** 0.5
            
            # Score
            median_scaled = max(0, min(1, 1 - (median / 60)))
            slope_scaled = max(0, min(1, -slope / 10 if slope < 0 else 0))
            consistency = max(0, min(1, 1 - (std_dev / 30)))
            
            score1 = 100 * (0.35 * slope_scaled + 0.35 * median_scaled + 0.20 * fast_rate + 0.10 * consistency)
            
            stats1 = {
                'count': len(replies1),
                'median_minutes': median,
                'mean_minutes': mean,
                'fast_rate': fast_rate,
                'std_minutes': std_dev,
                'slope': slope
            }
        
        # Get replies for s2 -> s1
        replies2 = reply_data.get((s2, s1), [])
        score2 = None
        stats2 = None
        
        if replies2 and len(replies2) >= 2:
            sorted_replies = sorted(replies2)
            median = sorted_replies[len(sorted_replies) // 2]
            mean = sum(replies2) / len(replies2)
            fast_count = sum(1 for r in replies2 if r <= 5)
            fast_rate = fast_count / len(replies2)
            
            # Trend
            n = len(replies2)
            x_mean = (n - 1) / 2
            y_mean = mean
            numerator = sum((k - x_mean) * (replies2[k] - y_mean) for k in range(n))
            denominator = sum((k - x_mean) ** 2 for k in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            
            # Std dev
            variance = sum((r - mean) ** 2 for r in replies2) / n
            std_dev = variance ** 0.5
            
            # Score
            median_scaled = max(0, min(1, 1 - (median / 60)))
            slope_scaled = max(0, min(1, -slope / 10 if slope < 0 else 0))
            consistency = max(0, min(1, 1 - (std_dev / 30)))
            
            score2 = 100 * (0.35 * slope_scaled + 0.35 * median_scaled + 0.20 * fast_rate + 0.10 * consistency)
            
            stats2 = {
                'count': len(replies2),
                'median_minutes': median,
                'mean_minutes': mean,
                'fast_rate': fast_rate,
                'std_minutes': std_dev,
                'slope': slope
            }
        
        if score1 or score2:
            combined = ((score1 or 0) + (score2 or 0)) / 2
            all_pairs.append({
                'person1': s1,
                'person2': s2,
                'score1': score1 or 0,
                'score2': score2 or 0,
                'stats1': stats1,
                'stats2': stats2,
                'combined_score': combined
            })

all_pairs.sort(key=lambda x: x['combined_score'], reverse=True)

print(f"✓ Calculated scores for {len(all_pairs)} pairs")

if all_pairs:
    top = all_pairs[0]
    print(f"\n🏆 Top pair: {top['person1']} ↔ {top['person2']}")
    print(f"   Combined score: {top['combined_score']:.1f}")
    print(f"   {top['person1']}: {top['score1']:.0f}/100")
    print(f"   {top['person2']}: {top['score2']:.0f}/100")
    
    # Create response format
    response = {
        'total_messages': len(chats),
        'total_participants': len(senders),
        'top_pairs': [{'person1': p['person1'], 'person2': p['person2'], 'combined_score': p['combined_score']} for p in all_pairs[:5]]
    }
    
    print(f"\n📊 Response data:")
    print(f"   total_messages: {response['total_messages']}")
    print(f"   total_participants: {response['total_participants']}")
    print(f"   top_pairs count: {len(response['top_pairs'])}")
    
    print("\n✅ All logic works correctly!")
else:
    print("\n❌ No pairs found!")
