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
            
            # Validate URL format
            if not self.url.startswith("https://"):
                print("❌ Invalid Supabase URL format")
                return
            
            # Try to create client
            if Client is not None:
                try:
                    self.client = create_client(self.url, self.key)
                    self.connected = True
                    print("✅ Supabase connected successfully!")
                except Exception as e:
                    print(f"⚠️  Supabase connection error: {str(e)[:100]}")
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
                        "upsert": "false"
                    }
                )
                
                # Get public URL
                public_url = self.client.storage.from_("char files").get_public_url(storage_path)
                
                return {
                    "success": True,
                    "storage_path": storage_path,
                    "public_url": public_url,
                    "message": f"✅ File uploaded successfully!"
                }
                
            except Exception as storage_error:
                # More detailed error message
                error_msg = str(storage_error)
                if "already exists" in error_msg.lower():
                    return {"error": f"File already exists. Try again."}
                elif "bucket not found" in error_msg.lower():
                    return {"error": "Storage bucket 'char files' not found. Create it in Supabase dashboard."}
                elif "policy" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    return {"error": "Permission denied. Run FIX_STORAGE.sql in Supabase SQL Editor."}
                else:
                    return {"error": f"Storage error: {error_msg}"}
                
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def save_chat_upload(self, filename: str, total_messages: int, 
                         participants: list, date_range: dict) -> dict:
        """
        Save chat upload metadata to database
        
        Args:
            filename: Name of uploaded file
            total_messages: Total number of messages
            participants: List of participant names
            date_range: Dict with 'start' and 'end' dates
            
        Returns:
            Dict with upload_id and status
        """
        if not self.is_connected():
            return {"error": "Supabase not connected"}
        
        try:
            data = {
                "filename": filename,
                "total_messages": total_messages,
                "participant_count": len(participants),
                "participants": participants,
                "date_start": date_range.get("start"),
                "date_end": date_range.get("end"),
            }
            
            response = self.client.table("chat_uploads").insert(data).execute()
            
            if response.data:
                return {
                    "success": True,
                    "upload_id": response.data[0]["id"],
                    "message": "Chat data saved successfully!"
                }
            else:
                return {"error": "Failed to save data"}
                
        except Exception as e:
            return {"error": f"Error saving to database: {str(e)}"}
    
    def save_chat_messages(self, upload_id: int, messages: list) -> dict:
        """
        Save individual chat messages to database
        
        Args:
            upload_id: ID from chat_uploads table
            messages: List of message dicts with sender, body, timestamp
            
        Returns:
            Dict with status
        """
        if not self.is_connected():
            return {"error": "Supabase not connected"}
        
        try:
            # Prepare messages for batch insert
            message_data = []
            for msg in messages:
                message_data.append({
                    "upload_id": upload_id,
                    "sender": msg.get("sender"),
                    "message_body": msg.get("body"),
                    "timestamp": str(msg.get("timestamp")) if msg.get("timestamp") else None,
                    "line_type": msg.get("line_type", "Chat")
                })
            
            # Insert in batches of 1000 to avoid size limits
            batch_size = 1000
            for i in range(0, len(message_data), batch_size):
                batch = message_data[i:i + batch_size]
                self.client.table("chat_messages").insert(batch).execute()
            
            return {
                "success": True,
                "message": f"Saved {len(messages)} messages"
            }
            
        except Exception as e:
            return {"error": f"Error saving messages: {str(e)}"}
    
    def save_analytics(self, upload_id: int, analytics_data: dict) -> dict:
        """
        Save chat analytics to database
        
        Args:
            upload_id: ID from chat_uploads table
            analytics_data: Dict with love scores, top senders, top words, etc.
            
        Returns:
            Dict with status
        """
        if not self.is_connected():
            return {"error": "Supabase not connected"}
        
        try:
            data = {
                "upload_id": upload_id,
                "love_scores": analytics_data.get("love_scores", []),
                "top_senders": analytics_data.get("top_senders", {}),
                "top_words": analytics_data.get("top_words", {}),
                "hourly_activity": analytics_data.get("hourly_activity", {}),
                "daily_activity": analytics_data.get("daily_activity", {})
            }
            
            response = self.client.table("chat_analytics").insert(data).execute()
            
            if response.data:
                return {
                    "success": True,
                    "message": "Analytics saved successfully!"
                }
            else:
                return {"error": "Failed to save analytics"}
                
        except Exception as e:
            return {"error": f"Error saving analytics: {str(e)}"}
    
    def get_recent_uploads(self, limit: int = 10) -> list:
        """
        Get recent chat uploads
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of upload records
        """
        if not self.is_connected():
            return []
        
        try:
            response = self.client.table("chat_uploads")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error fetching uploads: {e}")
            return []
    
    def get_upload_details(self, upload_id: int) -> dict:
        """
        Get details of a specific upload with messages and analytics
        
        Args:
            upload_id: ID of the upload
            
        Returns:
            Dict with upload details, messages, and analytics
        """
        if not self.is_connected():
            return {}
        
        try:
            # Get upload metadata
            upload = self.client.table("chat_uploads")\
                .select("*")\
                .eq("id", upload_id)\
                .execute()
            
            # Get messages
            messages = self.client.table("chat_messages")\
                .select("*")\
                .eq("upload_id", upload_id)\
                .execute()
            
            # Get analytics
            analytics = self.client.table("chat_analytics")\
                .select("*")\
                .eq("upload_id", upload_id)\
                .execute()
            
            return {
                "upload": upload.data[0] if upload.data else None,
                "messages": messages.data if messages.data else [],
                "analytics": analytics.data[0] if analytics.data else None
            }
            
        except Exception as e:
            print(f"Error fetching upload details: {e}")
            return {}


# Global instance
supabase_manager = SupabaseManager()
