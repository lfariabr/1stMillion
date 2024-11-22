import streamlit as st
from datetime import datetime

def setup_page():
    """Configure the initial page settings"""
    st.set_page_config(
        page_title="1st Million Journey",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def main():
    # Setup page configuration
    setup_page()
    
    # Header section
    st.title("📈 Journey to the First Million")
    
    # Add current date
    st.sidebar.markdown(f"**Today's Date:** {datetime.now().strftime('%Y-%m-%d')}")
    
    # Main content
    st.markdown("## Your Financial Dashboard")
    
    # Create columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Assets", value="$0", delta="0%")
    
    with col2:
        st.metric(label="Monthly Growth", value="$0", delta="0%")
    
    with col3:
        st.metric(label="Progress to Goal", value="0%", delta="0%")
    
    # Progress section
    st.progress(0, text="Progress to 1st Million")
    
    # Add timeline section
    st.markdown("### Timeline")
    st.info("Track your journey and milestones here!")
    
    # Footer
    st.markdown("---")
    st.markdown("*Building wealth one step at a time* 💪")

if __name__ == "__main__":
    main()