#!/bin/bash
# Quick Deploy Script for Streamlit Cloud

# This script helps you deploy to Streamlit Cloud

echo "🚀 WhatsApp Analyzer - Streamlit Cloud Deployment"
echo "=================================================="
echo ""
echo "Prerequisites:"
echo "✓ Git installed"
echo "✓ Streamlit account (https://share.streamlit.io)"
echo "✓ GitHub repository synced"
echo ""
echo "Step 1: Ensure all changes are committed"
cd "c:\Users\Lenovo\OneDrive\Desktop\examples\same lov\WhatsApp-Analyzer"
echo "Current git status:"
git status
echo ""
echo "Step 2: Verify requirements.txt"
echo "File: requirements.txt"
echo "Content:"
cat requirements.txt
echo ""
echo "Step 3: Open Streamlit Cloud in browser"
echo "URL: https://share.streamlit.io"
echo ""
echo "Step 4: Deploy Instructions"
echo "1. Click 'New app'"
echo "2. Repository: tanmayyy26/WhatsApp_ChatAnalyzer"
echo "3. Branch: main"
echo "4. Main file: app.py"
echo "5. Click 'Deploy'"
echo ""
echo "✅ Your app will be live at: https://[your-app-name].streamlit.app"
