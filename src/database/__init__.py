"""Database package initialization"""
# Lazy import to avoid initialization errors on startup
# Import supabase_manager only when needed

__all__ = ['supabase_manager']

def __getattr__(name):
    if name == 'supabase_manager':
        from .supabase_client import supabase_manager
        return supabase_manager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
