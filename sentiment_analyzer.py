#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sentiment Analysis Module for WhatsApp Analyzer
Analyzes emotional tone and sentiment of messages
"""

import re
from collections import Counter

class SentimentAnalyzer:
    """Simple rule-based sentiment analyzer"""
    
    def __init__(self, language='en'):
        self.language = language
        self.sentiment_words = self._load_sentiment_words()
    
    def _load_sentiment_words(self):
        """Load sentiment word dictionaries"""
        # Basic sentiment lexicon (expandable)
        sentiments = {
            'en': {
                'positive': [
                    'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful',
                    'fantastic', 'love', 'happy', 'joy', 'best', 'perfect',
                    'beautiful', 'brilliant', 'glad', 'pleased', 'excited',
                    'thanks', 'thank', 'appreciate', 'nice', 'cool', 'super',
                    '😊', '😄', '😃', '❤️', '👍', '🎉', '✨', '👏', '💯', '🔥'
                ],
                'negative': [
                    'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst',
                    'sad', 'angry', 'disappointed', 'annoying', 'stupid',
                    'wrong', 'problem', 'issue', 'difficult', 'hard',
                    'sorry', 'unfortunately', 'failure', 'fail', 'poor',
                    '😢', '😭', '😠', '😡', '💔', '👎', '😞', '😔', '😟'
                ]
            },
            'id': {
                'positive': [
                    'bagus', 'baik', 'senang', 'suka', 'mantap', 'keren',
                    'hebat', 'sempurna', 'terima kasih', 'thanks', 'makasih',
                    'gembira', 'bahagia', 'indah', 'cantik', 'lucu',
                    '😊', '😄', '😃', '❤️', '👍', '🎉', '✨', '👏', '💯', '🔥'
                ],
                'negative': [
                    'jelek', 'buruk', 'sedih', 'marah', 'kecewa', 'benci',
                    'susah', 'sulit', 'masalah', 'problem', 'salah', 'gagal',
                    'bodoh', 'parah', 'maaf', 'sayangnya', 'aneh',
                    '😢', '😭', '😠', '😡', '💔', '👎', '😞', '😔', '😟'
                ]
            }
        }
        
        return sentiments.get(self.language, sentiments['en'])
    
    def analyze_text(self, text):
        """Analyze sentiment of a text"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = 0
        negative_count = 0
        
        # Check words
        for word in words:
            if word in self.sentiment_words['positive']:
                positive_count += 1
            elif word in self.sentiment_words['negative']:
                negative_count += 1
        
        # Check emojis in original text
        for emoji_char in text:
            if emoji_char in self.sentiment_words['positive']:
                positive_count += 1
            elif emoji_char in self.sentiment_words['negative']:
                negative_count += 1
        
        # Calculate sentiment
        total = positive_count + negative_count
        
        if total == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        score = (positive_count - negative_count) / total
        confidence = total / len(words) if words else 0
        
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': min(confidence, 1.0),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def analyze_conversation(self, messages):
        """Analyze sentiment of entire conversation"""
        sentiments = []
        
        for msg in messages:
            if hasattr(msg, 'body') and msg.body:
                result = self.analyze_text(msg.body)
                if msg.sender:
                    result['sender'] = msg.sender
                    result['timestamp'] = msg.timestamp
                sentiments.append(result)
        
        return sentiments
    
    def get_sender_sentiment(self, sentiments):
        """Get overall sentiment per sender"""
        sender_sentiments = {}
        
        for sent in sentiments:
            if 'sender' not in sent:
                continue
            
            sender = sent['sender']
            if sender not in sender_sentiments:
                sender_sentiments[sender] = {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total': 0,
                    'avg_score': 0
                }
            
            sender_sentiments[sender][sent['sentiment']] += 1
            sender_sentiments[sender]['total'] += 1
            sender_sentiments[sender]['avg_score'] += sent['score']
        
        # Calculate averages
        for sender in sender_sentiments:
            total = sender_sentiments[sender]['total']
            if total > 0:
                sender_sentiments[sender]['avg_score'] /= total
                sender_sentiments[sender]['positive_ratio'] = \
                    sender_sentiments[sender]['positive'] / total
                sender_sentiments[sender]['negative_ratio'] = \
                    sender_sentiments[sender]['negative'] / total
        
        return sender_sentiments
    
    def get_sentiment_timeline(self, sentiments):
        """Get sentiment changes over time"""
        timeline = []
        
        for sent in sentiments:
            if 'timestamp' in sent and sent['timestamp']:
                timeline.append({
                    'timestamp': sent['timestamp'],
                    'sentiment': sent['sentiment'],
                    'score': sent['score']
                })
        
        return sorted(timeline, key=lambda x: x['timestamp'])
