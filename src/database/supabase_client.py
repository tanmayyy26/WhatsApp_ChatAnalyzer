"""
Supabase Client Configuration
Handles connection to Supabase database
"""

import os
from typing import Optional

try:
    from supabase import create_client, Client
except ImportError:
    Client = None

class SupabaseManager:
    """Manages Supabase connection and operations"""
    
    def __init__(self):
        """Initialize Supabase client with environment variables"""
        self.url = None
        self.key = None
        self.client: Optional[Client] = None
        self.connected = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Safely initialize the Supabase client"""
        try:
            # Get credentials from environment
            self.url = os.getenv("SUPABASE_URL", "").strip()
            self.key = os.getenv("SUPABASE_KEY", "").strip()
            
            # Validate credentials exist
            if not self.url or not self.key:
                print("⚠️  Supabase credentials not configured (optional)")
                return
            
            # Validate and sanitize URL
            if "http" not in self.url:
                self.url = f"https://{self.url}"
            
            # Validate URL format
            if not self.url.startswith("https://"):
                print("❌ Invalid Supabase URL format")
                return
            
            # Try to create client
            if Client is not None:
                try:
                    print(f"Attempting to connect to Supabase with URL: {self.url}")
                    self.client = create_client(self.url, self.key)
                    self.connected = True
                    print("✅ Supabase connected successfully!")
                except Exception as e:
                    print(f"⚠️  Supabase connection error: {str(e)}")
                    print("   App will work without cloud storage")
            else:
                print("⚠️  Supabase library not available (optional)")
                
        except Exception as e:
            print(f"⚠️  Error initializing Supabase: {str(e)}")
    
    def reconnect(self) -> bool:
        """Try to reconnect to Supabase"""
        self._initialize_client()
        return self.is_connected()
    
    def is_connected(self) -> bool:
        """Check if Supabase client is initialized and connected"""
        return self.client is not None and self.connected
    
    def save_file(self, filename: str, file_bytes: bytes) -> dict:
        """
        Save file to storage bucket 'char files'
        
        Args:
            filename: Name of uploaded file
            file_bytes: Raw file bytes
            
        Returns:
            Dict with status
        """
        if not self.is_connected():
            return {"error": "Supabase not connected"}
        
        try:
            from datetime import datetime
            import random
            
            # Create unique filename with timestamp and random number
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = random.randint(1000, 9999)
            storage_path = f"{timestamp}_{random_suffix}_{filename}"
            
            # Upload to storage bucket 'char files' with public access
            try:
                storage_response = self.client.storage.from_("char files").upload(
                    path=storage_path,
                    file=file_bytes,
                    file_options={
                        "content-type": "text/plain",
                        "cache-control": "3600",
                        "upsert": "true" 
                    }
                )
                
            except Exception as e:
                if "Name or service not known" in str(e):
                    error_message = (
                        "DNS resolution failed. Please verify the SUPABASE_URL. "
                        f"The hostname could not be resolved. URL: {self.url}"
                    )
                    return {"error": error_message}
                return {"error": f"Storage error: {e}"}

            # Check if upload was successful
            # The response can be an object with path attribute or a dict
            if storage_response:
                if hasattr(storage_response, 'path') or (isinstance(storage_response, dict) and "path" in storage_response):
                    return {"success": True, "path": storage_path}

            # Handle unexpected responses
            return {"error": f"Unknown storage response: {storage_response}"}

        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}

# Singleton instance for the app
supabase_manager = SupabaseManager()
