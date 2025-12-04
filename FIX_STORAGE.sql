-- ============================================
-- COMPLETE FIX FOR SUPABASE STORAGE
-- Run this ENTIRE script in Supabase SQL Editor
-- ============================================

-- Step 1: Check if storage bucket exists
-- Go to: Storage > Buckets and verify "char files" bucket exists
-- If not, create it with these settings:
--   Name: char files
--   Public: YES (check the box)
--   File size limit: 50MB
--   Allowed MIME types: text/plain

-- Step 2: Set storage bucket to PUBLIC
-- This SQL makes the bucket publicly accessible
UPDATE storage.buckets 
SET public = true 
WHERE name = 'char files';

-- Step 3: Create storage policies for the bucket
-- This allows anyone to upload and read files

-- Delete existing policies first
DROP POLICY IF EXISTS "Anyone can upload to char files" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can read from char files" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can update in char files" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can delete from char files" ON storage.objects;

-- Allow anyone to upload files to 'char files' bucket
CREATE POLICY "Anyone can upload to char files"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'char files');

-- Allow anyone to read files from 'char files' bucket
CREATE POLICY "Anyone can read from char files"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'char files');

-- Allow anyone to update files in 'char files' bucket
CREATE POLICY "Anyone can update in char files"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'char files');

-- Allow anyone to delete files in 'char files' bucket
CREATE POLICY "Anyone can delete from char files"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'char files');

-- Step 4: Verify the setup
SELECT 'Storage policies created successfully!' as status;

-- To verify bucket is public, run:
SELECT name, public FROM storage.buckets WHERE name = 'char files';
