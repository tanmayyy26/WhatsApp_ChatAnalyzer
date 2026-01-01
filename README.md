# 💬 WhatsApp Chat Analyzer

A powerful web application to analyze WhatsApp chat exports with beautiful visualizations and insights.



---

## 📋 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [License](#license)

---

## ✨ Features

- 📊 **Message Statistics** - Total messages, participants, duration analysis
- 👥 **Sender Analysis** - Messages per sender with percentages
- 📝 **Word Cloud** - Most frequently used words (filtered stop words)
- 📈 **Activity Timeline** - Messages per day visualization
- 🎨 **Beautiful UI** - Modern gradient interface with Plotly charts
- 📱 **Responsive Design** - Works on desktop and mobile devices
- ⚡ **Fast Processing** - Instant analysis of large chat files
- 🔒 **Privacy** - Files are processed server-side only, no data storage

---

## 🛠 Technologies Used

### Backend
- **Framework**: Flask 2.3+
- **Language**: Python 3.11
- **Deployment**: Vercel Serverless Functions

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **JavaScript** - Interactive file upload and data visualization
- **Plotly.js** - Advanced charting library

### Dependencies
```
flask>=2.3.0
werkzeug>=2.3.0
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/tanmayyy26/WhatsApp_ChatAnalyzer.git
cd WhatsApp_ChatAnalyzer
```

2. **Create virtual environment**:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run locally**:
```bash
python -m flask --app api/index run
```

5. **Open browser**:
```
http://localhost:5000
```

---

## 📖 Usage

### How to Export WhatsApp Chat

1. Open WhatsApp on your phone
2. Go to the chat you want to analyze
3. Tap Menu → More → Export chat
4. Choose "Without Media"
5. Save the .txt file to your computer

### How to Use the Analyzer

1. Go to https://whatsapp-analyzer-flame.vercel.app
2. Click "Choose File" button
3. Select your exported .txt file
4. Wait for analysis to complete
5. View statistics and charts

---

## 🔌 API Endpoints

### GET `/`
Returns the main HTML interface with file upload form.

**Response**: HTML page with embedded Plotly.js charts

---

### POST `/api/analyze`
Analyzes uploaded WhatsApp chat file.

**Request**:
```
Content-Type: multipart/form-data
Body: file (text/plain, .txt format)
```

**Response** (JSON):
```json
{
  "success": true,
  "basic_stats": {
    "total_messages": 1234,
    "participants": 5,
    "duration_days": 365,
    "avg_messages_per_day": 3.38
  },
  "top_senders": [
    {
      "sender": "John",
      "messages": 450,
      "percentage": 36.5
    }
  ],
  "top_words": [
    {
      "word": "hello",
      "frequency": 28
    }
  ],
  "daily_activity": [
    {
      "date": "2024-01-01",
      "messages": 5
    }
  ],
  "timestamp": "2024-12-30T12:00:00"
}
```

**Error Responses**:
- `400` - No file provided or invalid file format
- `500` - Server error during analysis

---

## 📁 Project Structure

```
WhatsApp-Analyzer/
├── api/
│   └── index.py              # Main Flask application & API endpoints
├── docs/                     # Documentation files
├── stop-words/              # Multilingual stop words lists
├── exports/                 # Generated exports (CSV/JSON)
├── reports/                 # Generated HTML reports
├── tests/                   # Unit tests
├── uploads/                 # Temporary uploaded files
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── vercel.json             # Vercel deployment config
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
└── README.md               # This file
```

### Key Files

- **`api/index.py`** - Main Flask app with all endpoints
- **`vercel.json`** - Vercel serverless function configuration
- **`requirements.txt`** - Python package dependencies
- **`LICENSE`** - MIT License

---

## 🚀 Deployment

### Deploy to Vercel (Recommended)

1. **Push to GitHub**:
```bash
git add .
git commit -m "Update app"
git push origin main
```

2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Import your GitHub repository
   - Vercel auto-detects Python project
   - Click Deploy

3. **Your app is live!**

### Environment Variables

No environment variables required for basic deployment.

---

## 📊 Chat File Format

The analyzer supports WhatsApp chat files in these formats:

```
[12/30/2024, 10:30:45 AM] John: Hello there
[12/30/2024, 10:31:12 AM] Jane: Hi! How are you?
12/30/2024, 10:32:00 - John: I'm doing great!
```

Supported date formats:
- `DD/MM/YYYY, HH:MM:SS`
- `DD/MM/YYYY, HH:MM`
- `MM/DD/YY, HH:MM AM/PM`
- `DD-MM-YYYY, HH:MM:SS`

---

## 🔧 Configuration

### Maximum File Size
Default: 16MB

To change, edit `api/index.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Stop Words
Supported languages are in `stop-words/` directory:
- English, Spanish, French, German, Portuguese, Italian
- Russian, Arabic, Hindi, and 15+ more languages

---

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Tanmay** - [GitHub Profile](https://github.com/tanmayyy26)

---

## ❓ FAQ

**Q: Is my chat data safe?**
A: Yes! Files are processed server-side only. No data is stored or logged.

**Q: What's the file size limit?**
A: 16MB by default (can be increased if needed).

**Q: Can I use this offline?**
A: Yes! Run locally with `python -m flask --app api/index run`

**Q: Does it work with group chats?**
A: Yes! All WhatsApp chat formats are supported.

**Q: How long does analysis take?**
A: Usually 1-5 seconds depending on file size.

---

## 🐛 Bug Reports

Found a bug? Please create an issue on GitHub:
[Create Issue](https://github.com/tanmayyy26/WhatsApp_ChatAnalyzer/issues)

---

## 📞 Support

For questions or issues:
1. Check existing [GitHub Issues](https://github.com/tanmayyy26/WhatsApp_ChatAnalyzer/issues)
2. Create a new issue with detailed description
3. Include your WhatsApp chat file format if relevant

---

**Made with ❤️ for WhatsApp chat enthusiasts**
