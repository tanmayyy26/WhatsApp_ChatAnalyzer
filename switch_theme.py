#!/usr/bin/env python3
"""
Theme Switcher for WhatsApp Analyzer
Easily switch between light and dark themes
"""

import os
import sys

CONFIG_PATH = ".streamlit/config.toml"

def read_config():
    """Read current config.toml"""
    if not os.path.exists(CONFIG_PATH):
        print("❌ config.toml not found!")
        return None
    
    with open(CONFIG_PATH, 'r') as f:
        return f.read()

def get_current_theme():
    """Get current theme setting"""
    config = read_config()
    if not config:
        return None
    
    for line in config.split('\n'):
        if line.startswith('base ='):
            theme = line.split('"')[1]
            return theme
    return None

def set_theme(theme):
    """Change theme in config.toml"""
    if theme not in ["light", "dark"]:
        print(f"❌ Invalid theme: {theme}")
        print("   Available: light, dark")
        return False
    
    config = read_config()
    if not config:
        return False
    
    # Replace theme line
    lines = config.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('base ='):
            new_lines.append(f'base = "{theme}"')
        else:
            new_lines.append(line)
    
    # Write back
    with open(CONFIG_PATH, 'w') as f:
        f.write('\n'.join(new_lines))
    
    return True

def main():
    """Main theme switcher"""
    current = get_current_theme()
    
    print("=" * 50)
    print("🎨 WhatsApp Analyzer - Theme Switcher")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        theme = sys.argv[1].lower()
        
        if set_theme(theme):
            print(f"✅ Theme changed to: {theme}")
            print()
            print("📝 Restart the app to see changes:")
            print("   streamlit run app.py")
        else:
            sys.exit(1)
    else:
        # Interactive mode
        print(f"Current theme: {current}")
        print()
        print("Available themes:")
        print("  1. light  (bright, daytime)")
        print("  2. dark   (dark, nighttime)")
        print()
        
        choice = input("Choose theme (1/2) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("Cancelled.")
            return
        
        theme_map = {'1': 'light', '2': 'dark'}
        if choice not in theme_map:
            print("❌ Invalid choice!")
            sys.exit(1)
        
        new_theme = theme_map[choice]
        if set_theme(new_theme):
            print()
            print(f"✅ Theme changed to: {new_theme}")
            print()
            print("📝 Restart the app to see changes:")
            print("   streamlit run app.py")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
