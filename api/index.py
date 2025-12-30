"""
WhatsApp Chat Analyzer - Vercel Deployment
Uses Flask as WSGI application for Vercel
"""

from flask import Flask, request, jsonify, render_template_string
import json
import re
from datetime import datetime
from collections import Counter

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WhatsApp Chat Analyzer</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
.container{max-width:1200px;margin:0 auto}
header{text-align:center;color:white;margin-bottom:40px}
header h1{font-size:2.5em;margin-bottom:10px}
.upload-section{background:white;border-radius:15px;padding:40px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}
.upload-section h2{margin-bottom:20px}
.upload-section p{margin-bottom:30px;color:#666}
.btn{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px 40px;border-radius:50px;cursor:pointer;font-weight:600;transition:transform 0.3s}
.btn:hover{transform:scale(1.05)}
input[type=file]{display:none}
.results{background:white;border-radius:15px;padding:40px;box-shadow:0 10px 40px rgba(0,0,0,0.2);display:none}
.results.show{display:block}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:40px}
.stat-card{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:30px;border-radius:10px;text-align:center}
.stat-card .value{font-size:2.5em;font-weight:bold;margin-top:10px}
.chart{margin-bottom:40px;background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
.loading{display:none;text-align:center;margin-top:20px;color:#667eea;font-size:1.2em}
.loading.show{display:block}
.error{color:#e74c3c;text-align:center;margin-top:20px;display:none}
.error.show{display:block}
</style>
</head>
<body>
<div class="container">
<header><h1>💬 WhatsApp Chat Analyzer</h1></header>
<div class="upload-section">
<h2>Upload Chat File</h2>
<p>Export your WhatsApp chat (without media) as .txt</p>
<label for="file" class="btn">📁 Choose File</label>
<input type="file" id="file" accept=".txt">
<div id="fileName" style="margin-top:15px;color:#666"></div>
<div class="loading" id="loading">⏳ Analyzing...</div>
<div class="error" id="error"></div>
</div>
<div class="results" id="results">
<h2>Results</h2>
<div class="stats-grid" id="stats"></div>
<div class="chart" id="chart1"></div>
<div class="chart" id="chart2"></div>
<div class="chart" id="chart3"></div>
</div>
</div>
<script>
document.getElementById('file').addEventListener('change', async e => {
  const f = e.target.files[0];
  if(!f) return;
  document.getElementById('fileName').textContent = 'File: ' + f.name;
  document.getElementById('loading').classList.add('show');
  document.getElementById('error').classList.remove('show');
  const fd = new FormData();
  fd.append('file', f);
  try {
    const r = await fetch('/api/analyze', {method: 'POST', body: fd});
    const d = await r.json();
    document.getElementById('loading').classList.remove('show');
    if(!r.ok) throw d.error || 'Error';
    const s = d.basic_stats;
    document.getElementById('stats').innerHTML = `
      <div class="stat-card"><div>Messages</div><div class="value">${s.total_messages}</div></div>
      <div class="stat-card"><div>People</div><div class="value">${s.participants}</div></div>
      <div class="stat-card"><div>Days</div><div class="value">${s.duration_days}</div></div>
      <div class="stat-card"><div>Avg/Day</div><div class="value">${s.avg_messages_per_day.toFixed(1)}</div></div>
    `;
    Plotly.newPlot('chart1', [{x:d.top_senders.map(s=>s.messages),y:d.top_senders.map(s=>s.sender),type:'bar',orientation:'h',marker:{color:'#667eea'}}], {margin:{l:150},title:'Top Senders'});
    Plotly.newPlot('chart2', [{x:d.top_words.map(w=>w.word),y:d.top_words.map(w=>w.frequency),type:'bar',marker:{color:'#764ba2'}}], {title:'Top Words'});
    Plotly.newPlot('chart3', [{x:d.daily_activity.map(d=>d.date),y:d.daily_activity.map(d=>d.messages),type:'scatter',mode:'lines+markers',line:{color:'#667eea'}}], {title:'Daily Activity'});
    document.getElementById('results').classList.add('show');
  } catch(e) {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('error').textContent = 'Error: ' + e;
    document.getElementById('error').classList.add('show');
  }
});
</script>
</body>
</html>'''

@app.route('/', methods=['GET'])
def home():
    """Serve home page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded WhatsApp chat file"""
    try:
        # Check file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files allowed'}), 400
        
        # Read file
        content = file.read().decode('utf-8', errors='ignore')
        messages = parse_chat(content)
        
        if not messages:
            return jsonify({'error': 'No messages found'}), 400
        
        # Analyze
        senders = [m['sender'] for m in messages]
        sender_counts = Counter(senders)
        dates = [m['timestamp'] for m in messages]
        
        stats = {
            'total_messages': len(messages),
            'participants': len(sender_counts),
            'duration_days': (max(dates) - min(dates)).days + 1,
            'avg_messages_per_day': len(messages) / ((max(dates) - min(dates)).days + 1)
        }
        
        top_senders = [
            {'sender': s, 'messages': c, 'percentage': (c/len(messages))*100}
            for s, c in sender_counts.most_common(10)
        ]
        
        # Words
        words = []
        for m in messages:
            t = m['body'].lower()
            t = re.sub(r'[^\w\s]', '', t)
            words.extend(t.split())
        
        stop = {'the','a','an','and','or','but','in','on','at','to','for','of','is','was','i','you','me','it'}
        filtered = [w for w in words if len(w) > 2 and w not in stop]
        top_words = [{'word': w, 'frequency': c} for w, c in Counter(filtered).most_common(20)]
        
        # Daily
        daily = [{'date': str(d), 'messages': c} for d, c in sorted(Counter([d.date() for d in dates]).items())]
        
        return jsonify({
            'success': True,
            'basic_stats': stats,
            'top_senders': top_senders,
            'top_words': top_words,
            'daily_activity': daily,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_chat(content):
    """Parse WhatsApp chat file"""
    messages = []
    pattern = r'\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?)\]?\s*-?\s*([^:]+):\s*(.+)'
    
    for line in content.split('\n'):
        if not line.strip():
            continue
        match = re.match(pattern, line)
        if match:
            try:
                ts = parse_date(match.group(1))
                if ts:
                    messages.append({
                        'timestamp': ts,
                        'sender': match.group(2).strip(),
                        'body': match.group(3).strip()
                    })
            except:
                pass
    
    return messages

def parse_date(s):
    """Parse date string"""
    for fmt in ['%d/%m/%Y, %H:%M:%S', '%d/%m/%Y, %H:%M', '%m/%d/%y, %I:%M %p', '%d/%m/%y, %H:%M']:
        try:
            return datetime.strptime(s.strip(), fmt)
        except:
            pass
    return None

# For Vercel
if __name__ == '__main__':
    app.run()
