"""
Flask API for WhatsApp Chat Analyzer - Vercel deployment (Minimal Version)
"""

from flask import Flask, request, jsonify
import re
import json
from datetime import datetime
from collections import Counter

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Simple WhatsApp chat parser
class SimpleChatParser:
    def __init__(self, line):
        self.line = line
        self.timestamp = None
        self.sender = None
        self.body = ""
        self.line_type = None
        self.parse()
    
    def parse_date(self, date_str):
        """Parse various WhatsApp date formats"""
        try:
            formats = [
                '%d/%m/%Y, %H:%M:%S',
                '%d/%m/%Y, %H:%M',
                '%m/%d/%y, %I:%M %p',
                '%d/%m/%y, %H:%M',
                '%d-%m-%Y, %H:%M:%S',
                '%d-%m-%Y, %H:%M',
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except:
                    continue
            return None
        except:
            return None
    
    def parse(self):
        pattern = r'\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?)\]?\s*-?\s*([^:]+):\s*(.+)'
        match = re.match(pattern, self.line, re.IGNORECASE)
        
        if match:
            try:
                self.timestamp = self.parse_date(match.group(1))
                self.sender = match.group(2).strip()
                self.body = match.group(3).strip()
                self.line_type = "Chat"
            except:
                self.line_type = "Event"
        else:
            self.line_type = "Event"

def parse_chat_file(content):
    """Parse WhatsApp chat file content"""
    lines = content.split('\n')
    messages = []
    
    for line in lines:
        if line.strip():
            try:
                msg = SimpleChatParser(line)
                if msg.line_type == "Chat" and msg.sender and msg.body:
                    messages.append(msg)
            except:
                pass
    
    return messages

@app.route('/')
def home():
    """Render home page"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Chat Analyzer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; color: white; margin-bottom: 40px; }
        header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .upload-section {
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }
        .file-input-label {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .file-input-label:hover { transform: scale(1.05); }
        input[type="file"] { display: none; }
        .results { background: white; border-radius: 15px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); display: none; }
        .results.show { display: block; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }
        .stat-card .value { font-size: 2.5em; font-weight: bold; margin-top: 10px; }
        .chart { margin-bottom: 40px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .loading { display: none; text-align: center; margin-top: 20px; color: #667eea; font-size: 1.2em; }
        .loading.show { display: block; }
        .error { color: #e74c3c; text-align: center; margin-top: 20px; font-size: 1.1em; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💬 WhatsApp Chat Analyzer</h1>
            <p>Upload your WhatsApp chat export to analyze conversations</p>
        </header>
        
        <div class="upload-section">
            <h2 style="margin-bottom: 20px;">Upload Chat File</h2>
            <p style="margin-bottom: 30px; color: #666;">Export your chat from WhatsApp (without media) and upload the .txt file</p>
            <form id="uploadForm">
                <label for="fileInput" class="file-input-label">Choose File</label>
                <input type="file" id="fileInput" name="file" accept=".txt" required>
                <div id="fileName" style="margin-top: 15px; color: #666;"></div>
            </form>
            <div class="loading" id="loading">Analyzing your chat... ⏳</div>
            <div class="error" id="error"></div>
        </div>
        
        <div class="results" id="resultsSection">
            <h2 style="margin-bottom: 30px; color: #333;">Analysis Results</h2>
            <div class="stats-grid" id="statsGrid"></div>
            <div class="chart" id="topSendersChart"></div>
            <div class="chart" id="wordsChart"></div>
            <div class="chart" id="dailyActivityChart"></div>
        </div>
    </div>
    
    <script>
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const loading = document.getElementById('loading');
        const errorDiv = document.getElementById('error');
        
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            fileName.textContent = `Selected: ${file.name}`;
            loading.classList.add('show');
            errorDiv.textContent = '';
            document.getElementById('resultsSection').classList.remove('show');
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                loading.classList.remove('show');
                
                if (!response.ok) {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                displayResults(data);
            } catch (error) {
                loading.classList.remove('show');
                errorDiv.textContent = `Error: ${error.message}`;
            }
        });
        
        function displayResults(data) {
            const stats = data.basic_stats;
            
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card"><div style="color: #fff; margin-bottom: 10px;">💬 Total Messages</div><div class="value">${stats.total_messages.toLocaleString()}</div></div>
                <div class="stat-card"><div style="color: #fff; margin-bottom: 10px;">👥 Participants</div><div class="value">${stats.participants}</div></div>
                <div class="stat-card"><div style="color: #fff; margin-bottom: 10px;">📅 Duration (Days)</div><div class="value">${stats.duration_days}</div></div>
                <div class="stat-card"><div style="color: #fff; margin-bottom: 10px;">📈 Avg Messages/Day</div><div class="value">${stats.avg_messages_per_day.toFixed(1)}</div></div>
            `;
            
            Plotly.newPlot('topSendersChart', [{
                x: data.top_senders.map(s => s.messages),
                y: data.top_senders.map(s => s.sender),
                type: 'bar', orientation: 'h', marker: { color: '#667eea' }
            }], { margin: { l: 150 }, title: 'Messages by Sender' });
            
            Plotly.newPlot('wordsChart', [{
                x: data.top_words.map(w => w.word),
                y: data.top_words.map(w => w.frequency),
                type: 'bar', marker: { color: '#764ba2' }
            }], { title: 'Most Frequently Used Words' });
            
            Plotly.newPlot('dailyActivityChart', [{
                x: data.daily_activity.map(d => d.date),
                y: data.daily_activity.map(d => d.messages),
                type: 'scatter', mode: 'lines+markers', line: { color: '#667eea' }
            }], { title: 'Messages per Day' });
            
            document.getElementById('resultsSection').classList.add('show');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>'''
    return html

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        # Read and parse file content
        content = file.read().decode('utf-8', errors='ignore')
        msgs = parse_chat_file(content)
        
        if len(msgs) == 0:
            return jsonify({'error': 'No messages found in file'}), 400
        
        # Extract basic information
        senders = [m.sender for m in msgs if m.sender]
        sender_counts = Counter(senders)
        dates = [m.timestamp for m in msgs if m.timestamp]
        
        # Basic statistics
        basic_stats = {
            'total_messages': len(msgs),
            'participants': len(sender_counts),
            'duration_days': (max(dates) - min(dates)).days + 1 if dates else 0,
            'avg_messages_per_day': len(msgs) / ((max(dates) - min(dates)).days + 1) if dates else 0
        }
        
        # Top senders
        top_senders = [
            {
                'sender': sender,
                'messages': count,
                'percentage': (count / len(msgs)) * 100
            }
            for sender, count in sender_counts.most_common(10)
        ]
        
        # Word analysis
        words = []
        for msg in msgs:
            if msg.body:
                text = str(msg.body).lower()
                text = re.sub(r'[^\w\s]', '', text)
                words.extend(text.split())
        
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
                      'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your',
                      'his', 'her', 'its', 'our', 'their', 'me', 'him', 'us', 'them'}
        
        filtered_words = [w for w in words if len(w) > 2 and w not in stop_words]
        word_counts = Counter(filtered_words)
        
        top_words = [
            {'word': word, 'frequency': count}
            for word, count in word_counts.most_common(20)
        ]
        
        # Time series analysis
        daily_activity = []
        if dates:
            date_counts = Counter([d.date() for d in dates])
            daily_activity = [
                {'date': str(date), 'messages': count}
                for date, count in sorted(date_counts.items())
            ]
        
        # Prepare response
        analysis_data = {
            'success': True,
            'basic_stats': basic_stats,
            'top_senders': top_senders,
            'top_words': top_words,
            'daily_activity': daily_activity,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel handler
def handler(event, context):
    return app(event, context)
