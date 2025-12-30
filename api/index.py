"""
Flask API for WhatsApp Chat Analyzer - Vercel deployment
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from collections import Counter
import re
import os
from io import BytesIO
import json

# Import local modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzers.chatline import Chatline
from src.analyzers.reply_analyzer import ReplyAnalyzer

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        .file-input-label:hover { transform: translateY(-2px); }
        input[type="file"] { display: none; }
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 50px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        .analyze-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results-section { display: none; }
        .results-section.show { display: block; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-card .value { font-size: 2em; font-weight: bold; color: #667eea; }
        .section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .section h2 { color: #333; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 15px; }
        .chart-container { height: 400px; margin: 20px 0; }
        .message { padding: 15px; border-radius: 10px; margin: 20px 0; display: none; }
        .error { background: #fff3cd; border: 1px solid #ffc107; color: #856404; }
        .success { background: #d4edda; border: 1px solid #28a745; color: #155724; }
        .message.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💬 WhatsApp Chat Analyzer</h1>
            <p>Upload your WhatsApp chat export to discover insights! ✨</p>
        </header>
        
        <div class="upload-section">
            <h2 style="margin-bottom: 20px; color: #333;">📤 Upload Your Chat File</h2>
            <div>
                <input type="file" id="fileInput" accept=".txt" />
                <label for="fileInput" class="file-input-label">📁 Choose File</label>
                <p id="fileName" style="margin: 15px 0; color: #666;">No file selected</p>
            </div>
            <button class="analyze-btn" id="analyzeBtn" onclick="analyzeChat()" disabled>🚀 Analyze Chat</button>
            <div class="loading" id="loading"><div class="spinner"></div><p>Analyzing your chat...</p></div>
            <div class="message error" id="errorMessage"></div>
            <div class="message success" id="successMessage"></div>
        </div>
        
        <div class="results-section" id="resultsSection">
            <div class="stats-grid" id="statsGrid"></div>
            <div class="section"><h2>👥 Top Contributors</h2><div id="topSendersChart" class="chart-container"></div></div>
            <div class="section"><h2>🔤 Top Words</h2><div id="wordsChart" class="chart-container"></div></div>
            <div class="section"><h2>📅 Activity Patterns</h2><div id="dailyActivityChart" class="chart-container"></div></div>
        </div>
        
        <footer style="text-align: center; color: white; margin-top: 40px;">
            <p>Made with ❤️ | WhatsApp Analyzer v2.0</p>
        </footer>
    </div>
    
    <script>
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file selected';
            document.getElementById('fileName').textContent = fileName;
            document.getElementById('analyzeBtn').disabled = !e.target.files[0];
        });
        
        async function analyzeChat() {
            const file = document.getElementById('fileInput').files[0];
            if (!file) { showError('Please select a file first'); return; }
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('errorMessage').classList.remove('show');
            document.getElementById('successMessage').classList.remove('show');
            
            try {
                const response = await fetch('/api/analyze', { method: 'POST', body: formData });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Analysis failed');
                
                displayResults(data);
                document.getElementById('successMessage').textContent = '✅ Analysis complete!';
                document.getElementById('successMessage').classList.add('show');
            } catch (error) {
                showError(error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = '❌ ' + message;
            document.getElementById('errorMessage').classList.add('show');
        }
        
        function displayResults(data) {
            const stats = data.basic_stats;
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card"><div style="color: #999; margin-bottom: 10px;">💬 Total Messages</div><div class="value">${stats.total_messages.toLocaleString()}</div></div>
                <div class="stat-card"><div style="color: #999; margin-bottom: 10px;">👥 Participants</div><div class="value">${stats.participants}</div></div>
                <div class="stat-card"><div style="color: #999; margin-bottom: 10px;">📅 Duration (Days)</div><div class="value">${stats.duration_days}</div></div>
                <div class="stat-card"><div style="color: #999; margin-bottom: 10px;">📈 Avg Messages/Day</div><div class="value">${stats.avg_messages_per_day.toFixed(1)}</div></div>
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
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        # Read file content
        content = file.read().decode('utf-8', errors='ignore')
        lines = content.split('\n')
        
        # Parse chat
        chats = []
        previous_chat = None
        for line in lines:
            if line.strip():
                try:
                    chat = Chatline(line, previous_line=previous_chat)
                    chats.append(chat)
                    previous_chat = chat
                except:
                    pass
        
        # Filter chat messages
        msgs = [c for c in chats if c.line_type == "Chat"]
        
        if len(msgs) == 0:
            return jsonify({'error': 'No messages found in file'}), 400
        
        # Extract basic information
        senders = [c.sender for c in msgs if c.sender]
        sender_counts = Counter(senders)
        dates = [c.timestamp for c in msgs if hasattr(c, 'timestamp') and c.timestamp]
        
        # === BASIC STATISTICS ===
        basic_stats = {
            'total_messages': len(msgs),
            'participants': len(sender_counts),
            'duration_days': (max(dates) - min(dates)).days + 1 if dates else 0,
            'avg_messages_per_day': len(msgs) / ((max(dates) - min(dates)).days + 1) if dates else 0
        }
        
        # === TOP SENDERS ===
        top_senders = [
            {
                'sender': sender,
                'messages': count,
                'percentage': (count / len(msgs)) * 100
            }
            for sender, count in sender_counts.most_common(10)
        ]
        
        # === WORD CLOUD DATA ===
        words = []
        for msg in msgs:
            if hasattr(msg, 'body') and msg.body:
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
        
        # === TIME SERIES ANALYSIS ===
        daily_activity = []
        hourly_activity = [0] * 24
        day_activity = [0] * 7
        
        if dates:
            date_counts = Counter([d.date() for d in dates])
            daily_activity = [
                {'date': str(date), 'messages': count}
                for date, count in sorted(date_counts.items())
            ]
            
            for d in dates:
                hourly_activity[d.hour] += 1
                day_activity[d.weekday()] += 1
        
        hourly_data = [
            {'hour': h, 'messages': hourly_activity[h]}
            for h in range(24)
        ]
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_breakdown = [
            {'day': day_names[i], 'messages': day_activity[i]}
            for i in range(7)
        ]
        
        # === LOVE SCORE ANALYSIS ===
        love_score_data = []
        try:
            analyzer = ReplyAnalyzer(msgs)
            scores = analyzer.get_love_scores()
            if scores and len(scores) >= 2:
                love_score_data = [
                    {
                        'sender': s['sender'],
                        'love_score': round(s['love_score'], 1),
                        'message_count': s['message_count']
                    }
                    for s in scores
                ]
        except:
            pass
        
        # Prepare response
        analysis_data = {
            'success': True,
            'basic_stats': basic_stats,
            'top_senders': top_senders,
            'top_words': top_words,
            'daily_activity': daily_activity,
            'hourly_activity': hourly_data,
            'daily_breakdown': daily_breakdown,
            'love_scores': love_score_data,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format_type>', methods=['POST'])
def export_data(format_type):
    """Export analysis results"""
    try:
        data = request.get_json()
        
        if format_type == 'json':
            output = BytesIO()
            output.write(json.dumps(data, indent=2).encode())
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        elif format_type == 'csv':
            # Convert to CSV format
            df = pd.DataFrame(data.get('top_senders', []))
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
