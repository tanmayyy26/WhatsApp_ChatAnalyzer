# 🚀 WhatsApp Analyzer - Advanced Version

An enhanced version of the WhatsApp chat analyzer with modern features including web dashboard, sentiment analysis, advanced visualizations, and multiple export formats.

## ✨ New Features

### 1. **💕 Love Score Analyzer** (NEW!)
- **Relationship Interest Analysis**: Measure engagement between two people
- **Reply Pattern Analysis**: Track response times and trends
- **Love Score (0-100)**: Algorithmic score based on communication patterns
- **Trend Detection**: See if interest is improving or declining
- **All-Pairs Analysis**: Find best relationships in group chats
- **Detailed Metrics**: Response times, consistency, fast reply rates
- Based on behavioral psychology and communication research

### 2. **Interactive Web Dashboard**
- Real-time chat analysis with beautiful visualizations
- Drag & drop file upload
- Interactive charts using Chart.js
- Responsive design for mobile and desktop
- Export results directly from the browser

### 3. **Advanced Analytics**
- **Response Time Analysis**: Track how quickly people respond
- **Conversation Flow**: Identify conversation patterns
- **Peak Hours Detection**: Find when the chat is most active
- **Sender Interactions**: See who talks to whom most
- **Daily/Weekly Patterns**: Understand activity trends

### 4. **Sentiment Analysis**
- Analyze emotional tone of messages
- Track sentiment per sender
- Sentiment timeline visualization
- Support for multiple languages (English, Indonesian)

### 5. **Multiple Export Formats**
- **JSON**: Machine-readable data export
- **CSV**: Import into Excel or Google Sheets
- **HTML**: Beautiful standalone reports
- **PDF**: Professional reports (coming soon)

### 6. **Enhanced Configuration**
- Centralized configuration system
- Customizable analysis parameters
- Privacy settings (anonymize phone numbers)
- Performance optimizations

## 🔧 Installation

### Basic Installation
```bash
pip install -r requirements_advanced.txt
```

### Full Installation (with web dashboard)
```bash
pip install -r requirements_advanced.txt
```

## 📖 Usage

### 1. 💕 Love Score Analyzer (NEW!)

**Analyze Top 2 Most Active:**
```bash
python love_analyzer.py chat.txt
```

**Analyze Specific Pair:**
```bash
python love_analyzer.py chat.txt -t "Person A" -c "Person B"
```

**Find Best Relationships in Group:**
```bash
python love_analyzer.py chat.txt --all-pairs --top 10
```

**Export Results:**
```bash
python love_analyzer.py chat.txt --all-pairs -e love_scores.json
```

### 2. Command Line Interface (Advanced)

**Basic Analysis with Export:**
```bash
python advanced_analyzer.py chat_example.txt --export json csv html
```

**With Stop Words:**
```bash
python advanced_analyzer.py chat_example.txt -s english --export all
```

**Skip Terminal Display (Export Only):**
```bash
python advanced_analyzer.py chat_example.txt --no-display --export all
```

### 3. Web Dashboard

**Start the Dashboard:**
```bash
python web_dashboard.py
```

Then open your browser and go to: `http://127.0.0.1:5000`

**Features:**
- Upload chat files through the browser
- Interactive charts and visualizations
- Real-time analysis
- Download reports in multiple formats

### 3. Python API

```python
from advanced_analyzer import AdvancedAnalyzer

# Initialize analyzer
analyzer = AdvancedAnalyzer('chat.txt', stop_words=[])

# Load and parse
analyzer.load_file()
analyzer.parse_chats()
analyzer.process_data()

# Get statistics
stats = analyzer.get_statistics()
print(f"Total messages: {stats['overview']['total_chats']}")
print(f"Participants: {stats['overview']['unique_senders']}")

# Export results
analyzer.export_json('output.json')
analyzer.export_csv('output.csv')
analyzer.export_html('report.html')
```

### 4. Sentiment Analysis

```python
from sentiment_analyzer import SentimentAnalyzer
from chatline import Chatline

# Initialize sentiment analyzer
sa = SentimentAnalyzer(language='en')

# Analyze a message
result = sa.analyze_text("This is an amazing chat! 😊")
print(result)  # {'sentiment': 'positive', 'score': 0.8, ...}

# Analyze conversation
messages = [...]  # List of Chatline objects
sentiments = sa.analyze_conversation(messages)
sender_sentiments = sa.get_sender_sentiment(sentiments)
```

## 📊 Export Formats

### JSON Export
```json
{
  "overview": {
    "total_chats": 157,
    "unique_senders": 11,
    "unique_words": 638
  },
  "senders": [
    ["Sender1", 46],
    ["Sender2", 41]
  ]
}
```

### CSV Export
- Organized in sections (Senders, Words, Emojis, Domains)
- Ready for Excel/Google Sheets
- Easy data manipulation

### HTML Export
- Beautiful standalone reports
- Gradient visualizations
- Responsive design
- Print-friendly

