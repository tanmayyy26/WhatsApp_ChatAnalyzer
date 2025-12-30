from http.server import BaseHTTPRequestHandler
import json
import re
from datetime import datetime
from collections import Counter
from urllib.parse import parse_qs
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(get_home_html().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/analyze':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parse multipart form data
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' in content_type:
                    boundary = content_type.split('boundary=')[1].encode()
                    parts = body.split(b'--' + boundary)
                    
                    file_content = None
                    for part in parts:
                        if b'filename=' in part:
                            # Extract file content
                            header_end = part.find(b'\r\n\r\n')
                            if header_end != -1:
                                file_content = part[header_end+4:-2]
                                break
                    
                    if not file_content:
                        return self.error_response('No file found')
                    
                    # Analyze
                    try:
                        text = file_content.decode('utf-8', errors='ignore')
                        result = analyze_chat(text)
                        self.success_response(result)
                    except Exception as e:
                        self.error_response(str(e))
                else:
                    self.error_response('Invalid request')
            except Exception as e:
                self.error_response(str(e))
        else:
            self.send_response(404)
            self.end_headers()
    
    def success_response(self, data):
        response = json.dumps(data)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response.encode())
    
    def error_response(self, message):
        response = json.dumps({'error': message})
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response.encode())

def analyze_chat(content):
    """Analyze chat content"""
    messages = []
    
    for line in content.split('\n'):
        if not line.strip():
            continue
        
        pattern = r'\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?)\]?\s*-?\s*([^:]+):\s*(.+)'
        match = re.match(pattern, line)
        
        if match:
            try:
                date_str = match.group(1)
                sender = match.group(2).strip()
                body = match.group(3).strip()
                
                timestamp = parse_date(date_str)
                if timestamp:
                    messages.append({'timestamp': timestamp, 'sender': sender, 'body': body})
            except:
                pass
    
    if not messages:
        raise ValueError('No messages found')
    
    senders = [m['sender'] for m in messages]
    sender_counts = Counter(senders)
    dates = [m['timestamp'] for m in messages]
    
    basic_stats = {
        'total_messages': len(messages),
        'participants': len(sender_counts),
        'duration_days': (max(dates) - min(dates)).days + 1,
        'avg_messages_per_day': len(messages) / ((max(dates) - min(dates)).days + 1)
    }
    
    top_senders = [
        {'sender': s, 'messages': c, 'percentage': (c/len(messages))*100}
        for s, c in sender_counts.most_common(10)
    ]
    
    words = []
    for msg in messages:
        text = msg['body'].lower()
        text = re.sub(r'[^\w\s]', '', text)
        words.extend(text.split())
    
    stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with','is','was','i','you','me'}
    filtered = [w for w in words if len(w) > 2 and w not in stop_words]
    top_words = [{'word': w, 'frequency': c} for w, c in Counter(filtered).most_common(20)]
    
    date_counts = Counter([d.date() for d in dates])
    daily_activity = [{'date': str(d), 'messages': c} for d, c in sorted(date_counts.items())]
    
    return {
        'success': True,
        'basic_stats': basic_stats,
        'top_senders': top_senders,
        'top_words': top_words,
        'daily_activity': daily_activity,
        'timestamp': datetime.now().isoformat()
    }

def parse_date(date_str):
    formats = ['%d/%m/%Y, %H:%M:%S', '%d/%m/%Y, %H:%M', '%m/%d/%y, %I:%M %p', '%d/%m/%y, %H:%M']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            pass
    return None

def get_home_html():
    return '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WhatsApp Chat Analyzer</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
.container{max-width:1200px;margin:0 auto}
header{text-align:center;color:#fff;margin-bottom:40px}
header h1{font-size:2.5em;margin-bottom:10px}
.upload-section{background:#fff;border-radius:15px;padding:40px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}
.upload-section h2{margin-bottom:20px}
.upload-section p{margin-bottom:30px;color:#666}
.btn{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:15px 40px;border-radius:50px;cursor:pointer;font-weight:600;transition:transform 0.3s}
.btn:hover{transform:scale(1.05)}
input[type=file]{display:none}
.results{background:#fff;border-radius:15px;padding:40px;box-shadow:0 10px 40px rgba(0,0,0,0.2);display:none;margin-bottom:40px}
.results.show{display:block}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:40px}
.stat-card{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:30px;border-radius:10px;text-align:center}
.stat-card .value{font-size:2.5em;font-weight:bold;margin-top:10px}
.chart{margin-bottom:40px;background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
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
<p>Export from WhatsApp (without media) as .txt file</p>
<label for="fileInput" class="btn">📁 Choose File</label>
<input type="file" id="fileInput" accept=".txt">
<div id="fileName" style="margin-top:15px;color:#666"></div>
<div class="loading" id="loading">⏳ Analyzing...</div>
<div class="error" id="error"></div>
</div>
<div class="results" id="results">
<h2>Analysis Results</h2>
<div class="stats-grid" id="statsGrid"></div>
<div class="chart" id="chart1"></div>
<div class="chart" id="chart2"></div>
<div class="chart" id="chart3"></div>
</div>
</div>
<script>
document.getElementById('fileInput').addEventListener('change', async e => {
  const file = e.target.files[0];
  if(!file) return;
  document.getElementById('fileName').textContent = 'Selected: ' + file.name;
  document.getElementById('loading').classList.add('show');
  document.getElementById('error').classList.remove('show');
  document.getElementById('results').classList.remove('show');
  
  const fd = new FormData();
  fd.append('file', file);
  
  try {
    const res = await fetch('/api/analyze', {method:'POST', body:fd});
    const data = await res.json();
    document.getElementById('loading').classList.remove('show');
    if(!res.ok) throw new Error(data.error);
    
    const s = data.basic_stats;
    document.getElementById('statsGrid').innerHTML = `
      <div class="stat-card"><div>💬 Messages</div><div class="value">${s.total_messages}</div></div>
      <div class="stat-card"><div>👥 People</div><div class="value">${s.participants}</div></div>
      <div class="stat-card"><div>📅 Days</div><div class="value">${s.duration_days}</div></div>
      <div class="stat-card"><div>📈 Avg/Day</div><div class="value">${s.avg_messages_per_day.toFixed(1)}</div></div>
    `;
    Plotly.newPlot('chart1', [{x:data.top_senders.map(s=>s.messages), y:data.top_senders.map(s=>s.sender), type:'bar', orientation:'h', marker:{color:'#667eea'}}], {margin:{l:150}, title:'Top Senders'});
    Plotly.newPlot('chart2', [{x:data.top_words.map(w=>w.word), y:data.top_words.map(w=>w.frequency), type:'bar', marker:{color:'#764ba2'}}], {title:'Top Words'});
    Plotly.newPlot('chart3', [{x:data.daily_activity.map(d=>d.date), y:data.daily_activity.map(d=>d.messages), type:'scatter', mode:'lines+markers', line:{color:'#667eea'}}], {title:'Daily Activity'});
    document.getElementById('results').classList.add('show');
  } catch(err) {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('error').textContent = 'Error: ' + err.message;
    document.getElementById('error').classList.add('show');
  }
});
</script>
</body>
</html>'''
