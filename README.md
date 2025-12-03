# 💬 WhatsApp Chat Analyzer

A powerful web application to analyze your WhatsApp chat exports with beautiful visualizations and insights.

## 🚀 Quick Start

### Local Development

#### Step 1: Install Python
Make sure you have Python 3.8 or higher installed on your computer.
- Download from: https://www.python.org/downloads/

#### Step 2: Setup Project

1. **Open the project folder** in your terminal/command prompt:
   ```bash
   cd "c:\Users\Lenovo\OneDrive\Desktop\examples\same lov\WhatsApp-Analyzer"
   ```

2. **Run the startup script** (easiest way):
   - **Windows**: Double-click `start.bat`
   
   OR manually:
   
3. **Activate virtual environment**:
   ```bash
   .venv\Scripts\activate
   ```

4. **Install dependencies** (first time only):
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the application**:
   ```bash
   streamlit run app.py --server.port 8504
   ```

6. **Open your browser** at: `http://localhost:8504`

### ☁️ Cloud Deployment (Free!)

Want to share your analyzer with friends? Deploy to **Streamlit Cloud** for **free**!

#### Quick Deploy Steps:

1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Sign in with GitHub** (or create account)
3. **Click "New app"**
4. **Select your repository**: `tanmayyy26/WhatsApp_ChatAnalyzer`
5. **Select branch**: `main`
6. **Select main file**: `app.py`
7. **Click "Deploy"** → Your app will be live in 2-3 minutes!

**Your app URL**: `https://your-app-name.streamlit.app`

✨ **No server costs, no configuration needed!**

For detailed deployment guide, see: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📱 How to Export Your WhatsApp Chat

### On Android:
1. Open WhatsApp and go to the chat you want to analyze
2. Tap the **⋮** (three dots) in the top right corner
3. Select **More** → **Export chat**
4. Choose **Without Media**
5. Save the `.txt` file

### On iPhone:
1. Open WhatsApp and go to the chat you want to analyze
2. Tap the contact/group name at the top
3. Scroll down and tap **Export Chat**
4. Choose **Without Media**
5. Save the `.txt` file

## 📊 Features

Once you upload your chat file, you'll get:

✅ **Message Statistics**
- Total messages count
- Number of participants
- Chat duration
- Average messages per day

✅ **Top Contributors**
- Bar chart showing who sends the most messages
- Percentage breakdown by sender
- Visual rankings

✅ **Word Cloud**
- Beautiful visualization of most used words
- Filtered to remove common words
- Top 20 words table

✅ **Activity Analysis**
- Daily message trends over time
- Hourly activity patterns (when you chat most)
- Day of week distribution (which days are busiest)

✅ **Love Score**
- Engagement metrics between participants
- Reply speed analysis
- Interaction quality scoring

✅ **Calendar Heatmap**
- Visual representation of chat activity
- See your most and least active periods

✅ **Automatic Cloud Backup**
- Files automatically saved to cloud storage
- Secure and private

## 🎯 Usage Instructions

1. **Launch the app** using `start.bat` or the command above
2. **Click "Browse files"** in the sidebar
3. **Select your exported WhatsApp chat** (.txt file)
4. **Wait a few seconds** for analysis to complete
5. **Explore the visualizations** by scrolling down
6. **View different metrics** across multiple charts

## 🔧 Troubleshooting

### App won't start?
- Make sure Python is installed
- Check that virtual environment is activated
- Try reinstalling dependencies: `pip install -r requirements.txt`

### File upload not working?
- Make sure your file is a `.txt` file
- Verify it's a proper WhatsApp export (has dates and timestamps)
- Try a different chat export

### Charts not showing?
- Refresh the page
- Check your internet connection (for some visualizations)
- Make sure the chat file has enough messages (at least 10)

## 📁 Project Structure

```
WhatsApp-Analyzer/
├── app.py              # Main application (run this)
├── start.bat           # Windows startup script
├── requirements.txt    # Python dependencies
├── .env               # Configuration (don't share!)
└── src/               # Source code
    ├── analyzers/     # Chat parsing logic
    ├── database/      # Cloud storage
    └── utils/         # Helper functions
```

## 🔒 Privacy & Security

- ✅ All analysis happens **locally on your computer**
- ✅ Chat files are only uploaded to **your own cloud storage**
- ✅ No data is shared with third parties
- ✅ You can delete uploaded files anytime from your Supabase dashboard

## 💡 Tips

- **Best results**: Use chats with at least 100 messages
- **Performance**: Large chats (10,000+ messages) may take a few seconds to analyze
- **Privacy**: Don't share your `.env` file with anyone
- **Updates**: Pull latest changes from GitHub for new features

## 🆘 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Make sure all dependencies are installed
3. Try with a different chat export
4. Restart the application

## 📄 License

This project is open source and available under the MIT License.

---

**Made with ❤️ using Python and Streamlit**

Start analyzing your chats now! Run `start.bat` or `streamlit run app.py --server.port 8504`
