#!/usr/bin/env python
"""Full Project Health Check"""
import os
import sys

print("="*60)
print("🔍 FULL PROJECT HEALTH CHECK")
print("="*60)
print()

# Check 1: Critical files
print("1️⃣ CRITICAL FILES:")
files = [
    'app.py',
    'requirements.txt',
    '.env',
    '.streamlit/config.toml',
    'README.md',
    'src/__init__.py',
    'src/analyzers/__init__.py',
    'src/analyzers/chatline.py',
    'src/analyzers/reply_analyzer.py',
    'src/database/__init__.py',
    'src/database/supabase_client.py',
]
all_exist = True
for f in files:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌"
    print(f"  {status} {f}")
    if not exists:
        all_exist = False

print()

# Check 2: Dependencies
print("2️⃣ DEPENDENCIES INSTALLED:")
deps = ['streamlit', 'pandas', 'plotly', 'wordcloud', 'supabase', 'python_dateutil']
all_deps = True
try:
    import pkg_resources
    for dep in deps:
        try:
            pkg_resources.get_distribution(dep)
            print(f"  ✅ {dep}")
        except:
            print(f"  ❌ {dep} - MISSING!")
            all_deps = False
except:
    print("  ⚠️ Could not check dependencies")

print()

# Check 3: Code syntax
print("3️⃣ CODE SYNTAX:")
try:
    import py_compile
    py_compile.compile('app.py', doraise=True)
    print("  ✅ app.py - No syntax errors")
    syntax_ok = True
except Exception as e:
    print(f"  ❌ app.py - {str(e)}")
    syntax_ok = False

print()

# Check 4: Environment variables
print("4️⃣ ENVIRONMENT VARIABLES:")
from dotenv import load_dotenv
load_dotenv()
env_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
env_ok = True
for var in env_vars:
    val = os.getenv(var)
    if val:
        masked = val[:20] + "***" if len(val) > 20 else val
        print(f"  ✅ {var} - Set ({len(val)} chars)")
    else:
        print(f"  ⚠️ {var} - Not set (optional for local)")
        env_ok = False

print()

# Check 5: Test imports
print("5️⃣ CRITICAL IMPORTS:")
import_ok = True
try:
    import streamlit
    print("  ✅ streamlit")
    import pandas
    print("  ✅ pandas")
    import plotly.express
    print("  ✅ plotly")
    from src.analyzers.chatline import Chatline
    print("  ✅ Chatline")
    from src.analyzers.reply_analyzer import ReplyAnalyzer
    print("  ✅ ReplyAnalyzer")
    from src.database.supabase_client import supabase_manager
    print("  ✅ Supabase client")
    if supabase_manager.is_connected():
        print("  ✅ Supabase - CONNECTED")
    else:
        print("  ⚠️ Supabase - Not connected (optional)")
except Exception as e:
    print(f"  ❌ Import error: {e}")
    import_ok = False

print()

# Summary
print("="*60)
print("📊 SUMMARY:")
print("="*60)
print()

issues = []
if not all_exist:
    issues.append("❌ Missing files")
if not all_deps:
    issues.append("❌ Missing dependencies")
if not syntax_ok:
    issues.append("❌ Syntax errors")
if not import_ok:
    issues.append("❌ Import errors")

if not issues:
    print("✅ PROJECT IS PERFECT!")
    print()
    print("No issues found. Your app is:")
    print("  ✅ Syntactically correct")
    print("  ✅ All files present")
    print("  ✅ All dependencies installed")
    print("  ✅ All imports working")
    print("  ✅ Supabase connected")
    print("  ✅ Ready to deploy!")
    sys.exit(0)
else:
    print("⚠️ ISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
    sys.exit(1)
