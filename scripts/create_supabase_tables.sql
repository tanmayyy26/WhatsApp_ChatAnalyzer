-- SQL Script to create tables in Supabase
-- Run this in Supabase SQL Editor (Database → SQL Editor)

-- Table 0: chat_files (File metadata)
-- Stores metadata for files uploaded to Supabase Storage
CREATE TABLE IF NOT EXISTS chat_files (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable Row Level Security for chat_files (for development)
ALTER TABLE chat_files DISABLE ROW LEVEL SECURITY;

-- Table 1: chat_uploads
-- Stores metadata about each chat file upload
CREATE TABLE IF NOT EXISTS chat_uploads (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    total_messages INTEGER NOT NULL,
    participant_count INTEGER NOT NULL,
    participants TEXT[] NOT NULL,
    date_start TIMESTAMP,
    date_end TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: chat_messages
-- Stores individual messages from uploaded chats
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    upload_id BIGINT NOT NULL REFERENCES chat_uploads(id) ON DELETE CASCADE,
    sender TEXT,
    message_body TEXT,
    timestamp TIMESTAMP,
    line_type TEXT DEFAULT 'Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 3: chat_analytics
-- Stores analytics data (love scores, statistics)
CREATE TABLE IF NOT EXISTS chat_analytics (
    id BIGSERIAL PRIMARY KEY,
    upload_id BIGINT NOT NULL REFERENCES chat_uploads(id) ON DELETE CASCADE,
    love_scores JSONB,
    top_senders JSONB,
    top_words JSONB,
    hourly_activity JSONB,
    daily_activity JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_upload_id ON chat_messages(upload_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON chat_messages(sender);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_analytics_upload_id ON chat_analytics(upload_id);
CREATE INDEX IF NOT EXISTS idx_chat_uploads_created_at ON chat_uploads(created_at DESC);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE chat_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_analytics ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public access (adjust based on your security needs)
-- WARNING: These policies allow anyone to read/write. Modify for production!

CREATE POLICY "Allow public read access on chat_uploads" 
    ON chat_uploads FOR SELECT 
    USING (true);

CREATE POLICY "Allow public insert on chat_uploads" 
    ON chat_uploads FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow public read access on chat_messages" 
    ON chat_messages FOR SELECT 
    USING (true);

CREATE POLICY "Allow public insert on chat_messages" 
    ON chat_messages FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow public read access on chat_analytics" 
    ON chat_analytics FOR SELECT 
    USING (true);

CREATE POLICY "Allow public insert on chat_analytics" 
    ON chat_analytics FOR INSERT 
    WITH CHECK (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers to auto-update updated_at
CREATE TRIGGER update_chat_uploads_updated_at 
    BEFORE UPDATE ON chat_uploads 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_analytics_updated_at 
    BEFORE UPDATE ON chat_analytics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Success message
SELECT 'Tables created successfully!' AS status;
