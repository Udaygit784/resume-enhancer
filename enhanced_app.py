import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Set, Optional, Tuple, Any
import re
import json
from streamlit_tags import st_tags
from resume_parser import ResumeParser

# Set page config
st.set_page_config(
    page_title="Enhanced Resume Parser & JD Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize parser
parser = ResumeParser()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        max-width: 1200px;
        padding: 2rem;
    }
    .header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #1E88E5;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: #424242;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .skill-tag {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .missing-skill {
        background-color: #ffebee;
        color: #d32f2f;
    }
    .progress-bar {
        height: 10px;
        background-color: #e0e0e0;
        border-radius: 5px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background-color: #4caf50;
        border-radius: 5px;
        transition: width 0.3s ease;
    }
    .section {
        margin-bottom: 1.5rem;
    }
    .experience-item, .education-item, .project-item {
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }
    .experience-item:last-child, .education-item:last-child, .project-item:last-child {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'resumes' not in st.session_state:
    st.session_state.resumes = []

# Sidebar for job description
with st.sidebar:
    st.title("🔍 Job Description")
    job_description = st.text_area("Paste Job Description", height=300, 
                                 placeholder="Paste the job description here to analyze skill matches...",
                                 help="Paste the job description to automatically match skills with resumes")
    
    st.markdown("---")
    st.markdown("### 📤 Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF or DOCX files", 
                                    type=['pdf', 'docx', 'doc'],
                                    accept_multiple_files=True,
                                    help="Upload multiple resume files (PDF/DOCX)")
    
    if st.button("🚀 Process Resumes", use_container_width=True):
        if uploaded_files:
            with st.spinner('Processing resumes...'):
                for file in uploaded_files:
                    # Check if file is already processed
                    if not any(r['filename'] == file.name for r in st.session_state.resumes):
                        resume_data = parser.parse_resume(file, job_description)
                        st.session_state.resumes.append(resume_data)
                st.success(f"✅ Processed {len(uploaded_files)} resume(s)!")
        else:
            st.warning("⚠️ Please upload at least one resume file.")
    
    # Clear all button
    if st.button("🗑️ Clear All Resumes", use_container_width=True):
        st.session_state.resumes = []
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Total Resumes", len(st.session_state.resumes))
    
    if job_description and st.session_state.resumes:
        avg_match = sum(r.get('skill_match', {}).get('match_percentage', 0) 
                       for r in st.session_state.resumes) / len(st.session_state.resumes)
        st.metric("Average Match", f"{avg_match:.1f}%")

# Main content
st.markdown("<div class='header'>📄 Enhanced Resume Parser & JD Matcher</div>", unsafe_allow_html=True)

if not st.session_state.resumes:
    st.info("👈 Upload resumes and paste a job description to get started!")
    
    # Features section
    st.markdown("### ✨ Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📝 Resume Parsing
        - Extract contact information
        - Parse work experience
        - Identify skills and education
        - Project history extraction
        """)
    
    with col2:
        st.markdown("""
        #### 🔍 JD Matching
        - Skill gap analysis
        - Match percentage calculation
        - Missing skills identification
        - Resume ranking
        """)
    
    with col3:
        st.markdown("""
        #### 📊 Analytics
        - Visual skill matching
        - Experience analysis
        - Education verification
        - Exportable results
        """)
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. Upload one or more resume files (PDF/DOCX)
    2. Paste a job description in the sidebar
    3. Click 'Process Resumes'
    4. View detailed analysis and matches
    """)
else:
    # Filter and sort resumes
    st.markdown(f"### 📋 Found {len(st.session_state.resumes)} Resumes")
    
    # Sort by match percentage if job description is provided
    if job_description:
        st.session_state.resumes.sort(
            key=lambda x: x.get('skill_match', {}).get('match_percentage', 0), 
            reverse=True
        )
    
    # Display each resume
    for i, resume in enumerate(st.session_state.resumes):
        with st.container():
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            
            # Header with name and match score
            col1, col2 = st.columns([4, 1])
            with col1:
                name = resume.get('contact_info', {}).get('name', 'Unknown')
                st.markdown(f"### {name}")
                
                # Contact info
                contact_info = []
                if resume.get('contact_info', {}).get('email'):
                    contact_info.append(f"📧 {resume['contact_info']['email']}")
                if resume.get('contact_info', {}).get('phone'):
                    contact_info.append(f"📞 {resume['contact_info']['phone']}")
                if contact_info:
                    st.markdown(" | ".join(contact_info))
            
            # Match score
            if job_description and 'skill_match' in resume:
                match_percentage = resume['skill_match'].get('match_percentage', 0)
                with col2:
                    st.markdown(f"<div style='text-align: right;'>"
                               f"<div style='font-size: 1.8rem; font-weight: bold; color: #1E88E5;'>{match_percentage}%</div>"
                               f"<div style='font-size: 0.8rem;'>Match Score</div>"
                               f"</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tabs for different sections
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🎓 Education", "💼 Experience", "🔧 Skills", "🚀 Projects"])
            
            with tab1:  # Overview
                st.markdown("#### 📝 Summary")
                if resume.get('raw_text'):
                    st.write(resume['raw_text'][:500] + '...' if len(resume['raw_text']) > 500 else resume['raw_text'])
                
                if job_description and 'skill_match' in resume:
                    st.markdown("#### 📈 Skill Match Analysis")
                    match_data = resume['skill_match']
                    
                    # Progress bar
                    st.markdown(f"**Match Score: {match_data['match_percentage']}%**")
                    match_pct = match_data.get('match_percentage', 0)
                    st.markdown(
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {match_pct}%"></div></div>',
                        unsafe_allow_html=True
                    )
                    
                    # Matched skills
                    if match_data.get('found_skills'):
                        st.markdown("✅ **Matched Skills:**")
                        for skill in match_data['found_skills']:
                            st.markdown(f"<span class='skill-tag'>{skill}</span>", unsafe_allow_html=True)
                    
                    # Missing skills
                    if match_data.get('missing_skills'):
                        st.markdown("❌ **Missing Skills:**")
                        for skill in match_data['missing_skills']:
                            st.markdown(f"<span class='skill-tag missing-skill'>{skill}</span>", unsafe_allow_html=True)
            
            with tab2:  # Education
                if resume.get('education'):
                    for edu in resume['education']:
                        st.markdown(f"<div class='education-item'>"
                                   f"<h4>{edu.get('degree', 'N/A')}</h4>"
                                   f"<p>🎓 {edu.get('institution', 'N/A')}</p>"
                                   f"<p>📅 {edu.get('year', 'N/A')}</p>"
                                   f"</div>", unsafe_allow_html=True)
                else:
                    st.info("No education information found.")
            
            with tab3:  # Experience
                if resume.get('experience'):
                    for exp in resume['experience']:
                        st.markdown(f"<div class='experience-item'>"
                                   f"<h4>{exp.get('position', 'N/A')}</h4>"
                                   f"<p>🏢 {exp.get('company', 'N/A')}</p>"
                                   f"<p>📅 {exp.get('duration', 'N/A')}</p>"
                                   f"</div>", unsafe_allow_html=True)
                else:
                    st.info("No work experience found.")
            
            with tab4:  # Skills
                if resume.get('skills'):
                    st.markdown("#### 🛠️ Technical Skills")
                    for skill in resume['skills']:
                        st.markdown(f"<span class='skill-tag'>{skill}</span>", unsafe_allow_html=True)
                else:
                    st.info("No skills information found.")
            
            with tab5:  # Projects
                if resume.get('projects'):
                    for proj in resume['projects']:
                        st.markdown(f"<div class='project-item'>"
                                   f"<h4>{proj.get('name', 'Unnamed Project')}</h4>"
                                   f"<p>{proj.get('description', 'No description available.')}</p>"
                                   f"</div>", unsafe_allow_html=True)
                else:
                    st.info("No projects information found.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

# Download results as JSON
if st.session_state.resumes:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Results")
    
    # Convert to JSON
    json_data = json.dumps(st.session_state.resumes, indent=2, default=str)
    
    # Create download button
    st.sidebar.download_button(
        label="💾 Download Results (JSON)",
        data=json_data,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Install required NLTK data
import nltk
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Install spaCy model
import subprocess
import sys

def install_spacy_model():
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            with st.spinner("Downloading language model for spaCy..."):
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    except Exception as e:
        st.error(f"Error installing spaCy model: {e}")

# Run the installation
install_spacy_model()
