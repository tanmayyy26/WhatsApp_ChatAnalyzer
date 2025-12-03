#!/usr/bin/env python3
"""
WhatsApp Love Score Analyzer - FINAL WORKING VERSION
Completely tested and verified
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import io
from werkzeug.utils import secure_filename
from datetime import datetime
from collections import defaultdict
from chatline import Chatline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 WhatsApp Love Score Analyzer</title>
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
        
        .container { max-width: 1000px; margin: 0 auto; }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeIn 0.8s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 20px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.95; }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            animation: fadeIn 0.8s ease;
        }
        
        .upload-zone {
            border: 3px dashed #e73c7e;
            border-radius: 15px;
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .upload-zone:hover {
            border-color: #23a6d5;
            background: linear-gradient(135deg, rgba(231, 60, 126, 0.05), rgba(35, 166, 213, 0.05));
            transform: translateY(-5px);
        }
        
        .upload-icon { font-size: 4em; margin-bottom: 20px; }
        .upload-zone h3 { font-size: 1.5em; color: #333; margin-bottom: 10px; }
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
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(231, 60, 126, 0.3);
        }
        
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(231, 60, 126, 0.4); }
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
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results { display: none; }
        .results.show { display: block; animation: fadeIn 0.8s; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .stat-number { font-size: 2.5em; font-weight: 700; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        
        .love-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin: 30px 0;
            box-shadow: 0 20px 60px rgba(245, 87, 108, 0.4);
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
        
        .person-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
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
        
        .pair-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px 30px;
            border-radius: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .pair-rank { font-size: 1.5em; font-weight: 700; color: #e73c7e; margin-right: 20px; }
        .pair-names { flex: 1; font-weight: 500; color: #333; }
        .pair-score { font-size: 1.8em; font-weight: 700; color: #e73c7e; }
        
        .alert {
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            font-weight: 500;
            background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💕 Love Score Analyzer</h1>
            <p>Discover relationship dynamics through WhatsApp analysis</p>
        </div>
        
        <div class="card" id="uploadCard">
            <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📱</div>
                <h3>Upload WhatsApp Chat Export</h3>
                <p style="color: #666;">Click to select your .txt file</p>
                <input type="file" id="fileInput" accept=".txt">
            </div>
            <center>
                <button class="btn" id="analyzeBtn" onclick="analyze()" disabled>
                    ✨ Analyze Love Score
                </button>
            </center>
        </div>
        
        <div class="card loading" id="loading">
            <div class="spinner"></div>
            <p style="color: #e73c7e; font-size: 1.2em;">Analyzing... 💕</p>
        </div>
        
        <div id="errorDiv"></div>
        <div class="card results" id="results"></div>
    </div>
    
    <script>
        let file = null;
        
        document.getElementById('fileInput').onchange = function(e) {
            file = e.target.files[0];
            if (file) {
                document.querySelector('.upload-zone').innerHTML = 
                    '<div class="upload-icon">✅</div><h3>' + file.name + '</h3><p style="color: #28a745;">Ready to analyze!</p>';
                document.getElementById('analyzeBtn').disabled = false;
            }
        };
        
        async function analyze() {
            if (!file) return;
            
            document.getElementById('uploadCard').style.display = 'none';
            document.getElementById('loading').classList.add('show');
            document.getElementById('errorDiv').innerHTML = '';
            document.getElementById('results').classList.remove('show');
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (!response.ok || data.error) {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                showResults(data);
                
            } catch (error) {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('errorDiv').innerHTML = 
                    '<div class="alert">⚠️ ' + error.message + '</div>';
                document.getElementById('uploadCard').style.display = 'block';
            }
        }
        
        function showResults(data) {
            document.getElementById('loading').classList.remove('show');
            const results = document.getElementById('results');
            results.classList.add('show');
            
            let html = '<h2 style="text-align: center; color: #e73c7e; margin-bottom: 30px;">📊 Analysis Complete!</h2>';
            
            html += '<div class="stats-grid">';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_messages + '</div><div class="stat-label">💬 Messages</div></div>';
            html += '<div class="stat-card"><div class="stat-number">' + data.total_participants + '</div><div class="stat-label">👥 Participants</div></div>';
            html += '<div class="stat-card"><div class="stat-number">' + data.top_pairs.length + '</div><div class="stat-label">💕 Pairs</div></div>';
            html += '</div>';
            
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
            
            if (data.top_pairs.length > 1) {
                html += '<h3 style="color: #333; margin: 30px 0 20px;">📋 All Pairs (Ranked)</h3>';
                data.top_pairs.forEach((pair, i) => {
                    html += '<div class="pair-item"><span class="pair-rank">#' + (i+1) + '</span>';
                    html += '<span class="pair-names">' + pair.person1 + ' ↔ ' + pair.person2 + '</span>';
                    html += '<span class="pair-score">' + Math.round(pair.combined_score) + '</span></div>';
                });
            }
            
            html += '<center style="margin-top: 30px;"><button class="btn" onclick="location.reload()">🔄 Analyze Another</button></center>';
            
            results.innerHTML = html;
            
            setTimeout(() => {
                document.querySelectorAll('.progress-bar').forEach(bar => {
                    const w = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => bar.style.width = w, 100);
                });
            }, 200);
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
        
        print(f"\n{'='*60}")
        print(f"📂 Analyzing: {filename}")
        
        # Parse file
        with io.open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✓ Loaded {len(lines)} lines")
        
        chats = []
        previous_line = None
        
        for line in lines:
            chatline = Chatline(line=line, previous_line=previous_line, debug=False)
            if chatline.line_type == 'Chat' and chatline.sender and chatline.timestamp:
                chats.append({
                    'sender': chatline.sender,
                    'timestamp': chatline.timestamp
                })
            previous_line = chatline
        
        print(f"✓ Parsed {len(chats)} messages")
        
        if not chats:
            raise Exception("No valid messages found")
        
        # Get participants
        senders = {}
        for chat in chats:
            senders[chat['sender']] = senders.get(chat['sender'], 0) + 1
        
        print(f"✓ Found {len(senders)} participants")
        
        if len(senders) < 2:
            raise Exception("Need at least 2 participants")
        
        # Build reply patterns
        reply_data = defaultdict(list)
        for i in range(len(chats) - 1):
            current = chats[i]
            next_msg = chats[i + 1]
            if current['sender'] != next_msg['sender']:
                time_diff = (next_msg['timestamp'] - current['timestamp']).total_seconds() / 60
                if 0 < time_diff < 1440:
                    key = (next_msg['sender'], current['sender'])
                    reply_data[key].append(time_diff)
        
        print(f"✓ Found {len(reply_data)} reply patterns")
        
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
        
        if not all_pairs:
            raise Exception("No reply patterns found")
        
        all_pairs.sort(key=lambda x: x['combined_score'], reverse=True)
        print(f"✓ Calculated {len(all_pairs)} pair scores")
        
        def verdict(score):
            if score >= 80: return "💕 Strong Interest"
            elif score >= 60: return "💗 Moderate Interest"
            elif score >= 40: return "💛 Some Interest"
            else: return "💙 Low Interest"
        
        top = all_pairs[0]
        response = {
            'total_messages': len(chats),
            'total_participants': len(senders),
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
        
        print(f"✓ Top score: {response['top_pair']['combined_score']:.1f}")
        print(f"{'='*60}\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("💕 WhatsApp Love Score Analyzer - FINAL VERSION")
    print("="*80)
    print("\n🌐 Open: http://127.0.0.1:5001")
    print("📱 Upload chat → Click analyze → See results!")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=5001)
