# 🚀 Supabase Integration Setup Guide

## ✅ What's Been Created:

### 1. **Files Created:**
- ✅ `supabase_client.py` - Python client for Supabase operations
- ✅ `create_supabase_tables.sql` - SQL script to create database tables
- ✅ `.env` - Environment configuration file
- ✅ `.env.example` - Example environment file
- ✅ `simple_streamlit.py` - Updated with Supabase integration

### 2. **Dependencies Installed:**
- ✅ `supabase` - Supabase Python client
- ✅ `python-dotenv` - Environment variable management

---

## 📋 Setup Steps:

### Step 1: Get Your Supabase API Key

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Open your project: `ojusbxunwfnqisoqmxbf`
3. Click **Project Settings** (gear icon)
4. Go to **API** section
5. Copy the **`anon` `public`** key (starts with `eyJh...`)

### Step 2: Update .env File

1. Open the `.env` file in your project
2. Replace `YOUR_ANON_KEY_HERE` with your actual Supabase key:

```env
SUPABASE_URL=https://ojusbxunwfnqisoqmxbf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_ACTUAL_KEY_HERE
```

### Step 3: Create Database Tables

1. Go to [https://supabase.com/dashboard/project/ojusbxunwfnqisoqmxbf/sql/new](https://supabase.com/dashboard/project/ojusbxunwfnqisoqmxbf/sql/new)
2. Copy ALL content from `create_supabase_tables.sql`
3. Paste it into the SQL Editor
4. Click **Run** button
5. You should see: "Tables created successfully!"

### Step 4: Verify Tables Were Created

1. Go to **Table Editor** in Supabase dashboard
2. You should see 3 new tables:
   - ✅ `chat_uploads` - Stores upload metadata
   - ✅ `chat_messages` - Stores individual messages
   - ✅ `chat_analytics` - Stores analysis results

### Step 5: Run Your App

```powershell
cd "C:\Users\Lenovo\OneDrive\Desktop\examples\same lov\WhatsApp-Analyzer"
python -m streamlit run simple_streamlit.py --server.port=8504
```

---

## 🎯 Features Now Available:

### 1. **Upload & Save**
- Upload WhatsApp chat file
- Analyze messages locally
- Click **"💾 Save Analysis to Supabase"** button
- Data is saved to cloud database

### 2. **View Saved Data**
- Sidebar shows **"📚 Recent Uploads"**
- See your last 5 uploaded chats
- View metadata (filename, message count, dates)

### 3. **Data Stored:**

**chat_uploads table:**
- Filename
- Total messages
- Participant count
- List of participants
- Date range (start/end)
- Upload timestamp

**chat_messages table:**
- Sender name
- Message body
- Timestamp
- Message type (Chat/Event/Attachment)
- Linked to upload via `upload_id`

**chat_analytics table:**
- Love scores between participants
- Top 10 senders with message counts
- Top 50 words with frequencies
- Hourly activity patterns
- Daily activity patterns
- Linked to upload via `upload_id`

---

## 🔒 Security Notes:

### Current Setup (Development):
- ⚠️ **Public access enabled** - Anyone with the URL can read/write
- ✅ Good for: Testing, demos, personal projects
- ❌ Not recommended for: Production, sensitive data

### To Secure for Production:

1. **Enable Authentication:**
   ```sql
   -- Update RLS policies to require authentication
   ALTER POLICY "Allow public read access on chat_uploads" 
   ON chat_uploads 
   USING (auth.uid() IS NOT NULL);
   ```

2. **Add User-Specific Access:**
   - Add `user_id` column to `chat_uploads`
   - Link uploads to specific users
   - Update RLS policies to filter by `user_id`

3. **Use Service Role Key for Admin:**
   - Store `service_role` key securely
   - Use only for admin operations
   - Never expose in frontend code

---

## 🧪 Testing:

### Test the Integration:

1. **Upload a chat file** in the app
2. Check **"💾 Save analysis to database"** checkbox
3. Click **"💾 Save Analysis to Supabase"** button
4. You should see success messages:
   - ✅ Upload metadata saved! ID: X
   - ✅ Saved X messages
   - ✅ Analytics saved!
5. Go to Supabase dashboard → Table Editor
6. Check `chat_uploads` table - you should see your upload
7. Check `chat_messages` table - you should see messages
8. Check `chat_analytics` table - you should see analytics

### View Saved Data:

1. Look at sidebar **"📚 Recent Uploads"**
2. You should see your uploaded file
3. Click to expand and view details

---

## 🐛 Troubleshooting:

### "⚠️ Supabase Not Connected"
**Problem:** API key not set or invalid

**Solution:**
1. Check `.env` file exists
2. Verify `SUPABASE_KEY` is set correctly
3. Make sure key starts with `eyJh...`
4. Restart the Streamlit app

### "Failed to save data"
**Problem:** Tables don't exist or RLS policies blocking

**Solution:**
1. Run the SQL script in Supabase SQL Editor
2. Check RLS policies allow inserts
3. Verify tables exist in Table Editor

### "Error saving to database: X"
**Problem:** Database connection or data format issue

**Solution:**
1. Check Supabase dashboard is accessible
2. Verify internet connection
3. Check error message for specific details
4. Look at browser console for more info

---

## 📊 Database Schema Diagram:

```
chat_uploads (parent)
├── id (primary key)
├── filename
├── total_messages
├── participant_count
├── participants[]
├── date_start
├── date_end
└── created_at

chat_messages (child)
├── id (primary key)
├── upload_id (foreign key → chat_uploads.id)
├── sender
├── message_body
├── timestamp
└── line_type

chat_analytics (child)
├── id (primary key)
├── upload_id (foreign key → chat_uploads.id)
├── love_scores (JSON)
├── top_senders (JSON)
├── top_words (JSON)
├── hourly_activity (JSON)
└── daily_activity (JSON)
```

---

## 🎉 You're All Set!

Your WhatsApp Analyzer now has **cloud storage** powered by Supabase!

**Next Steps:**
1. Add your Supabase API key to `.env`
2. Run the SQL script to create tables
3. Start analyzing and saving chats!

**Need Help?**
- Check Supabase docs: https://supabase.com/docs
- Check error messages in the app
- Verify tables exist in Supabase dashboard
