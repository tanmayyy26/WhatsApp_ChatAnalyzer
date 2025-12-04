"""Analyzer package initialization"""
# Lazy imports to avoid initialization errors

__all__ = ['Chatline', 'ReplyAnalyzer']

def __getattr__(name):
    if name == 'Chatline':
        from .chatline import Chatline
        return Chatline
    elif name == 'ReplyAnalyzer':
        from .reply_analyzer import ReplyAnalyzer
        return ReplyAnalyzer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
