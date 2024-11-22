import streamlit as st
from pathlib import Path

# Configuration
VIEWS_DIR = Path("views")

def main():
    """Initialize and run the application"""
    pages = {
        "💰 Current Status": {
            "path": VIEWS_DIR / "current.py",
            "icon": "💰",
        },
        "📈 Evolution View": {
            "path": VIEWS_DIR / "evolution.py",
            "icon": "📈",
        }
    }
    
    # Create navigation
    page_objects = []
    for title, config in pages.items():
        page = st.Page(
            str(config["path"]),
            title=title,
            icon=config["icon"],
        )
        page_objects.append(page)
    
    navigation = st.navigation({"Menu": page_objects})
    navigation.run()

if __name__ == "__main__":
    main()