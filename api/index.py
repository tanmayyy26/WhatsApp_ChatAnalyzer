"""
Flask API for WhatsApp Chat Analyzer - Vercel deployment
"""

from flask import Flask, request, jsonify
import re
import json
from datetime import datetime
from collections import Counter

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

class SimpleChatParser:
    def __init__(self, line):
        self.timestamp = None
        self.sender = None
        self.body = ""
        self.parse(line)
    
    def parse_date(self, date_str):
        formats = ['%d/%m/%Y, %H:%M:%S', '%d/%m/%Y, %H:%M', '%m/%d/%y, %I:%M %p', '%d/%m/%y, %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                pass
        return None
    
    def parse(self, line):
        pattern = r'\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?)\]?\s*-?\s*([^:]+):\s*(.+)'
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            try:
                self.timestamp = self.parse_date(match.group(1))
                self.sender = match.group(2).strip()
                self.body = match.group(3).strip()
            except:
                pass

def parse_chat_file(content):
    messages = []
    for line in content.split('\n'):
        if line.strip():
            try:
                msg = SimpleChatParser(line)
                if msg.sender and msg.body:
                    messages.append(msg)
            except:
                pass
    return messages

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WhatsApp Chat Analyzer</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
.container{max-width:1200px;margin:0 auto}
header{text-align:center;color:white;margin-bottom:40px}
header h1{font-size:2.5em;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
.upload-section{background:white;border-radius:15px;padding:40px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.2);text-align:center}
.file-input-label{display:inline-block;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 40px;border-radius:50px;font-size:1.1em;font-weight:600;cursor:pointer;transition:transform 0.3s}
.file-input-label:hover{transform:scale(1.05)}
input[type="file"]{display:none}
.results{background:white;border-radius:15px;padding:40px;box-shadow:0 10px 40px rgba(0,0,0,0.2);display:none}
.results.show{display:block}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:40px}
.stat-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;border-radius:10px;text-align:center}
.stat-card .value{font-size:2.5em;font-weight:bold;margin-top:10px}
.chart{margin-bottom:40px;background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
.loading{display:none;text-align:center;margin-top:20px;color:#667eea;font-size:1.2em}
.loading.show{display:block}
.error{color:#e74c3c;text-align:center;margin-top:20px;font-size:1.1em}
</style></head><body>
<div class="container">
<header><h1>💬 WhatsApp Chat Analyzer</h1><p>Upload your WhatsApp chat export to analyze conversations</p></header>
<div class="upload-section">
<h2 style="margin-bottom:20px;">Upload Chat File</h2>
<p style="margin-bottom:30px;color:#666;">Export your chat from WhatsApp (without media) and upload the .txt file</p>
<form id="uploadForm"><label for="fileInput" class="file-input-label">Choose File</label>
<input type="file" id="fileInput" name="file" accept=".txt" required>
<div id="fileName" style="margin-top:15px;color:#666;"></div></form>
<div class="loading" id="loading">Analyzing your chat... ⏳</div>
<div class="error" id="error"></div>
</div>
<div class="results" id="resultsSection">
<h2 style="margin-bottom:30px;color:#333;">Analysis Results</h2>
<div class="stats-grid" id="statsGrid"></div>
<div class="chart" id="topSendersChart"></div>
<div class="chart" id="wordsChart"></div>
<div class="chart" id="dailyActivityChart"></div>
</div>
</div>
<script>
const fileInput = document.getElementById('fileInput');const fileName = document.getElementById('fileName');const loading = document.getElementById('loading');const errorDiv = document.getElementById('error');
fileInput.addEventListener('change',async(e)=>{const file=e.target.files[0];if(!file)return;fileName.textContent=`Selected: ${file.name}`;loading.classList.add('show');errorDiv.textContent='';document.getElementById('resultsSection').classList.remove('show');
const formData=new FormData();formData.append('file',file);
try{const response=await fetch('/api/analyze',{method:'POST',body:formData});const data=await response.json();loading.classList.remove('show');
if(!response.ok)throw new Error(data.error||'Analysis failed');displayResults(data);}catch(error){loading.classList.remove('show');errorDiv.textContent=`Error: ${error.message}`;}});
function displayResults(data){const stats=data.basic_stats;document.getElementById('statsGrid').innerHTML=`<div class="stat-card"><div style="color:#fff;margin-bottom:10px;">💬 Total Messages</div><div class="value">${stats.total_messages.toLocaleString()}</div></div><div class="stat-card"><div style="color:#fff;margin-bottom:10px;">👥 Participants</div><div class="value">${stats.participants}</div></div><div class="stat-card"><div style="color:#fff;margin-bottom:10px;">📅 Duration (Days)</div><div class="value">${stats.duration_days}</div></div><div class="stat-card"><div style="color:#fff;margin-bottom:10px;">📈 Avg Messages/Day</div><div class="value">${stats.avg_messages_per_day.toFixed(1)}</div></div>`;
Plotly.newPlot('topSendersChart',[{x:data.top_senders.map(s=>s.messages),y:data.top_senders.map(s=>s.sender),type:'bar',orientation:'h',marker:{color:'#667eea'}}],{margin:{l:150},title:'Messages by Sender'});
Plotly.newPlot('wordsChart',[{x:data.top_words.map(w=>w.word),y:data.top_words.map(w=>w.frequency),type:'bar',marker:{color:'#764ba2'}}],{title:'Most Frequently Used Words'});
Plotly.newPlot('dailyActivityChart',[{x:data.daily_activity.map(d=>d.date),y:data.daily_activity.map(d=>d.messages),type:'scatter',mode:'lines+markers',line:{color:'#667eea'}}],{title:'Messages per Day'});
document.getElementById('resultsSection').classList.add('show');window.scrollTo({top:0,behavior:'smooth'});}
</script></body></html>'''

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files allowed'}), 400
        
        content = file.read().decode('utf-8', errors='ignore')
        msgs = parse_chat_file(content)
        
        if not msgs:
            return jsonify({'error': 'No messages found'}), 400
        
        senders = [m.sender for m in msgs]
        sender_counts = Counter(senders)
        dates = [m.timestamp for m in msgs if m.timestamp]
        
        basic_stats = {
            'total_messages': len(msgs),
            'participants': len(sender_counts),
            'duration_days': (max(dates) - min(dates)).days + 1 if dates else 0,
            'avg_messages_per_day': len(msgs) / ((max(dates) - min(dates)).days + 1) if dates else 0
        }
        
        top_senders = [{'sender': s, 'messages': c, 'percentage': (c/len(msgs))*100} for s, c in sender_counts.most_common(10)]
        
        words = []
        for msg in msgs:
            text = str(msg.body).lower()
            text = re.sub(r'[^\w\s]', '', text)
            words.extend(text.split())
        
        stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with','by','from','as','is','was','are','were','i','you','he','she','it','we','they'}
        filtered = [w for w in words if len(w) > 2 and w not in stop_words]
        word_counts = Counter(filtered)
        top_words = [{'word': w, 'frequency': c} for w, c in word_counts.most_common(20)]
        
        daily_activity = []
        if dates:
            date_counts = Counter([d.date() for d in dates])
            daily_activity = [{'date': str(d), 'messages': c} for d, c in sorted(date_counts.items())]
        
        return jsonify({
            'success': True,
            'basic_stats': basic_stats,
            'top_senders': top_senders,
            'top_words': top_words,
            'daily_activity': daily_activity,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel uses the Flask app directly
# Export as WSGI application
