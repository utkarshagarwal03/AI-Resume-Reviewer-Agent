import streamlit as st
import os
import logging
from dotenv import load_dotenv
from agents.graph import run_resume_analysis
from rag.vectorstore import build_vector_store, create_chat_chain
from utils.pdf_reader import extract_text_from_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load local environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Resume Reviewer Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Executive ATS Score Card */
    .ats-score-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    
    .ats-score-num {
        font-size: 72px;
        font-weight: 800;
        margin: 10px 0;
        letter-spacing: -2px;
    }
    
    /* General Premium Cards */
    .custom-card {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .custom-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Skill Badges */
    .skills-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
    }
    .skill-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
        display: inline-block;
    }
    .extracted-badge {
        background-color: rgba(30, 136, 229, 0.15);
        color: #90CAF9;
        border: 1px solid rgba(30, 136, 229, 0.3);
    }
    .missing-badge {
        background-color: rgba(229, 57, 53, 0.15);
        color: #EF9A9A;
        border: 1px solid rgba(229, 57, 53, 0.3);
    }
    
    /* Roadmap Step Cards */
    .roadmap-card {
        background: rgba(255, 255, 255, 0.015);
        border-left: 4px solid #1E88E5;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin-bottom: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .roadmap-phase {
        font-weight: 700;
        color: #42A5F5;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #E0E0E0;
        margin-bottom: 12px;
        border-left: 3px solid #00E676;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to interpret the ATS score
def get_score_interpretation(score: int) -> str:
    if score >= 80:
        return "🔥 Excellent! The resume is highly optimized for target keywords, syntax, and layout."
    elif score >= 60:
        return "✨ Good! Solid foundation, but requires keyword refinement and stronger action verbs."
    else:
        return "⚠️ Critical Gaps! Missing core skills and needs structural improvement."

# Sidebar configuration
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🚀 AI Resume Agent</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9E9E9E;'>Analyze & Optimize your Resume with LangGraph & Gemini</p>", unsafe_allow_html=True)
    st.write("---")
    
    # API Key management
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Provide your Gemini API key. If already set as an environment variable (GOOGLE_API_KEY), you can leave this blank."
    )
    
    st.write("---")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    st.write("---")
    
    # Run button
    analyze_button = st.button("🔍 Run Full Analysis", use_container_width=True, type="primary")
    
    if st.session_state.get("analysis_results"):
        st.success("Analysis Complete!")
        st.metric("Overall ATS Score", f"{st.session_state.analysis_results.get('ats_score', 0)}/100")
        
        # Sidebar reset button
        if st.button("🧹 Clear & Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# Layout management
if not st.session_state.get("analysis_results"):
    # Initial Welcome Screen
    st.markdown("<h1 style='text-align: center;'>AI Resume Reviewer & Career Agent</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; font-weight: normal; color: #9E9E9E;'>Prepare for placement interviews with ATS evaluation, side-by-side bullet point fixes, technical interview preps, and an interactive resume RAG bot.</h4>", unsafe_allow_html=True)
    
    st.write("---")
    
    # Grid of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="custom-card">
            <h3>📊 ATS Scoring</h3>
            <p>Evaluate your resume relevance using advanced LLM processing. Get an instant score and section critique.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="custom-card">
            <h3>🤖 Interview Coach</h3>
            <p>Get custom HR, Java, DSA, SQL, and project-based questions matched to your profile, complete with preparation tips.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h3>🔍 Skill Gap Detection</h3>
            <p>Automatically match extracted technical and soft skills against standard industry benchmarks to uncover gaps.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="custom-card">
            <h3>🗺️ Learning Roadmap</h3>
            <p>Get recommended certifications, missing technologies, and a week-by-week learning roadmap customized for your career path.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="custom-card">
            <h3>✍️ Bullet Point Optimizer</h3>
            <p>Convert generic descriptions to high-impact accomplishment bullets using metrics, verbs, and the STAR framework.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="custom-card">
            <h3>💬 RAG Resume Chatbot</h3>
            <p>Index your resume dynamically in a FAISS vector store and chat with it in real time to test response relevance.</p>
        </div>
        """, unsafe_allow_html=True)

    # Check for run trigger
    if analyze_button:
        if not uploaded_file:
            st.error("Please upload a PDF resume first.")
        else:
            api_key = api_key_input or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                st.error("Google Gemini API Key is required. Please enter it in the sidebar or set it in your .env file.")
            else:
                with st.spinner("Analyzing resume... This executes Parser, ATS, Improvement, Interview, and Career agents in a LangGraph workflow."):
                    try:
                        pdf_bytes = uploaded_file.read()
                        
                        # Execute LangGraph Pipeline
                        final_state = run_resume_analysis(pdf_bytes, api_key=api_key)
                        
                        if final_state.get("error"):
                            st.error(f"Analysis Error: {final_state['error']}")
                        else:
                            # Save state
                            st.session_state.analysis_results = final_state
                            
                            # Initialize RAG
                            vector_store = build_vector_store(final_state["resume_text"], api_key=api_key)
                            chat_chain = create_chat_chain(vector_store, api_key=api_key)
                            
                            st.session_state.vector_store = vector_store
                            st.session_state.chat_chain = chat_chain
                            st.session_state.messages = []
                            
                            st.success("Analysis complete!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to execute analysis pipeline: {str(e)}")
else:
    # Render dashboard
    state = st.session_state.analysis_results
    
    st.markdown("<h1>🚀 Resume Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Executive Row (ATS Score + Summary)
    col_score, col_summary = st.columns([1, 2])
    
    with col_score:
        score = state.get("ats_score", 0)
        color = "#00E676" if score >= 80 else "#FFB300" if score >= 60 else "#EF5350"
        
        st.markdown(f"""
        <div class="ats-score-card">
            <h3 style="margin: 0; color: #E0E0E0;">Overall ATS Score</h3>
            <div class="ats-score-num" style="color: {color};">{score}/100</div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 10px; height: 12px; overflow: hidden; margin-top: 10px;">
                <div style="background: {color}; width: {score}%; height: 100%; border-radius: 10px;"></div>
            </div>
            <p style="margin-top: 15px; font-size: 15px; color: #CFD8DC; font-weight: 500;">
                {get_score_interpretation(score)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_summary:
        st.markdown("<div class='section-header'>Candidate Profile Summary</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 16px; line-height: 1.6; color: #ECEFF1;'>{state.get('summary', '')}</div>", unsafe_allow_html=True)
        
        # Mini Columns for Strengths & Weaknesses
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("<div style='color: #81C784; font-weight: 600; margin-top: 12px;'>✓ Core Strengths</div>", unsafe_allow_html=True)
            for strg in state.get("strengths", [])[:3]:
                st.markdown(f"<div style='font-size: 14px; color: #CFD8DC;'>• {strg}</div>", unsafe_allow_html=True)
        with col_w:
            st.markdown("<div style='color: #E57373; font-weight: 600; margin-top: 12px;'>✗ Areas for Improvement</div>", unsafe_allow_html=True)
            for weak in state.get("weaknesses", [])[:3]:
                st.markdown(f"<div style='font-size: 14px; color: #CFD8DC;'>• {weak}</div>", unsafe_allow_html=True)

    st.write("---")
    
    # Create Tabs for detailed feedback
    tab_skills, tab_improvements, tab_interview, tab_career, tab_export = st.tabs([
        "🔍 Skill Gap Analysis",
        "✍️ Bullet Point Optimizer",
        "👨‍💻 Interview Coach",
        "🗺️ Career Advisor & Roadmap",
        "📥 Export Report"
    ])
    
    # 1. Skill Gap Tab
    with tab_skills:
        st.subheader("Skill Mapping & Keyword Optimization")
        st.write("Ensuring keywords align with common applicant tracking filters.")
        
        col_ext, col_miss = st.columns(2)
        
        with col_ext:
            st.markdown("<div class='section-header'>Extracted Skills</div>", unsafe_allow_html=True)
            st.write("These skills were identified on your resume:")
            extracted = state.get("extracted_skills", [])
            if extracted:
                badges = "".join([f'<span class="skill-badge extracted-badge">{s}</span>' for s in extracted])
                st.markdown(f'<div class="skills-container">{badges}</div>', unsafe_allow_html=True)
            else:
                st.info("No skills detected.")
                
        with col_miss:
            st.markdown("<div class='section-header'>Missing Industry Keywords</div>", unsafe_allow_html=True)
            st.write("Adding these keywords can help match ATS filter requirements:")
            missing = state.get("missing_skills", [])
            if missing:
                badges = "".join([f'<span class="skill-badge missing-badge">{s}</span>' for s in missing])
                st.markdown(f'<div class="skills-container">{badges}</div>', unsafe_allow_html=True)
            else:
                st.success("No critical missing skills identified!")
                
        # Weak Sections
        st.write("---")
        st.markdown("<div class='section-header'>Weak Sections / Structure Critic</div>", unsafe_allow_html=True)
        for ws in state.get("weak_sections", []):
            st.markdown(f"- {ws}")
        if not state.get("weak_sections"):
            st.success("Your resume sections are well-defined!")
            
    # 2. Bullet Point Optimizer Tab
    with tab_improvements:
        st.subheader("Bullet Point Improvement & Formatting Advice")
        st.write("Compare rewritten bullet points optimized for STAR framework and action verbs.")
        
        # Side-by-Side improvements
        bullets = state.get("improved_bullets", [])
        if bullets:
            for idx, bullet in enumerate(bullets, 1):
                st.markdown(f"""
                <div class="custom-card">
                    <div style="font-weight: 700; color: #42A5F5; margin-bottom: 10px; font-size: 16px;">Suggestion {idx}</div>
                    <div style="margin-left: 10px;">
                        <p style="color: #EF5350; margin: 4px 0;"><strong>Original:</strong> <em>"{bullet.get('original', '')}"</em></p>
                        <p style="color: #66BB6A; margin: 4px 0;"><strong>Improved:</strong> <strong>"{bullet.get('improved', '')}"</strong></p>
                        <p style="color: #B0BEC5; margin: 4px 0; font-size: 13px;"><strong>Why:</strong> {bullet.get('reason', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No bullet point improvements needed.")
            
        # Formatting Suggestions & New Projects
        st.write("---")
        col_format, col_proj = st.columns(2)
        
        with col_format:
            st.markdown("<div class='section-header'>Layout & Formatting Suggestions</div>", unsafe_allow_html=True)
            for sug in state.get("formatting_suggestions", []):
                st.markdown(f"- {sug}")
            if not state.get("formatting_suggestions"):
                st.success("No layout suggestions. formatting looks standard!")
                
        with col_proj:
            st.markdown("<div class='section-header'>Suggested Portfolio Projects</div>", unsafe_allow_html=True)
            for proj in state.get("project_suggestions", []):
                st.markdown(f"- {proj}")
            if not state.get("project_suggestions"):
                st.info("No projects suggested.")
                
    # 3. Interview Coach Tab
    with tab_interview:
        st.subheader("Personalized Mock Interview Simulator")
        st.write("Questions tailored to your profile, key programming constructs, and projects.")
        
        # Accordion of question types
        with st.expander("💼 Behavioral & HR Questions", expanded=True):
            for idx, q in enumerate(state.get("hr_questions", []), 1):
                st.markdown(f"**Q{idx}: {q.get('question', '')}**")
                st.markdown(f"> **Approach:** {q.get('best_approach', '')}")
                st.write("")
                
        with st.expander("☕ Java Interview Questions"):
            for idx, q in enumerate(state.get("java_questions", []), 1):
                st.markdown(f"**Q{idx}: {q.get('question', '')}**")
                st.markdown(f"> **Approach:** {q.get('best_approach', '')}")
                st.write("")
                
        with st.expander("📈 Data Structures & Algorithms (DSA)"):
            for idx, q in enumerate(state.get("dsa_questions", []), 1):
                st.markdown(f"**Q{idx}: {q.get('question', '')}**")
                st.markdown(f"> **Approach:** {q.get('best_approach', '')}")
                st.write("")
                
        with st.expander("🗄️ SQL & Databases"):
            for idx, q in enumerate(state.get("sql_questions", []), 1):
                st.markdown(f"**Q{idx}: {q.get('question', '')}**")
                st.markdown(f"> **Approach:** {q.get('best_approach', '')}")
                st.write("")
                
        with st.expander("🛠️ Project-Based Questions"):
            for idx, q in enumerate(state.get("project_questions", []), 1):
                st.markdown(f"**Q{idx}: {q.get('question', '')}**")
                st.markdown(f"> **Approach:** {q.get('best_approach', '')}")
                st.write("")

    # 4. Career Advisor Tab
    with tab_career:
        st.subheader("Career Growth Recommendations & Roadmaps")
        
        col_c, col_tech = st.columns(2)
        with col_c:
            st.markdown("<div class='section-header'>Recommended Certifications</div>", unsafe_allow_html=True)
            for cert in state.get("certifications", []):
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <strong>{cert.get('name')}</strong> ({cert.get('provider')})<br/>
                    <span style="font-size: 13px; color:#B0BEC5;">{cert.get('relevance')}</span>
                </div>
                """, unsafe_allow_html=True)
            if not state.get("certifications"):
                st.info("No specific certifications recommended.")
                
        with col_tech:
            st.markdown("<div class='section-header'>Key Missing Technologies</div>", unsafe_allow_html=True)
            for tech in state.get("missing_technologies", []):
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <strong>{tech.get('name')}</strong><br/>
                    <span style="font-size: 13px; color:#B0BEC5;">{tech.get('reason')}</span>
                </div>
                """, unsafe_allow_html=True)
            if not state.get("missing_technologies"):
                st.success("No missing tech stack gaps found.")
                
        # Roadmap Timeline
        st.write("---")
        st.markdown("<div class='section-header'>Custom Learning Roadmap</div>", unsafe_allow_html=True)
        for phase in state.get("learning_roadmap", []):
            topics_str = ", ".join(phase.get("topics", []))
            st.markdown(f"""
            <div class="roadmap-card">
                <div class="roadmap-phase">{phase.get('phase')}</div>
                <div style="margin-top: 6px; color:#E0E0E0;"><strong>Topics:</strong> {topics_str}</div>
                <div style="margin-top: 4px; font-size: 13px; color: #B0BEC5;"><strong>Suggested Resources:</strong> {phase.get('resources')}</div>
            </div>
            """, unsafe_allow_html=True)
            
    # 5. Export Report Tab
    with tab_export:
        st.subheader("Download Full Career & Resume Report")
        st.write("Generate a complete text analysis output formatted in Markdown, perfect for offline reading or printing.")
        
        report_md = state.get("report_markdown", "")
        
        st.download_button(
            label="📥 Download Markdown Report",
            data=report_md,
            file_name="Resume_Review_Report.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        with st.expander("Preview Report", expanded=False):
            st.markdown(report_md)

    # RAG Chat Interface at the bottom
    st.write("---")
    st.markdown("<h2>💬 Chat with your Resume</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9E9E9E;'>Ask clarifying questions, test pitch ideas, or ask the chatbot how to explain a gap using context from your resume.</p>", unsafe_allow_html=True)
    
    # Initialize message list in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Render historical conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # User Input Field
    if prompt := st.chat_input("Ask a question (e.g. 'How would you summarize my project experiences?')"):
        # Display user input
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get LLM output from vectorstore conversational retrieval chain
        with st.chat_message("assistant"):
            with st.spinner("Analyzing resume facts..."):
                try:
                    chat_chain = st.session_state.chat_chain
                    response = chat_chain.invoke({"question": prompt})
                    answer = response.get("answer", "No answer could be retrieved.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error answering query: {str(e)}")
