# 🎨 Theme Settings Guide

## How to Change Theme

### 🌐 On Streamlit Cloud (Deployed App)

1. **Open your deployed app** at `https://your-app-name.streamlit.app`
2. **Click the ⚙️ Settings icon** in the top-right corner
3. **Select Settings** from the dropdown menu
4. **Choose Theme:**
   - 🌕 **Light** - Bright, clean appearance
   - 🌑 **Dark** - Dark mode for night viewing
5. **Close the menu** - Changes apply instantly

### 💻 On Local Machine

#### Option 1: Using the Sidebar Radio Button (Easiest)
1. Run the app locally
2. Look at the sidebar (left side)
3. Under "🎨 Theme Settings", select:
   - **Light** - Bright theme
   - **Dark** - Dark theme
   - **Auto** - Follows your system preference

#### Option 2: Edit Configuration File
Edit `.streamlit/config.toml`:

```toml
[theme]
base = "light"  # Change to "dark" for dark theme
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#31333F"
font = "sans serif"
```

Then restart the app.

#### Option 3: Using Environment Variable
```bash
streamlit run app.py --theme dark
```

---

## Theme Options Explained

### 🌕 Light Theme
- **Best for:** Daytime use, presentations, printing
- **Colors:** White background, dark text
- **Eye strain:** Minimal in bright environments

### 🌑 Dark Theme
- **Best for:** Night viewing, eye comfort
- **Colors:** Dark background, light text
- **Eye strain:** Reduced in low-light environments

### 🔄 Auto Theme
- **Best for:** Automatic switching based on system settings
- **Behavior:** Follows your OS theme preference
- **Windows:** Settings → Personalization → Colors
- **Mac:** System Preferences → General → Appearance

---

## Customizing Colors

### Edit `.streamlit/config.toml`

```toml
[theme]
base = "light"

# Primary UI elements
primaryColor = "#1f77b4"        # Charts, buttons, links

# Backgrounds
backgroundColor = "#ffffff"     # Main background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar, containers

# Text
textColor = "#31333F"           # Text color

# Font
font = "sans serif"             # System font
```

### Popular Color Schemes

**Blue Theme** (Current)
```toml
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#31333F"
```

**Green Theme**
```toml
primaryColor = "#00aa44"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#e8f5e9"
textColor = "#1b5e20"
```

**Purple Theme**
```toml
primaryColor = "#7b2cbf"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f3e5ff"
textColor = "#4a148c"
```

**Dark Blue Theme**
```toml
base = "dark"
primaryColor = "#1f77b4"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#161b22"
textColor = "#c9d1d9"
```

---

## Troubleshooting

### Theme Not Changing?

**Local App:**
1. Stop the app (Ctrl+C)
2. Clear cache: Delete `.streamlit/` folder
3. Restart: `streamlit run app.py`

**Streamlit Cloud:**
1. Hard refresh your browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Try a different browser
4. Wait 30 seconds for deployment to finish

### Theme Settings Greyed Out?
- May indicate app still loading
- Wait 10-15 seconds for full deployment
- Refresh the page

### Colors Look Different Than Expected?
- Some colors are overridden by custom CSS in the app
- See: Lines 40-50 in `app.py`
- Modify the CSS section to customize further

---

## Custom CSS Overrides

The app applies custom CSS for specific elements:

```python
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;  /* Custom metric color */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 600;
        color: #31333F;  /* Custom label color */
    }
    </style>
""", unsafe_allow_html=True)
```

To customize these:
1. Edit `app.py` lines 40-50
2. Modify the color values
3. Restart the app

---

## Best Practices

✅ **Do:**
- Use high contrast colors for readability
- Test theme in both light and dark environments
- Use system colors (white on dark, black on light)

❌ **Don't:**
- Use pure black text on pure white (too harsh)
- Use low contrast colors
- Override too many default styles

---

## Support

Having issues with themes?
- **Local:** Run `streamlit config show` to verify settings
- **Cloud:** Check logs in app settings
- **GitHub:** https://github.com/tanmayyy26/WhatsApp_ChatAnalyzer

---

**Status:** ✅ Theme settings are now fully configurable!
