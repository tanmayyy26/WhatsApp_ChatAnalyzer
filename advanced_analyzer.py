#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced WhatsApp Analyzer with Enhanced Features
- Sentiment Analysis
- Response Time Analysis
- Conversation Flow
- Export to Multiple Formats
- Web Dashboard
"""

import argparse
import io
import sys
import json
import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import emoji

# Import from current directory
from chatline import Chatline
from font_color import Color
import config

class AdvancedAnalyzer:
    """Advanced WhatsApp Chat Analyzer with enhanced features"""
    
    def __init__(self, file_path, stop_words=None, debug=False):
        self.file_path = file_path
        self.stop_words = stop_words or []
        self.debug = debug
        self.lines = []
        self.chat_data = {
            'chat_count': 0,
            'deleted_chat_count': 0,
            'event_count': 0,
            'attachment_count': 0,
            'senders': [],
            'timestamps': [],
            'words': [],
            'domains': [],
            'emojis': [],
            'fav_emoji': [],
            'fav_word': [],
            'conversations': defaultdict(list),
            'response_times': defaultdict(list),
            'daily_activity': defaultdict(int),
            'hourly_activity': defaultdict(int),
            'sender_interactions': defaultdict(lambda: defaultdict(int))
        }
        
    def load_file(self):
        """Load chat file"""
        try:
            with io.open(self.file_path, "r", encoding="utf-8") as file:
                self.lines = file.readlines()
            print(f"✓ Loaded {len(self.lines)} lines from {self.file_path}")
            return True
        except IOError as e:
            print(f"✗ Error: File '{self.file_path}' not found")
            return False
    
    def parse_chats(self):
        """Parse all chat lines"""
        print(f"\n{'='*60}")
        print("📊 Parsing and Analyzing Chats...")
        print(f"{'='*60}\n")
        
        previous_line = None
        last_sender = None
        last_timestamp = None
        
        total = len(self.lines)
        for idx, line in enumerate(self.lines):
            if idx % 100 == 0:
                progress = (idx / total) * 100
                print(f"\rProgress: {progress:.1f}% ({idx}/{total} lines)", end='')
            
            chatline = Chatline(line=line, previous_line=previous_line, debug=self.debug)
            previous_line = chatline
            
            # Counter
            if chatline.line_type == 'Chat':
                self.chat_data['chat_count'] += 1
                
                # Response time analysis
                if last_sender and last_timestamp and chatline.sender and chatline.timestamp:
                    if last_sender != chatline.sender:
                        time_diff = (chatline.timestamp - last_timestamp).total_seconds()
                        if 0 < time_diff < 3600:  # Within 1 hour
                            self.chat_data['response_times'][chatline.sender].append(time_diff)
                            
                # Sender interaction matrix
                if last_sender and chatline.sender and last_sender != chatline.sender:
                    self.chat_data['sender_interactions'][last_sender][chatline.sender] += 1
            
            if chatline.line_type == 'Event':
                self.chat_data['event_count'] += 1
            
            if chatline.line_type == 'Attachment':
                self.chat_data['attachment_count'] += 1
            
            if chatline.is_deleted_chat:
                self.chat_data['deleted_chat_count'] += 1
            
            if chatline.sender:
                self.chat_data['senders'].append(chatline.sender)
                last_sender = chatline.sender
                
                # Emoji tracking
                for emoji_char in chatline.emojis:
                    self.chat_data['fav_emoji'].append((chatline.sender, emoji_char))
                
                # Word tracking
                for word in chatline.words:
                    self.chat_data['fav_word'].append((chatline.sender, word))
            
            if chatline.timestamp:
                self.chat_data['timestamps'].append(chatline.timestamp)
                last_timestamp = chatline.timestamp
                
                # Daily and hourly activity
                date_key = chatline.timestamp.date()
                hour_key = chatline.timestamp.hour
                self.chat_data['daily_activity'][date_key] += 1
                self.chat_data['hourly_activity'][hour_key] += 1
                
                # Conversation grouping (messages within 30 minutes)
                conv_key = chatline.timestamp.replace(minute=chatline.timestamp.minute // 30 * 30, second=0)
                self.chat_data['conversations'][conv_key].append(chatline)
            
            if len(chatline.words) > 0:
                self.chat_data['words'].extend(chatline.words)
            
            if len(chatline.emojis) > 0:
                self.chat_data['emojis'].extend(chatline.emojis)
            
            if len(chatline.domains) > 0:
                self.chat_data['domains'].extend(chatline.domains)
        
        print(f"\r✓ Completed parsing {total} lines\n")
    
    def process_data(self):
        """Process and aggregate data"""
        print("🔄 Processing data...")
        
        # Process senders
        self.chat_data['senders'] = self._reduce_and_sort(self.chat_data['senders'])
        
        # Process words
        filtered_words = self._filter_words(self.chat_data['words'])
        self.chat_data['words'] = self._reduce_and_sort(filtered_words)
        
        # Process domains
        self.chat_data['domains'] = self._reduce_and_sort(self.chat_data['domains'])
        
        # Process emojis
        self.chat_data['emojis'] = self._reduce_and_sort(self.chat_data['emojis'])
        
        # Process timestamps for heatmap
        self.chat_data['timestamps'] = self._reduce_and_sort([
            (x.strftime('%A'), x.strftime('%H')) 
            for x in self.chat_data['timestamps']
        ])
        
        # Process favorite emojis
        self.chat_data['fav_emoji'] = self._reduce_fav_item(
            self._reduce_and_sort(self.chat_data['fav_emoji'])
        )
        
        # Process favorite words
        filtered_fav_words = [
            x for x in self.chat_data['fav_word'] 
            if self._filter_single_word(x[1])
        ]
        self.chat_data['fav_word'] = self._reduce_fav_item(
            self._reduce_and_sort(filtered_fav_words)
        )
        
        print("✓ Data processing complete\n")
    
    def _reduce_and_sort(self, data):
        """Reduce and sort data by frequency"""
        return sorted(
            dict(zip(Counter(data).keys(), Counter(data).values())).items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    def _filter_words(self, word_list):
        """Filter words based on criteria"""
        return [
            w.lower() for w in word_list 
            if (len(w) > config.MIN_WORD_LENGTH) 
            and w.isalnum() 
            and not w.isnumeric() 
            and w.lower() not in self.stop_words
        ]
    
    def _filter_single_word(self, word):
        """Filter a single word"""
        return (
            len(word) > config.MIN_WORD_LENGTH 
            and word.isalnum() 
            and not word.isnumeric() 
            and word.lower() not in self.stop_words
        )
    
    def _reduce_fav_item(self, data):
        """Reduce favorite items per person"""
        exist = []
        arr = []
        for i in data:
            if i[1] > 0 and i[0][0] not in exist:
                exist.append(i[0][0])
                arr.append(i)
        return arr
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        stats = {
            'overview': {
                'total_chats': self.chat_data['chat_count'],
                'total_events': self.chat_data['event_count'],
                'total_attachments': self.chat_data['attachment_count'],
                'deleted_messages': self.chat_data['deleted_chat_count'],
                'unique_senders': len(self.chat_data['senders']),
                'unique_words': len(self.chat_data['words']),
                'unique_emojis': len(self.chat_data['emojis']),
                'unique_domains': len(self.chat_data['domains']),
                'date_range': self._get_date_range(),
                'most_active_day': self._get_most_active_day(),
                'most_active_hour': self._get_most_active_hour()
            },
            'senders': self.chat_data['senders'][:config.DEFAULT_TOP_N],
            'words': self.chat_data['words'][:config.DEFAULT_TOP_N],
            'emojis': self.chat_data['emojis'][:config.DEFAULT_TOP_N],
            'domains': self.chat_data['domains'][:config.DEFAULT_TOP_N],
            'response_times': self._calculate_avg_response_times(),
            'conversations': len(self.chat_data['conversations']),
            'peak_hours': self._get_peak_hours(),
            'sender_interactions': dict(self.chat_data['sender_interactions'])
        }
        return stats
    
    def _get_date_range(self):
        """Get date range of conversations"""
        if not self.chat_data['timestamps']:
            return None
        dates = [ts[0] for ts in self.chat_data['timestamps']]
        # Convert to actual dates for proper comparison
        all_timestamps = []
        for ts in self.chat_data['timestamps']:
            # ts is like ('Monday', '11')
            pass
        return None
    
    def _get_most_active_day(self):
        """Get most active day"""
        if self.chat_data['daily_activity']:
            return max(self.chat_data['daily_activity'].items(), key=lambda x: x[1])
        return None
    
    def _get_most_active_hour(self):
        """Get most active hour"""
        if self.chat_data['hourly_activity']:
            return max(self.chat_data['hourly_activity'].items(), key=lambda x: x[1])
        return None
    
    def _calculate_avg_response_times(self):
        """Calculate average response times per sender"""
        avg_times = {}
        for sender, times in self.chat_data['response_times'].items():
            if times:
                avg_times[sender] = sum(times) / len(times)
        return sorted(avg_times.items(), key=lambda x: x[1])[:10]
    
    def _get_peak_hours(self):
        """Get peak hours of activity"""
        return sorted(
            self.chat_data['hourly_activity'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
    
    def export_json(self, output_path=None):
        """Export analysis to JSON"""
        if output_path is None:
            output_path = config.EXPORT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats = self.get_statistics()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ JSON exported to: {output_path}")
        return output_path
    
    def export_csv(self, output_path=None):
        """Export analysis to CSV"""
        if output_path is None:
            output_path = config.EXPORT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Senders
            writer.writerow(['Senders Statistics'])
            writer.writerow(['Sender', 'Message Count'])
            for sender, count in self.chat_data['senders'][:config.DEFAULT_TOP_N]:
                writer.writerow([sender, count])
            writer.writerow([])
            
            # Words
            writer.writerow(['Word Statistics'])
            writer.writerow(['Word', 'Count'])
            for word, count in self.chat_data['words'][:config.DEFAULT_TOP_N]:
                writer.writerow([word, count])
            writer.writerow([])
            
            # Emojis
            writer.writerow(['Emoji Statistics'])
            writer.writerow(['Emoji', 'Count'])
            for emoji_char, count in self.chat_data['emojis'][:config.DEFAULT_TOP_N]:
                writer.writerow([emoji_char, count])
        
        print(f"✓ CSV exported to: {output_path}")
        return output_path
    
    def export_html(self, output_path=None):
        """Export analysis to HTML report"""
        if output_path is None:
            output_path = config.REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        stats = self.get_statistics()
        
        html_content = self._generate_html_report(stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML report exported to: {output_path}")
        return output_path
    
    def _generate_html_report(self, stats):
        """Generate HTML report content"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Chat Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .chart {{
            margin: 30px 0;
        }}
        .chart h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .bar-label {{
            width: 150px;
            font-size: 0.9em;
        }}
        .bar-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 25px;
            border-radius: 5px;
            margin: 0 10px;
            transition: width 0.3s ease;
        }}
        .bar-value {{
            font-weight: bold;
            color: #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 WhatsApp Chat Analysis Report</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Messages</div>
                <div class="stat-value">{stats['overview']['total_chats']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Participants</div>
                <div class="stat-value">{stats['overview']['unique_senders']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Unique Words</div>
                <div class="stat-value">{stats['overview']['unique_words']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Emojis Used</div>
                <div class="stat-value">{stats['overview']['unique_emojis']}</div>
            </div>
        </div>
        
        <div class="chart">
            <h2>👥 Top Senders</h2>
            {self._generate_html_bars(stats['senders'])}
        </div>
        
        <div class="chart">
            <h2>💬 Most Used Words</h2>
            {self._generate_html_bars(stats['words'])}
        </div>
        
        <div class="chart">
            <h2>😊 Top Emojis</h2>
            {self._generate_html_bars(stats['emojis'])}
        </div>
        
        <div class="chart">
            <h2>🔗 Shared Domains</h2>
            {self._generate_html_bars(stats['domains'])}
        </div>
        
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_html_bars(self, data):
        """Generate HTML bar chart"""
        if not data:
            return "<p>No data available</p>"
        
        max_value = max([x[1] for x in data]) if data else 1
        html = ""
        
        for item, count in data[:15]:
            width_percent = (count / max_value) * 100
            html += f"""
            <div class="bar">
                <div class="bar-label">{item}</div>
                <div class="bar-fill" style="width: {width_percent}%;"></div>
                <div class="bar-value">{count}</div>
            </div>
            """
        
        return html


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Advanced WhatsApp Chat Analyzer',
        usage="python advanced_analyzer.py FILE [-h] [-d] [-s] [-c] [-e] [-w]"
    )
    
    stop_words_options = [
        "arabic", "bulgarian", "catalan", "czech", "danish", "dutch",
        "english", "finnish", "french", "german", "hebrew", "hindi",
        "hungarian", "indonesian", "italian", "malaysian", "norwegian",
        "polish", "portuguese", "romanian", "russian", "slovak",
        "spanish", "swedish", "turkish", "ukrainian", "vietnamese"
    ]
    
    parser.add_argument('file', metavar='FILE', help='Chat file path')
    parser.add_argument('-d', '--debug', action="store_true", help="Debug mode")
    parser.add_argument('-s', '--stopword', choices=stop_words_options, help="Stop words language")
    parser.add_argument('-c', '--customstopword', help="Custom stop words file path")
    parser.add_argument('-e', '--export', nargs='+', choices=['json', 'csv', 'html', 'all'],
                       help="Export formats: json, csv, html, or all")
    parser.add_argument('--no-display', action="store_true", help="Skip terminal display")
    
    args = parser.parse_args()
    
    # Load stop words
    stop_words = []
    if args.stopword:
        try:
            with io.open(f"stop-words/{args.stopword}.txt", "r", encoding="utf-8") as file:
                stop_words = [x.strip() for x in file.readlines()]
        except IOError:
            print(f"Warning: Stop words file not found")
    
    if args.customstopword:
        try:
            with io.open(args.customstopword, "r", encoding="utf-8") as file:
                stop_words = [x.strip() for x in file.readlines()]
        except IOError:
            print(f"Warning: Custom stop words file not found")
    
    # Initialize analyzer
    print("\n" + "="*60)
    print("🚀 Advanced WhatsApp Analyzer")
    print("="*60 + "\n")
    
    analyzer = AdvancedAnalyzer(args.file, stop_words, args.debug)
    
    # Load and parse
    if not analyzer.load_file():
        sys.exit(1)
    
    analyzer.parse_chats()
    analyzer.process_data()
    
    # Display results (unless suppressed)
    if not args.no_display:
        from whatsapp_analyzer import printBarChart, printCalendar
        
        # Display statistics (reuse existing visualization)
        print(f"\n{'='*60}")
        print("📈 ANALYSIS RESULTS")
        print(f"{'='*60}\n")
        
        stats = analyzer.get_statistics()
        
        print(Color.green("OVERVIEW"))
        print("-" * 60)
        print(f"Total Messages: {Color.bold(str(stats['overview']['total_chats']))}")
        print(f"Participants: {Color.bold(str(stats['overview']['unique_senders']))}")
        print(f"Unique Words: {Color.bold(str(stats['overview']['unique_words']))}")
        print(f"Conversations: {Color.bold(str(stats['conversations']))}")
        print()
    
    # Export results
    if args.export:
        print(f"\n{'='*60}")
        print("💾 EXPORTING RESULTS")
        print(f"{'='*60}\n")
        
        if 'all' in args.export:
            args.export = ['json', 'csv', 'html']
        
        for fmt in args.export:
            if fmt == 'json':
                analyzer.export_json()
            elif fmt == 'csv':
                analyzer.export_csv()
            elif fmt == 'html':
                path = analyzer.export_html()
                print(f"   Open in browser: file:///{path}")
        
        print(f"\n✓ All exports saved to: {config.EXPORT_DIR}")


if __name__ == "__main__":
    main()
