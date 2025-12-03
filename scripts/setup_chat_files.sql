-- Complete SQL setup for chat_files table
-- Run this entire script in Supabase SQL Editor

-- Drop table if exists to start fresh
DROP TABLE IF EXISTS chat_files CASCADE;

-- Create the chat_files table
CREATE TABLE chat_files (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable Row Level Security (for development/testing)
ALTER TABLE chat_files DISABLE ROW LEVEL SECURITY;

-- Grant access to authenticated and anonymous users
GRANT ALL ON chat_files TO postgres, anon, authenticated, service_role;
GRANT ALL ON SEQUENCE chat_files_id_seq TO postgres, anon, authenticated, service_role;

-- Verify table was created
SELECT 'Table chat_files created successfully!' as status;
