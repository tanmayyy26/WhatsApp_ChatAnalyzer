#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Configuration Module for WhatsApp Analyzer
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
STOP_WORDS_DIR = BASE_DIR / "stop-words"
EXPORT_DIR = BASE_DIR / "exports"
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
for directory in [EXPORT_DIR, REPORTS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Analysis settings
DEFAULT_TOP_N = 20  # Number of top items to show in charts
MIN_WORD_LENGTH = 2
MAX_VISUALIZATION_ITEMS = 50

# Chart settings
CHART_WIDTH = 50
CHART_FILL_CHARS = {
    'default': '█',
    'light': '░',
    'medium': '▒',
    'heavy': '▓'
}

# Color schemes
COLOR_SCHEMES = {
    'default': {
        'sender': 'red',
        'domain': 'blue',
        'emoji': 'orange',
        'word': 'green',
        'heatmap': 'purple'
    }
}

# Export formats
EXPORT_FORMATS = ['json', 'csv', 'html', 'pdf']

# Database settings
DATABASE_ENABLED = False
DATABASE_PATH = DATA_DIR / "analytics.db"

# Web dashboard settings
WEB_DASHBOARD_ENABLED = True
WEB_HOST = '127.0.0.1'
WEB_PORT = 5000
WEB_DEBUG = True

# Sentiment analysis settings
SENTIMENT_ENABLED = True
SENTIMENT_LANGUAGES = ['en', 'id']

# Performance settings
ENABLE_CACHING = True
CACHE_SIZE = 1000
PARALLEL_PROCESSING = True
MAX_WORKERS = 4

# Privacy settings
ANONYMIZE_NUMBERS = True
ANONYMIZE_NAMES = False
MASK_PATTERN = 'xxx'

# Advanced analytics
RESPONSE_TIME_ANALYSIS = True
CONVERSATION_FLOW_ANALYSIS = True
PEAK_HOURS_ANALYSIS = True
DAILY_PATTERNS_ANALYSIS = True
WEEKLY_PATTERNS_ANALYSIS = True

# Notification settings
ENABLE_NOTIFICATIONS = False
NOTIFICATION_EMAIL = None

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'analyzer.log'
