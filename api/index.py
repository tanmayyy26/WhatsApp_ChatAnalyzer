"""
WhatsApp Chat Analyzer - Flask Version with All Features
Restored from original Streamlit app, enhanced for web
"""

from flask import Flask, request, jsonify, render_template_string
import re
from datetime import datetime
from collections import Counter
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# HTML Template with all features
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WhatsApp Chat Analyzer</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
.container{max-width:1400px;margin:0 auto}
header{text-align:center;color:white;margin-bottom:40px}
header h1{font-size:3em;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
header p{font-size:1.2em;opacity:0.9}
.section{background:white;border-radius:15px;padding:40px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}
.upload-section{text-align:center}
.upload-section h2{margin-bottom:20px;color:#333}
.upload-section p{margin-bottom:30px;color:#666;font-size:1.1em}
.btn{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px 50px;border-radius:50px;cursor:pointer;font-weight:600;font-size:1.1em;transition:transform 0.3s;border:none}
.btn:hover{transform:scale(1.05)}
input[type=file]{display:none}
.hidden{display:none !important}
.results{display:none}
.results.show{display:block}
.metrics-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;margin:30px 0}
.metric-card{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:30px;border-radius:15px;text-align:center}
.metric-card .label{font-size:0.9em;opacity:0.9}
.metric-card .value{font-size:2.8em;font-weight:bold;margin-top:10px}
.chart-container{margin:30px 0;min-height:400px}
.h2{color:#333;margin:40px 0 20px 0;font-size:2em;border-bottom:3px solid #667eea;padding-bottom:10px}
.h3{color:#555;margin:25px 0 15px 0;font-size:1.5em}
.loading{display:none;text-align:center;margin-top:20px;color:#667eea;font-size:1.2em}
.loading.show{display:block}
.error{color:#e74c3c;text-align:center;margin-top:20px;display:none;padding:20px;background:#f8d7da;border-radius:10px}
.error.show{display:block}
.top-senders-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-top:20px}
.sender-card{background:#f8f9fa;padding:20px;border-radius:10px;border-left:5px solid #667eea}
.sender-name{font-weight:bold;font-size:1.1em;color:#333}
.sender-count{color:#667eea;font-size:1.5em;font-weight:bold;margin-top:5px}
.sender-percentage{color:#999;font-size:0.9em}
.score-display{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:40px;border-radius:15px;text-align:center;margin:20px 0}
.score-value{font-size:4em;font-weight:bold}
.score-label{font-size:1.5em;margin-top:10px}
.progress-bar{background:#ddd;height:30px;border-radius:15px;overflow:hidden;margin:10px 0}
.progress-fill{background:linear-gradient(90deg,#667eea,#764ba2);height:100%;width:0;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;transition:width 0.5s}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:20px 0}
.word-cloud-container{background:#f8f9fa;padding:20px;border-radius:10px;margin-top:20px}
.words-table{width:100%;border-collapse:collapse;margin-top:15px}
.words-table th{background:#667eea;color:white;padding:12px;text-align:left}
.words-table td{padding:10px;border-bottom:1px solid #ddd}
.words-table tr:nth-child(even){background:#f8f9fa}
.activity-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-top:20px}
.stat-box{background:#f8f9fa;padding:20px;border-radius:10px;text-align:center}
.stat-value{font-size:2em;font-weight:bold;color:#667eea}
.stat-label{color:#666;margin-top:5px}
</style>
</head>
<body>
<div class="container">
<header>
<h1>💬 WhatsApp Chat Analyzer</h1>
<p>Upload your WhatsApp chat export to discover insights!</p>
</header>

<div class="section upload-section">
<h2>Upload Chat File</h2>
<p>Export your WhatsApp chat (without media) as .txt</p>
<label for="file" class="btn">📁 Choose File</label>
<input type="file" id="file" accept=".txt">
<div id="fileName" style="margin-top:15px;color:#666"></div>
<div class="loading" id="loading">⏳ Analyzing your chat...</div>
<div class="error" id="error"></div>
</div>

<div class="results" id="results">

<!-- Quick Overview -->
<div class="section">
<div class="h2">📊 Quick Overview</div>
<div class="metrics-grid">
<div class="metric-card">
<div class="label">💬 Total Messages</div>
<div class="value" id="metric-messages">-</div>
</div>
<div class="metric-card">
<div class="label">👥 Participants</div>
<div class="value" id="metric-participants">-</div>
</div>
<div class="metric-card">
<div class="label">📅 Duration (Days)</div>
<div class="value" id="metric-days">-</div>
</div>
<div class="metric-card">
<div class="label">📈 Avg Messages/Day</div>
<div class="value" id="metric-avg">-</div>
</div>
</div>
</div>

<!-- Top Contributors -->
<div class="section">
<div class="h2">👥 Top Contributors</div>
<div class="top-senders-list" id="senders-list"></div>
<div class="chart-container" id="chart-senders"></div>
</div>

<!-- Word Cloud -->
<div class="section">
<div class="h2">📝 Most Frequently Used Words</div>
<div class="chart-container" id="chart-words"></div>
<div class="word-cloud-container">
<div class="h3">Top Words</div>
<table class="words-table">
<thead>
<tr><th>Rank</th><th>Word</th><th>Frequency</th></tr>
</thead>
<tbody id="words-table-body"></tbody>
</table>
</div>
</div>

<!-- Activity Patterns -->
<div class="section">
<div class="h2">📅 Activity Patterns Over Time</div>
<div class="chart-container" id="chart-daily"></div>
<div class="grid-2">
<div class="chart-container" id="chart-hourly"></div>
<div class="chart-container" id="chart-weekly"></div>
</div>
<div class="activity-stats" id="activity-stats"></div>
</div>

<!-- Love Score -->
<div class="section">
<div class="h2">💕 Engagement Analysis</div>
<div id="love-score-section"></div>
</div>

</div> <!-- results -->

</div> <!-- container -->

<script>
document.getElementById('file').addEventListener('change', async e => {
  const file = e.target.files[0];
  if(!file) return;
  
  document.getElementById('fileName').textContent = 'File: ' + file.name;
  document.getElementById('loading').classList.add('show');
  document.getElementById('error').classList.remove('show');
  document.getElementById('results').classList.remove('show');
  
  const fd = new FormData();
  fd.append('file', file);
  
  try {
    const res = await fetch('/api/analyze', {method: 'POST', body: fd});
    const data = await res.json();
    document.getElementById('loading').classList.remove('show');
    
    if(!res.ok) throw new Error(data.error || 'Analysis failed');
    
    displayResults(data);
    document.getElementById('results').classList.add('show');
    window.scrollTo({top:0,behavior:'smooth'});
  } catch(e) {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('error').textContent = '❌ Error: ' + e.message;
    document.getElementById('error').classList.add('show');
  }
});

function displayResults(data) {
  const s = data.basic_stats;
  document.getElementById('metric-messages').textContent = s.total_messages.toLocaleString();
  document.getElementById('metric-participants').textContent = s.participants;
  document.getElementById('metric-days').textContent = s.duration_days;
  document.getElementById('metric-avg').textContent = s.avg_messages_per_day.toFixed(1);
  
  // Top Senders List
  let html = '';
  for(let i = 0; i < Math.min(5, data.top_senders.length); i++) {
    const s = data.top_senders[i];
    html += `
      <div class="sender-card">
        <div class="sender-name">#${i+1} ${s.sender}</div>
        <div class="sender-count">${s.messages} messages</div>
        <div class="sender-percentage">${s.percentage.toFixed(1)}% of total</div>
        <div class="progress-bar"><div class="progress-fill" style="width:${s.percentage}%"></div></div>
      </div>
    `;
  }
  document.getElementById('senders-list').innerHTML = html;
  
  // Bar chart
  Plotly.newPlot('chart-senders', [{
    x: data.top_senders.map(s=>s.messages),
    y: data.top_senders.map(s=>s.sender),
    type:'bar',
    orientation:'h',
    marker:{color:'#667eea'}
  }], {margin:{l:150},title:'Top 10 Message Senders',height:400});
  
  // Words chart
  Plotly.newPlot('chart-words', [{
    x: data.top_words.map(w=>w.word),
    y: data.top_words.map(w=>w.frequency),
    type:'bar',
    marker:{color:'#764ba2'}
  }], {title:'Top 20 Most Used Words',height:400});
  
  // Words table
  let table = '';
  for(let i = 0; i < data.top_words.length; i++) {
    table += `<tr><td>${i+1}</td><td>${data.top_words[i].word}</td><td>${data.top_words[i].frequency}</td></tr>`;
  }
  document.getElementById('words-table-body').innerHTML = table;
  
  // Daily activity
  Plotly.newPlot('chart-daily', [{
    x: data.daily_activity.map(d=>d.date),
    y: data.daily_activity.map(d=>d.messages),
    type:'scatter',
    mode:'lines+markers',
    line:{color:'#667eea'}
  }], {title:'Daily Message Activity',height:400});
  
  // Hourly activity
  if(data.hourly_activity) {
    Plotly.newPlot('chart-hourly', [{
      x: data.hourly_activity.map(h=>h.hour + ':00'),
      y: data.hourly_activity.map(h=>h.messages),
      type:'bar',
      marker:{color:'#e74c3c'}
    }], {title:'Activity by Hour',height:350});
  }
  
  // Weekly activity
  if(data.weekly_activity) {
    Plotly.newPlot('chart-weekly', [{
      x: data.weekly_activity.map(w=>w.day),
      y: data.weekly_activity.map(w=>w.messages),
      type:'bar',
      marker:{color:'#27ae60'}
    }], {title:'Activity by Day of Week',height:350});
  }
  
  // Activity stats
  if(data.activity_stats) {
    let stats = '';
    for(let stat of data.activity_stats) {
      stats += `
        <div class="stat-box">
          <div class="stat-label">${stat.label}</div>
          <div class="stat-value">${stat.value}</div>
        </div>
      `;
    }
    document.getElementById('activity-stats').innerHTML = stats;
  }
  
  // Love score
  if(data.love_score) {
    let score = data.love_score;
    let verdict = '';
    let color = '';
    if(score >= 75) {venture = '💚 Very High Engagement'; color = '#196127';}
    else if(score >= 60) {verdict = '💚 High Engagement'; color = '#239a3b';}
    else if(score >= 45) {verdict = '💛 Moderate Engagement'; color = '#7bc96f';}
    else if(score >= 30) {verdict = '🧡 Low Engagement'; color = '#c6e48b';}
    else {verdict = '🤍 Very Low Engagement'; color = '#ebedf0';}
    
    document.getElementById('love-score-section').innerHTML = `
      <div class="score-display" style="background:linear-gradient(135deg,${color},${color})">
        <div class="score-value">${score.toFixed(1)}%</div>
        <div class="score-label">${verdict}</div>
      </div>
      <p style="text-align:center;color:#666;margin-top:15px">Engagement score based on message frequency, reply patterns, and consistency</p>
    `;
  }
}
</script>
</body>
</html>'''

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files allowed'}), 400
        
        content = file.read().decode('utf-8', errors='ignore')
        messages = parse_chat(content)
        
        if not messages:
            return jsonify({'error': 'No messages found'}), 400
        
        # Basic stats
        senders = [m['sender'] for m in messages]
        sender_counts = Counter(senders)
        dates = [m['timestamp'] for m in messages]
        
        stats = {
            'total_messages': len(messages),
            'participants': len(sender_counts),
            'duration_days': (max(dates) - min(dates)).days + 1,
            'avg_messages_per_day': len(messages) / ((max(dates) - min(dates)).days + 1)
        }
        
        # Top senders
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
        
        stop = {'the','a','an','and','or','but','in','on','at','to','for','of','is','was','i','you','me','it','this','that','with','have','from','been','be','are','be','do','does','did','will','would','could','should','may','might','can','he','she','we','they','my','your','his','her','its','our','their','him','us','them'}
        filtered = [w for w in words if len(w) > 2 and w not in stop]
        word_counts = Counter(filtered)
        top_words = [{'word': w, 'frequency': c} for w, c in word_counts.most_common(20)]
        
        # Daily/Hourly/Weekly
        daily = [{'date': str(d), 'messages': c} for d, c in sorted(Counter([d.date() for d in dates]).items())]
        hourly = [{'hour': h, 'messages': Counter([d.hour for d in dates]).get(h, 0)} for h in range(24)]
        day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        weekly = [{'day': day_names[i], 'messages': Counter([d.weekday() for d in dates]).get(i, 0)} for i in range(7)]
        
        # Activity stats
        date_counts = Counter([d.date() for d in dates])
        busiest = max(date_counts.items(), key=lambda x: x[1])
        activity_stats = [
            {'label': 'Most Active Day', 'value': f"{busiest[0].strftime('%b %d')}"},
            {'label': 'Active Days', 'value': f"{len(date_counts)}"},
            {'label': 'Avg per Day', 'value': f"{sum(date_counts.values())/len(date_counts):.1f}"}
        ]
        
        # Love score (engagement)
        if len(sender_counts) >= 2:
            avg_messages = stats['avg_messages_per_day']
            consistency = min(len(date_counts) / ((stats['duration_days']) + 1), 1) * 100
            love_score = (consistency * 0.6 + min(avg_messages * 2, 100) * 0.4)
        else:
            love_score = 50
        
        return jsonify({
            'basic_stats': stats,
            'top_senders': top_senders,
            'top_words': top_words,
            'daily_activity': daily,
            'hourly_activity': hourly,
            'weekly_activity': weekly,
            'activity_stats': activity_stats,
            'love_score': love_score,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_chat(content):
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
    for fmt in ['%d/%m/%Y, %H:%M:%S', '%d/%m/%Y, %H:%M', '%m/%d/%y, %I:%M %p', '%d/%m/%y, %H:%M']:
        try:
            return datetime.strptime(s.strip(), fmt)
        except:
            pass
    return None

if __name__ == '__main__':
    app.run()
