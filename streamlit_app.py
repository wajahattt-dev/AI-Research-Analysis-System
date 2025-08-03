#!/usr/bin/env python3
"""
Streamlit Interface for AI Research Analysis System
A modern, user-friendly interface for conducting AI-powered research analysis.
"""

import streamlit as st
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from main import ResearchAnalyst
from utils.config import config

# Page configuration
st.set_page_config(
    page_title="AI Research Analysis System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    
    .report-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .source-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 AI Research Analysis System</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Transform your research queries into comprehensive, AI-powered analysis reports</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Research query
        query = st.text_area(
            "Research Query",
            placeholder="Enter your research question here...",
            height=100,
            help="Describe what you want to research. Be specific for better results."
        )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            output_format = st.selectbox(
                "Output Format",
                ["markdown", "pdf"],
                help="Choose the format for your final report"
            )
            
            max_sources = st.slider(
                "Maximum Sources",
                min_value=3,
                max_value=15,
                value=8,
                help="Number of sources to analyze"
            )
            
            target_audience = st.selectbox(
                "Target Audience",
                ["general", "academic", "business", "technical"],
                help="Tailor the report for your intended audience"
            )
            
            include_citations = st.checkbox(
                "Include Citations",
                value=True,
                help="Add proper citations to the report"
            )
        
        # System status
        st.markdown("## 📊 System Status")
        
        # Check API keys
        api_status = check_api_keys()
        if api_status['openai']:
            st.success("✅ OpenAI API Key")
        else:
            st.error("❌ OpenAI API Key Missing")
        
        if api_status['news']:
            st.success("✅ News API Key")
        else:
            st.warning("⚠️ News API Key Missing (News sources disabled)")
        
        # System info
        st.markdown("## ℹ️ System Info")
        st.info(f"**Version:** 1.0.0\n**Model:** {config.openai_model}\n**Sources:** ArXiv, News API, Mock Data")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">🚀 Start Your Research</h2>', unsafe_allow_html=True)
        
        # Research form
        if st.button("🔍 Start Research Analysis", type="primary", disabled=not query or not api_status['openai']):
            if query:
                st.session_state.is_processing = True
                st.session_state.research_results = None
                
                # Run research
                with st.spinner("🤖 AI agents are analyzing your research query..."):
                    results = run_research(query, output_format, max_sources, target_audience, include_citations)
                    st.session_state.research_results = results
                    st.session_state.is_processing = False
                
                st.success("✅ Research completed successfully!")
                st.rerun()
        
        # Display results
        if st.session_state.research_results:
            display_results(st.session_state.research_results)
    
    with col2:
        st.markdown('<h2 class="sub-header">📈 Quick Stats</h2>', unsafe_allow_html=True)
        
        if st.session_state.research_results:
            display_metrics(st.session_state.research_results)
        else:
            st.info("Run a research query to see statistics here.")
        
        # Recent reports
        st.markdown('<h3 class="sub-header">📄 Recent Reports</h3>', unsafe_allow_html=True)
        display_recent_reports()

def check_api_keys():
    """Check if required API keys are configured."""
    return {
        'openai': bool(config.openai_api_key and config.openai_api_key != 'your_openai_api_key_here'),
        'news': bool(config.news_api_key and config.news_api_key != 'your_news_api_key_here')
    }

def run_research(query, output_format, max_sources, target_audience, include_citations):
    """Run the research analysis."""
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize analyst
        status_text.text("Initializing AI Research Analyst...")
        progress_bar.progress(10)
        
        analyst = ResearchAnalyst()
        
        # Configure research
        config_overrides = {
            "output_format": output_format,
            "max_sources": max_sources,
            "target_audience": target_audience,
            "include_citations": include_citations
        }
        
        # Run research
        status_text.text("Conducting research analysis...")
        progress_bar.progress(30)
        
        # Use asyncio to run the async research function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                analyst.conduct_research(query, config_overrides)
            )
        finally:
            loop.close()
        
        progress_bar.progress(100)
        status_text.text("Research completed!")
        
        return results
        
    except Exception as e:
        st.error(f"❌ Research failed: {str(e)}")
        return None

def display_results(results):
    """Display research results."""
    if not results:
        return
    
    # Report content
    st.markdown('<h2 class="sub-header">📋 Research Report</h2>', unsafe_allow_html=True)
    
    if 'report_content' in results:
        with st.expander("📄 View Full Report", expanded=True):
            st.markdown(results['report_content'])
    
    # Download report
    if 'report_metadata' in results and 'file_path' in results['report_metadata']:
        file_path = results['report_metadata']['file_path']
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            st.download_button(
                label="📥 Download Report",
                data=report_content,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    # Sources analysis
    if 'sources' in results:
        st.markdown('<h3 class="sub-header">📚 Sources Analyzed</h3>', unsafe_allow_html=True)
        
        sources_data = []
        for i, source in enumerate(results['sources'], 1):
            sources_data.append({
                'Source': i,
                'Title': source.get('title', 'Untitled'),
                'Authors': source.get('authors', 'Unknown'),
                'Source Type': source.get('source', 'Unknown'),
                'Date': source.get('published', 'Unknown')
            })
        
        if sources_data:
            df = pd.DataFrame(sources_data)
            st.dataframe(df, use_container_width=True)
    
    # Comparison analysis
    if 'comparison' in results:
        st.markdown('<h3 class="sub-header">🔍 Analysis Insights</h3>', unsafe_allow_html=True)
        
        comparison = results['comparison']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if comparison.get('agreements'):
                st.markdown("**✅ Areas of Agreement:**")
                for agreement in comparison['agreements']:
                    st.markdown(f"• {agreement}")
            
            if comparison.get('common_themes'):
                st.markdown("**🎯 Common Themes:**")
                for theme in comparison['common_themes']:
                    st.markdown(f"• {theme}")
        
        with col2:
            if comparison.get('disagreements'):
                st.markdown("**❌ Areas of Disagreement:**")
                for disagreement in comparison['disagreements']:
                    st.markdown(f"• {disagreement}")
            
            if comparison.get('gaps_in_knowledge'):
                st.markdown("**🔍 Research Gaps:**")
                for gap in comparison['gaps_in_knowledge']:
                    st.markdown(f"• {gap}")

def display_metrics(results):
    """Display research metrics."""
    if not results:
        return
    
    # Number of sources
    num_sources = len(results.get('sources', []))
    st.markdown(f"""
    <div class="metric-card">
        <h3>📚 Sources</h3>
        <h2>{num_sources}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Processing time
    if 'processing_metadata' in results:
        processing_time = results['processing_metadata'].get('processing_time', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Time</h3>
            <h2>{processing_time:.1f}s</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Evidence strength
    if 'comparison' in results and 'strength_of_evidence' in results['comparison']:
        strength = results['comparison']['strength_of_evidence'].get('overall_strength', 'unknown')
        st.markdown(f"""
        <div class="metric-card">
            <h3>💪 Evidence</h3>
            <h2>{strength.title()}</h2>
        </div>
        """, unsafe_allow_html=True)

def display_recent_reports():
    """Display list of recent reports."""
    reports_dir = Path("./reports")
    if not reports_dir.exists():
        st.info("No reports generated yet.")
        return
    
    reports = list(reports_dir.glob("*.md"))
    reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for report in reports[:5]:  # Show last 5 reports
        report_name = report.stem
        report_date = datetime.fromtimestamp(report.stat().st_mtime)
        
        st.markdown(f"""
        <div class="source-card">
            <strong>{report_name}</strong><br>
            <small>{report_date.strftime('%Y-%m-%d %H:%M')}</small>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 