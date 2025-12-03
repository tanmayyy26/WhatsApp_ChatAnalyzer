# 💕 Love Score Analyzer - NEW FEATURE!

## What is Love Score?

The **Love Score** is a unique feature that analyzes WhatsApp chat reply patterns to measure **relationship interest** between two people. It uses behavioral psychology principles to evaluate:

- **Reply Speed**: How quickly someone responds
- **Reply Trends**: Are they getting faster or slower over time?
- **Consistency**: How reliable are their response times?
- **Fast Reply Rate**: Percentage of replies within 5 minutes

## How It Works

The Love Score algorithm analyzes:

1. **Slope Trend (35% weight)**: Negative slope = getting faster over time ✨
2. **Median Reply Time (35% weight)**: Lower times = more interest 💗
3. **Fast Reply Rate (20% weight)**: More <5min replies = higher engagement ⚡
4. **Consistency (10% weight)**: Lower variation = more predictable/committed 📊

### Score Interpretation

| Score | Verdict | Meaning |
|-------|---------|---------|
| 75-100 | Strong Interest 💕 | Very engaged, fast & improving replies |
| 55-74 | Moderate Interest 💗 | Good engagement, consistent replies |
| 35-54 | Low Interest 💙 | Sporadic or slow replies |
| 0-34 | Very Low Interest 💔 | Minimal engagement |

## Usage

### Basic Analysis (Top 2 Most Active)
```bash
py love_analyzer.py chat.txt
```

### Analyze Specific Pair
```bash
py love_analyzer.py chat.txt -t "John Doe" -c "Jane Smith"
```

### Find Top Relationships in Group Chat
```bash
py love_analyzer.py chat.txt --all-pairs --top 5
```

### Export Results to JSON
```bash
py love_analyzer.py chat.txt --all-pairs -e results.json
```

## Example Output

```
================================================================================
💕 LOVE SCORE ANALYSIS: John ← → Jane
================================================================================

📊 John Analysis:
--------------------------------------------------------------------------------
   Love Score: [█████████████████░░░] 85%
   Verdict: Strong interest 💕

   Reply Statistics:
      • Total Replies: 42
      • Median Reply Time: 3.5 minutes
      • Average Reply Time: 8.2 minutes
      • Fast Reply Rate: 78.6% (within 5 min)
      • Consistency (StdDev): 12.3 minutes
      • Reply Trend: 📉 Getting FASTER (-0.45)
      • Trend Strength (R²): 0.72

   Score Breakdown:
      • Trend Score: 31.5 points
      • Speed Score: 34.2 points
      • Fast Rate Score: 15.7 points
      • Consistency Score: 7.9 points

⚖️  Head-to-Head Comparison:
--------------------------------------------------------------------------------
   🏃 Faster Replier: John
   📏 More Consistent: Jane
   📈 Improving Faster: John
   ⏱️  Median Time Difference: 2.3 minutes

💡 Interpretation:
--------------------------------------------------------------------------------
   💖 John shows stronger interest in the conversation!
      (8 points higher)
   ⚡ Very responsive conversation - both reply quickly!
```

## Use Cases

### 1. Dating Context
```bash
# Check if they're interested in you!
py love_analyzer.py date_chat.txt -t "Your Name" -c "Their Name"
```

### 2. Group Chat Analysis
```bash
# Find who has the best chemistry in your friend group
py love_analyzer.py group_chat.txt --all-pairs --top 10
```

### 3. Customer Support
```bash
# Measure response quality between support agent and customer
py love_analyzer.py support_chat.txt -t "Agent" -c "Customer"
```

### 4. Team Communication
```bash
# Identify strong working relationships
py love_analyzer.py team_chat.txt --all-pairs
```

## Science Behind It

The Love Score is based on:

1. **Communication Accommodation Theory**: People who are interested tend to mirror and match communication patterns
2. **Response Latency Research**: Faster responses indicate higher engagement and interest
3. **Behavioral Consistency**: Consistent patterns show commitment and reliability
4. **Trend Analysis**: Improving response times over time indicate growing interest

## Features

✅ **Individual Analysis**: Detailed metrics for each person
✅ **Comparative Analysis**: Head-to-head comparison
✅ **Trend Detection**: Identify improving/declining patterns
✅ **Group Analysis**: Find best pairs in group chats
✅ **Visual Indicators**: Progress bars and emoji indicators
✅ **JSON Export**: Save results for further analysis
✅ **Detailed Breakdown**: See exactly how the score is calculated

## Tips for Accurate Results

1. **Use chats with at least 20+ replies** between two people
2. **Longer time periods** give more accurate trends
3. **1-on-1 chats** work best (group chats can be noisy)
4. **Recent chats** reflect current dynamics better

## Privacy Note

⚠️ **All analysis is done locally on your computer**
- No data is sent anywhere
- No cloud processing
- Your conversations remain private
- Results are only saved if you use --export

## Limitations

- System messages and media are excluded
- Assumes alternating conversation pattern
- Group chats may have confounding factors
- Very short conversations (<10 replies) may be unreliable

## Integration with Other Tools

### Use with Advanced Analyzer
```bash
# First get general stats
py advanced_analyzer.py chat.txt --export html

# Then analyze love scores
py love_analyzer.py chat.txt --all-pairs -e love_scores.json
```

### Combine with Sentiment Analysis
```python
from advanced_analyzer import AdvancedAnalyzer
from love_analyzer import ReplyAnalyzer
from sentiment_analyzer import SentimentAnalyzer

# Get love score + sentiment together
analyzer = AdvancedAnalyzer('chat.txt')
reply = ReplyAnalyzer(messages)
sentiment = SentimentAnalyzer()

# Full relationship analysis!
```

## Coming Soon

- 📊 Web dashboard integration
- 📈 Time-series visualization
- 🎯 Predictive trends
- 💬 Message quality analysis
- 🔔 Pattern change detection

---

**Remember: Love Score is for fun and insight, not relationship advice!** 💕

Use it to:
- Understand communication patterns
- Identify engagement levels  
- Track relationship dynamics
- Have fun with friends

**Not recommended for:**
- Making serious relationship decisions
- Confronting people about their "score"
- Comparing yourself to others
- Creating anxiety about responses

**Communication is complex - this is just one lens to view it through!** 🌈