## ⚙️ Configuration

```
WhatsApp-Analyzer/
├── advanced_analyzer.py      # Main advanced analyzer
├── love_analyzer.py          # 💕 Love Score analyzer (NEW!)
├── reply_analyzer.py         # Reply pattern analysis (NEW!)
├── web_dashboard.py          # Flask web application
├── sentiment_analyzer.py     # Sentiment analysis module
├── config.py                 # Configuration settings
├── chatline.py               # Chat line parser
├── patterns.py               # Regex patterns
├── font_color.py             # Terminal colors
├── whatsapp_analyzer.py      # Original analyzer
├── demo_advanced.py          # Feature demonstration
├── requirements_advanced.txt # Dependencies
├── LOVE_SCORE_GUIDE.md       # Love Score documentation (NEW!)
├── exports/                  # Exported files
├── reports/                  # HTML reports
├── data/                     # Temporary data
├── stop-words/               # Stop word files
└── templates/                # Web templates
```ORT_DIR = "exports/"
REPORTS_DIR = "reports/"
```

## 📁 Project Structure

```
WhatsApp-Analyzer/
├── advanced_analyzer.py      # Main advanced analyzer
├── web_dashboard.py          # Flask web application
├── sentiment_analyzer.py     # Sentiment analysis module
├── config.py                 # Configuration settings
├── chatline.py               # Chat line parser
├── patterns.py               # Regex patterns
├── font_color.py             # Terminal colors
├── whatsapp_analyzer.py      # Original analyzer
├── requirements_advanced.txt # Dependencies
├── exports/                  # Exported files
├── reports/                  # HTML reports
├── data/                     # Temporary data
├── stop-words/               # Stop word files
└── templates/                # Web templates
| Feature | Original | Advanced |
|---------|----------|----------|
| Terminal Analysis | ✅ | ✅ |
| Bar Charts | ✅ | ✅ |
| Heatmap | ✅ | ✅ |
| **Love Score Analysis** | ❌ | ✅ 💕 |
| **Reply Pattern Metrics** | ❌ | ✅ 💕 |
| **Relationship Insights** | ❌ | ✅ 💕 |
| Web Dashboard | ❌ | ✅ |
| Export (JSON/CSV/HTML) | ❌ | ✅ |
| Sentiment Analysis | ❌ | ✅ |
| Response Time Analysis | ❌ | ✅ |
| Conversation Flow | ❌ | ✅ |
| Interactive Charts | ❌ | ✅ |
| Progress Indicators | ❌ | ✅ |
| Sender Interactions | ❌ | ✅ |
| Peak Hours Detection | ❌ | ✅ |
| Interactive Charts | ❌ | ✅ |
| Progress Indicators | ❌ | ✅ |
| Sender Interactions | ❌ | ✅ |
| Peak Hours Detection | ❌ | ✅ |

## 🚀 Quick Start Examples

### Example 1: Generate HTML Report
```bash
python advanced_analyzer.py chat_example.txt -s english --export html
```

### Example 2: Web Analysis
```bash
python web_dashboard.py
# Open browser to http://127.0.0.1:5000
# Upload chat file
# View interactive dashboard
```

### Example 3: Full Export
```bash
python advanced_analyzer.py chat_example.txt --export all --no-display
```

### Example 4: Custom Analysis
```python
from advanced_analyzer import AdvancedAnalyzer

analyzer = AdvancedAnalyzer('chat.txt')
analyzer.load_file()
analyzer.parse_chats()
analyzer.process_data()

# Get specific insights
stats = analyzer.get_statistics()
print(f"Most active sender: {stats['senders'][0]}")
print(f"Average response time: {stats['response_times'][0]}")
print(f"Peak hour: {stats['peak_hours'][0]}")
```

## 🔒 Privacy & Security

- All processing is done locally
- No data is sent to external servers
- Optional anonymization of phone numbers
- Secure file handling
- No data persistence (unless exported)

## 🐛 Troubleshooting

### Web Dashboard Won't Start
```bash
# Make sure Flask is installed
pip install flask

# Check if port is available
netstat -an | findstr :5000
```

### Export Files Not Created
```bash
# Check if directories exist
mkdir exports reports data
```

### Unicode/Emoji Issues
```bash
# Make sure file encoding is UTF-8
# Re-export chat with UTF-8 encoding
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional sentiment lexicons
- More export formats (PDF, XML)
- Database integration
- Real-time chat monitoring
- Mobile app
- Advanced NLP features

## 📄 License

Same as original project - check LICENSE file

## 🙏 Credits

- Original WhatsApp Analyzer by PetengDedet
- Advanced features and enhancements
- Chart.js for visualizations
- Flask for web framework
- Emoji library for emoji processing

## 📞 Support

For issues or questions:
1. Check existing issues
2. Create new issue with details
3. Provide sample data (anonymized)

---

**Happy Analyzing! 📊✨**
