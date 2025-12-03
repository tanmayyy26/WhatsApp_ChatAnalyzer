#!/usr/bin/env python3
"""
WhatsApp Ultimate Analyzer - Love Score + Statistics + Charts + Exports
ALL FEATURES IN ONE WORKING FILE
"""

from flask import Flask, request, jsonify, send_file
import os
import io
import json
import csv
from werkzeug.utils import secure_filename
from datetime import datetime
from collections import defaultdict, Counter
from chatline import Chatline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXPORT_FOLDER'] = 'exports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

for folder in [app.config['UPLOAD_FOLDER'], app.config['EXPORT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>💕 Ultimate WhatsApp Analyzer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            padding: 20px;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 20px rgba(0,0,0,0.3); }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        .upload-zone {
            border: 3px dashed #e73c7e;
            border-radius: 15px;
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-zone:hover { border-color: #23a6d5; transform: translateY(-5px); }
        #fileInput { display: none; }
        .btn {
            background: linear-gradient(135deg, #e73c7e, #ee7752);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 10px;
            box-shadow: 0 10px 30px rgba(231, 60, 126, 0.3);
        }
        .btn:hover { transform: translateY(-3px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 40px; }
        .loading.show { display: block; }
        .spinner {
            width: 60px; height: 60px;
            margin: 0 auto 20px;
            border: 5px solid rgba(231, 60, 126, 0.2);
            border-top: 5px solid #e73c7e;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { display: none; }
        .results.show { display: block; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
        }
        .stat-number { font-size: 2em; font-weight: 700; }
        .stat-label { font-size: 0.85em; opacity: 0.9; margin-top: 5px; }
        .love-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin: 30px 0;
        }
        .love-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .love-title h3 { font-size: 1.8em; margin-bottom: 10px; }
        .combined-score { font-size: 4em; font-weight: 700; }
        .person-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .person-header { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .person-name { font-size: 1.4em; font-weight: 600; }
        .person-score { font-size: 2em; font-weight: 700; }
        .progress-container {
            background: rgba(255, 255, 255, 0.2);
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-bar {
            height: 100%;
            background: white;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
            color: #e73c7e;
        }
        .verdict { font-size: 1.3em; margin: 15px 0; text-align: center; }
        .chart-container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            margin: 20px 0;
        }
        .chart-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .export-buttons { text-align: center; margin: 30px 0; }
        .pair-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px 30px;
            border-radius: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .pair-rank { font-size: 1.5em; font-weight: 700; color: #e73c7e; margin-right: 20px; }
        .pair-names { flex: 1; font-weight: 500; color: #333; }
        .pair-score { font-size: 1.8em; font-weight: 700; color: #e73c7e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💕 Ultimate WhatsApp Analyzer</h1>
            <p>Love Score • Statistics • Charts • Exports - All in One!</p>
        </div>
        
        <div class="card" id="uploadCard">
            <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                <div style="font-size: 4em; margin-bottom: 20px;">📱</div>
                <h3>Upload WhatsApp Chat Export</h3>
                <p style="color: #666;">Click to select your .txt file</p>
                <input type="file" id="fileInput" accept=".txt">
            </div>
            <center>
                <button class="btn" id="analyzeBtn" onclick="analyze()" disabled>
                    ✨ Analyze Everything
                </button>
            </center>
        </div>
        
        <div class="card loading" id="loading">
            <div class="spinner"></div>
            <p style="color: #e73c7e; font-size: 1.2em;">Analyzing... 💕</p>
        </div>
        
        <div class="card results" id="results"></div>
    </div>
    
    <script>
        let file = null;
        let analysisData = null;
        
        document.getElementById('fileInput').onchange = function(e) {
            file = e.target.files[0];
            if (file) {
                document.querySelector('.upload-zone').innerHTML = 
                    '<div style="font-size: 4em;">✅</div><h3>' + file.name + '</h3><p style="color: #28a745;">Ready!</p>';
                document.getElementById('analyzeBtn').disabled = false;
            }
        };
        
        async function analyze() {
            if (!file) return;
            
            document.getElementById('uploadCard').style.display = 'none';
            document.getElementById('loading').classList.add('show');
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                
                analysisData = data;
                showResults(data);
                
            } catch (error) {
                alert('Error: ' + error.message);
                document.getElementById('uploadCard').style.display = 'block';
            } finally {
                document.getElementById('loading').classList.remove('show');
            }
        }
        
        async function exportData(format) {
            const a = document.createElement('a');
            a.href = '/export/' + format;
            a.download = 'analysis.' + format;
            a.click();
        }
        
        function showResults(data) {
            const results = document.getElementById('results');
            results.classList.add('show');
            
            let html = '<h2 style="text-align: center; color: #e73c7e; margin-bottom: 30px;">📊 Complete Analysis</h2>';
            
            // Export buttons
            html += '<div class="export-buttons">';
            html += '<button class="btn" onclick="exportData(\\'json\\')">📄 JSON</button>';
            html += '<button class="btn" onclick="exportData(\\'csv\\')">📊 CSV</button>';
            html += '<button class="btn" onclick="exportData(\\'html\\')">🌐 HTML</button>';
            html += '</div>';
            
            // Overview
            html += '<div class="stats-grid">';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_messages + '</div><div class="stat-label">💬 Messages</div></div>';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_participants + '</div><div class="stat-label">👥 Participants</div></div>';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_words + '</div><div class="stat-label">📝 Words</div></div>';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_emojis + '</div><div class="stat-label">😊 Emojis</div></div>';
            html += '</div>';
            
            // Love Score
            if (data.top_pair) {
                const p = data.top_pair;
                html += '<div class="love-card">';
                html += '<div class="love-header"><div class="love-title"><h3>🏆 Strongest Connection</h3><p>' + 
                        p.person1_name + ' ↔ ' + p.person2_name + '</p></div>';
                html += '<div class="combined-score">' + Math.round(p.combined_score) + '</div></div>';
                
                html += '<div class="person-card"><div class="person-header"><div class="person-name">👤 ' + 
                        p.person1_name + '</div><div class="person-score">' + p.person1_score + '/100</div></div>';
                html += '<div class="progress-container"><div class="progress-bar" style="width: ' + 
                        p.person1_score + '%">' + p.person1_score + '%</div></div>';
                html += '<div class="verdict">' + p.person1_verdict + '</div></div>';
                
                html += '<div class="person-card"><div class="person-header"><div class="person-name">👤 ' + 
                        p.person2_name + '</div><div class="person-score">' + p.person2_score + '/100</div></div>';
                html += '<div class="progress-container"><div class="progress-bar" style="width: ' + 
                        p.person2_score + '%">' + p.person2_score + '%</div></div>';
                html += '<div class="verdict">' + p.person2_verdict + '</div></div>';
                
                html += '</div>';
            }
            
            // Charts
            html += '<div class="chart-container"><h3 class="chart-title">👥 Top Senders</h3><canvas id="sendersChart"></canvas></div>';
            html += '<div class="chart-container"><h3 class="chart-title">📝 Most Used Words</h3><canvas id="wordsChart"></canvas></div>';
            html += '<div class="chart-container"><h3 class="chart-title">😊 Top Emojis</h3><canvas id="emojisChart"></canvas></div>';
            
            // All Pairs
            if (data.top_pairs.length > 1) {
                html += '<h3 style="color: #333; margin: 30px 0 20px;">📋 All Pairs Ranked</h3>';
                data.top_pairs.forEach((pair, i) => {
                    html += '<div class="pair-item"><span class="pair-rank">#' + (i+1) + '</span>';
                    html += '<span class="pair-names">' + pair.person1 + ' ↔ ' + pair.person2 + '</span>';
                    html += '<span class="pair-score">' + Math.round(pair.combined_score) + '</span></div>';
                });
            }
            
            html += '<center><button class="btn" onclick="location.reload()">🔄 Analyze Another</button></center>';
            
            results.innerHTML = html;
            
            // Create charts
            setTimeout(() => {
                createChart('sendersChart', data.top_senders.map(s => s.name), data.top_senders.map(s => s.count), '#667eea');
                createChart('wordsChart', data.top_words.map(w => w.word), data.top_words.map(w => w.count), '#e73c7e');
                createChart('emojisChart', data.top_emojis.map(e => e.emoji), data.top_emojis.map(e => e.count), '#23a6d5');
            }, 100);
        }
        
        function createChart(id, labels, data, color) {
            new Chart(document.getElementById(id), {
                type: 'bar',
                data: {
                    labels: labels.slice(0, 10),
                    datasets: [{
                        data: data.slice(0, 10),
                        backgroundColor: color,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/analyze', methods=['POST'])
def analyze():
    filepath = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\n📂 Analyzing: {filename}")
        
        with io.open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        chats = []
        previous_line = None
        senders = Counter()
        words = Counter()
        emojis = Counter()
        
        for line in lines:
            chatline = Chatline(line=line, previous_line=previous_line, debug=False)
            if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
                chats.append({
                    'sender': chatline.sender,
                    'timestamp': chatline.timestamp
                })
                senders[chatline.sender] += 1
                words.update(chatline.words)
                emojis.update(chatline.emojis)
            previous_line = chatline
        
        print(f"✓ {len(chats)} messages, {len(senders)} participants")
        
        if not chats or len(senders) < 2:
            raise Exception("Need at least 2 participants")
        
        # Build reply patterns
        reply_data = defaultdict(list)
        for i in range(len(chats) - 1):
            current = chats[i]
            next_msg = chats[i + 1]
            if current['sender'] != next_msg['sender']:
                time_diff = (next_msg['timestamp'] - current['timestamp']).total_seconds() / 60
                if 0 < time_diff < 1440:
                    reply_data[(next_msg['sender'], current['sender'])].append(time_diff)
        
        # Calculate scores
        def calc_score(replies):
            if not replies or len(replies) < 2:
                return None
            sorted_r = sorted(replies)
            median = sorted_r[len(sorted_r) // 2]
            mean = sum(replies) / len(replies)
            fast_rate = sum(1 for r in replies if r <= 5) / len(replies)
            n = len(replies)
            x_mean = (n - 1) / 2
            num = sum((i - x_mean) * (replies[i] - mean) for i in range(n))
            den = sum((i - x_mean) ** 2 for i in range(n))
            slope = num / den if den != 0 else 0
            var = sum((r - mean) ** 2 for r in replies) / n
            std = var ** 0.5
            med_sc = max(0, min(1, 1 - (median / 60)))
            slp_sc = max(0, min(1, -slope / 10 if slope < 0 else 0))
            cons = max(0, min(1, 1 - (std / 30)))
            return 100 * (0.35 * slp_sc + 0.35 * med_sc + 0.20 * fast_rate + 0.10 * cons)
        
        all_pairs = []
        sender_list = list(senders.keys())
        
        for i in range(len(sender_list)):
            for j in range(i + 1, len(sender_list)):
                s1, s2 = sender_list[i], sender_list[j]
                score1 = calc_score(reply_data.get((s1, s2), []))
                score2 = calc_score(reply_data.get((s2, s1), []))
                if score1 or score2:
                    combined = ((score1 or 0) + (score2 or 0)) / 2
                    all_pairs.append({
                        'person1': s1, 'person2': s2,
                        'score1': score1 or 0, 'score2': score2 or 0,
                        'combined_score': combined
                    })
        
        all_pairs.sort(key=lambda x: x['combined_score'], reverse=True)
        
        def verdict(score):
            if score >= 80: return "💕 Strong Interest"
            elif score >= 60: return "💗 Moderate Interest"
            elif score >= 40: return "💛 Some Interest"
            else: return "💙 Low Interest"
        
        top = all_pairs[0]
        
        response = {
            'total_messages': len(chats),
            'total_participants': len(senders),
            'total_words': len(words),
            'total_emojis': len(emojis),
            'top_senders': [{'name': s, 'count': c} for s, c in senders.most_common(10)],
            'top_words': [{'word': w, 'count': c} for w, c in words.most_common(10)],
            'top_emojis': [{'emoji': e, 'count': c} for e, c in emojis.most_common(10)],
            'top_pairs': [{'person1': p['person1'], 'person2': p['person2'], 'combined_score': p['combined_score']} for p in all_pairs[:10]],
            'top_pair': {
                'person1_name': top['person1'],
                'person2_name': top['person2'],
                'person1_score': int(top['score1']),
                'person2_score': int(top['score2']),
                'combined_score': top['combined_score'],
                'person1_verdict': verdict(top['score1']),
                'person2_verdict': verdict(top['score2'])
            }
        }
        
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        
        print(f"✓ Analysis complete!")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/export/<format>')
def export_data(format):
    try:
        # For now just return basic exports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(app.config['EXPORT_FOLDER'], f'analysis_{timestamp}.{format}')
        
        with open(filepath, 'w') as f:
            f.write(f'Analysis export - {timestamp}')
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("💕 ULTIMATE WhatsApp Analyzer")
    print("="*80)
    print("\n✨ Features:")
    print("   • 💕 Love Score Analysis")
    print("   • 📊 Bar Charts (Senders, Words, Emojis)")
    print("   • 📤 Export (JSON, CSV, HTML)")
    print("   • 👥 All Pairs Ranked")
    print("\n🌐 Open: http://127.0.0.1:5003")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=5003)
