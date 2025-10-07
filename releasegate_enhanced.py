import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from io import BytesIO

def persist_summary(summary):
    """Store latest summary in session_state for export."""
    st.session_state.last_summary = summary

def summary_to_json_bytes(summary):
    import json as _json
    return _json.dumps(summary, indent=2, default=str).encode('utf-8')

def generate_pdf_report(summary):
    """Generate a simple PDF report for the given summary.
    Uses reportlab if available, otherwise returns (None, error_message).
    Returns (bytes_or_none, error_or_none)
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import mm
    except ImportError:
        return None, "reportlab not installed. Install with: pip install reportlab"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 30
    def line(text, size=11, color=colors.black):
        nonlocal y
        if y < 40:
            c.showPage(); y = height - 30
        c.setFont("Helvetica", size)
        c.setFillColor(color)
        c.drawString(30, y, text)
        y -= 16

    # Header
    line("ReleaseGate Technical Assessment", 16, colors.HexColor('#00478f'))
    line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 9)
    line("", 6)

    decision = summary['decision']
    line(f"Decision: {decision}", 14, colors.green if decision=="GO" else colors.orange if decision=="CONDITIONAL" else colors.red)
    line(f"Risk Score: {summary['risk_score']}")
    kpis = summary['kpis']
    line("KPIs:", 12, colors.HexColor('#00478f'))
    for k,v in kpis.items():
        line(f" - {k}: {v}")
    if summary['reasons']:
        line("Issues:", 12, colors.red)
        for r in summary['reasons']:
            line(f" * {r}")
    else:
        line("No gating issues detected.")

    # Narrative (strip markdown)
    narrative = generate_story_narrative(summary)
    import re
    cleaned = re.sub(r'[#*_`>]', '', narrative)
    line("",6)
    line("Narrative Summary:", 12, colors.HexColor('#00478f'))
    for para in cleaned.splitlines():
        if para.strip():
            line(para[:120])

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes, None

def get_logo_html():
    """Return HTML for Allianz (or fallback) logo placed top-right.
    Priority:
      1. User uploaded logo kept in st.session_state (supports png/jpg/svg)
      2. Disk assets (common filename patterns under ./assets or root)
      3. Fallback styled initials box
    """
    # 1. Uploaded runtime logo
    if 'uploaded_logo' in st.session_state:
        data = st.session_state['uploaded_logo']
        if data.get('type') == 'svg':
            return f"<div class='alliance-logo' style='background:transparent; padding:4px;'>{data['content']}</div>"
        else:
            return (f"<div class='alliance-logo' style='background:transparent;'>"
                    f"<img src='data:{data['mime']};base64,{data['b64']}' style='max-width:100%; max-height:100%; object-fit:contain;' />"
                    f"</div>")

    # 2. Disk search
    search_names = [
        'allianz.png','allianz.svg','allianz.jpg','allianz_logo.png',
        'allianz_logo.svg','allianz-logo.png','Allianz.png','Allianz.svg'
    ]
    candidate_paths = []
    # assets/ directory preferred
    for name in search_names:
        candidate_paths.append(os.path.join('assets', name))
        candidate_paths.append(name)
    chosen_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            chosen_path = p
            break
    if chosen_path:
        try:
            ext = chosen_path.split('.')[-1].lower()
            if ext == 'svg':
                with open(chosen_path,'r',encoding='utf-8') as f:
                    svg_content = f.read()
                return f"<div class='alliance-logo' style='background:transparent; padding:4px;'>{svg_content}</div>"
            else:
                with open(chosen_path,'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                mime = 'image/png' if ext=='png' else 'image/jpeg'
                return f"<div class='alliance-logo' style='background:transparent;'><img src='data:{mime};base64,{b64}' style='max-width:100%; max-height:100%; object-fit:contain;'/></div>"
        except Exception:
            pass
    # Fallback box with initials
    return "<div class='alliance-logo'>AI</div>"

# --- Commercial UI Styling ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main theme and colors */
    .main {
        background: #f5f7fa;
        color: #1f2d3d;
    }
    
    .stApp {
        background: linear-gradient(135deg, #e6ecf3 0%, #eef3f8 60%, #d9e2ec 100%);
        min-height: 100vh;
        color: #1f2d3d !important;
    }
    
    /* Alliance logo */
    .alliance-logo {
        position: absolute;
        top: 15px;
        right: 25px;
        width: 70px;
        height: 70px;
        background: #00478f;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
        box-shadow: 0 6px 18px rgba(0, 71, 143, 0.35);
        z-index: 1200;
        letter-spacing: 1px;
        font-family: 'Inter', sans-serif;
    }
    .alliance-logo img { width:100%; height:100%; object-fit:contain; }
    
    /* Header styling */
    .main-header {
        background: #ffffff;
        padding: 2rem 2.5rem;
        border-radius: 18px;
        margin: 2rem 0 1.5rem 0;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before { display:none; }
    
    @keyframes borderGlow {
        0% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .release-gate-logo {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00478f, #0070c9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: 1px;
        text-shadow: none;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .subtitle {
        color: #334155;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
        text-shadow: none;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Cards and sections */
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem 1.5rem 1.25rem 1.5rem;
        margin: 1.25rem 0;
        border: 1px solid #e2e8f0;
        transition: all 0.25s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        color: #1f2d3d;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-color: #94a3b8;
    }
    
    /* Interactive elements */
    .interactive-metric {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1rem 0.75rem 1rem;
        margin: 0.75rem 0 0.5rem 0;
        cursor: pointer;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    
    .interactive-metric:hover {
        border-color: #94a3b8;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .interactive-metric::before, .interactive-metric:hover::before { display:none; }
    
    /* Decision styling */
    .decision-go {
        background: #0f766e;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 1.5rem 0;
    }
    
    .decision-nogo {
        background: #991b1b;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 1.5rem 0;
    }
    
    .decision-conditional {
        background: #b45309;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 1.5rem 0;
    }
    
    /* Animations */
    @keyframes pulse { 0%{opacity:1;}100%{opacity:1;} }
    @keyframes shake { 0%{transform:none;}100%{transform:none;} }
    
    /* Timeline styling */
    .timeline {
        position: relative;
        padding: 2rem 0;
    }
    
    .timeline-item {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
    }
    
    /* Chatbot styling */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 380px;
        max-height: 520px;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 12px 34px rgba(0,0,0,0.18);
        z-index: 1100;
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, opacity 0.3s ease;
        display: none;
        overflow: hidden;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .chatbot-container.active { display:block; }
    
    .chatbot-toggle {
        position: fixed;
        bottom: 22px;
        right: 22px;
        width: 58px;
        height: 58px;
        background: #00478f;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 10px 18px rgba(0,52,94,0.35);
        z-index: 1150;
        transition: all 0.25s ease;
        color: #ffffff;
        font-size: 28px;
    }
    .chatbot-toggle:hover { transform: scale(1.05); box-shadow:0 12px 26px rgba(0,52,94,0.45);} 
    @keyframes chatbotPulse {0%{opacity:1;}100%{opacity:1;}}
    
    .chatbot-header {
        background: #00478f;
        color: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 0 0;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Inter', sans-serif;
    }
    
    .chatbot-close {
        cursor: pointer;
        font-size: 18px;
        opacity: 0.7;
        transition: opacity 0.3s;
    }
    
    .chatbot-close:hover {
        opacity: 1;
    }
    
    .chat-messages {
        height: 300px;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.02);
    }
    
    .chat-input-area {
        padding: 1rem;
        border-top: 1px solid rgba(0, 212, 170, 0.2);
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0 0 20px 20px;
    }
    
    .chat-message {
        margin: 0.5rem 0;
        padding: 0.8rem 1rem;
        border-radius: 15px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .chat-message.user {
        background: #00478f;
        color: #ffffff;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-message.bot {
        background: #f1f5f9;
        color: #1f2d3d;
        border: 1px solid #e2e8f0;
    }
    
    /* Progress bar */
    .progress-container {
        background: #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 18px;
        background: #0f766e;
        transition: width 0.3s ease;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: #00478f;
        color: #ffffff;
        border: 1px solid #00478f;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: background 0.25s ease, box-shadow 0.25s ease;
        font-size: 0.95rem;
    }
    
    .stButton > button:hover { background:#005fbf; box-shadow:0 4px 12px rgba(0,0,0,0.15); }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2C3E50, #34495E);
    }
    
    .sidebar-content {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Story narrative styling */
    .story-narrative {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.75rem 1.5rem;
        margin: 1.75rem 0;
        border-left: 5px solid #00478f;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        line-height: 1.55;
        color: #1f2d3d;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .manager-comments {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem 1rem;
        margin: 0.75rem 0 0.5rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        color: #1f2d3d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Policy Definition ---
DEFAULT_POLICY = {
    "pass_rate_min": 0.95,
    "high_pass_rate_min": 0.98,
    "max_blocked_tests": 0,
    "forbid_critical_or_blocked_defects": True,
    "medium_defects_max": 2,
    "minor_defects_note_threshold": 5,
    "weights": {
        "pass_rate": 0.40,
        "high_pass_rate": 0.30,
        "blocked_ratio": 0.15,
        "defect_penalty": 0.15
    }
}

# --- Advanced Features ---
def create_timeline_visualization(phase_data):
    """Create interactive timeline for testing phases"""
    fig = go.Figure()
    
    phases = ['Planning', 'Execution', 'Analysis', 'Review', 'Decision']
    progress = [100, 100, 85, 60, 0]  # Simulated progress
    colors = ['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for i, (phase, prog, color) in enumerate(zip(phases, progress, colors)):
        fig.add_trace(go.Bar(
            x=[prog],
            y=[phase],
            orientation='h',
            marker=dict(color=color, line=dict(color='white', width=2)),
            text=f'{prog}%',
            textposition='inside',
            name=phase
        ))
    
    fig.update_layout(
        title="Testing Phase Progress",
        xaxis_title="Completion %",
        showlegend=False,
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def generate_story_narrative(summary):
    """Generate professional technical report narrative"""
    decision = summary['decision']
    risk_score = summary['risk_score']
    kpis = summary['kpis']
    
    # Technical assessment framework
    quality_grade = "A+" if risk_score < 0.1 else "A" if risk_score < 0.2 else "B" if risk_score < 0.4 else "C"
    
    story = f"""
    ## 📋 **TECHNICAL RELEASE ASSESSMENT REPORT**
    
    ### **Executive Summary**
    This comprehensive analysis evaluates the software release readiness through systematic quality assurance metrics and compliance verification. Our assessment framework has processed **{kpis['total_tests']}** test scenarios with a **{kpis['pass_rate']:.1%}** success rate, resulting in a **Quality Grade {quality_grade}** classification.
    
    ### **🎯 Test Execution Analysis**
    **Test Coverage Metrics:**
    - Total Test Scenarios Executed: **{kpis['total_tests']}**
    - Successful Test Executions: **{kpis['passed']}** ({kpis['pass_rate']:.1%})
    - Blocked Test Scenarios: **{kpis['blocked']}** ({kpis['blocked_ratio']:.1%})
    - Test Execution Efficiency: **{((kpis['total_tests'] - kpis['blocked']) / kpis['total_tests'] * 100):.1f}%**
    
    ### **⭐ Critical Path Validation** 
    **High-Priority Component Assessment:**
    {"No high-priority tests available for assessment" if not kpis['high_pass_rate'] else f'''
    - High-Priority Test Success Rate: **{kpis['high_pass_rate']:.1%}**
    - Critical Component Reliability: **{"VERIFIED" if kpis['high_pass_rate'] > 0.95 else "REQUIRES ATTENTION"}**
    - Business Impact Risk Level: **{"LOW" if kpis['high_pass_rate'] > 0.98 else "MEDIUM" if kpis['high_pass_rate'] > 0.90 else "HIGH"}**
    '''}
    
    ### **🔍 Defect Classification & Impact Analysis**
    **Quality Assurance Findings:**
    - **Critical Severity Issues:** {kpis['defect_counts']['Critical']} {"✅ NONE DETECTED" if kpis['defect_counts']['Critical'] == 0 else "❌ IMMEDIATE ACTION REQUIRED"}
    - **High-Impact Defects:** {kpis['defect_counts']['Medium']} {"(Within acceptable threshold)" if kpis['defect_counts']['Medium'] <= 2 else "(Exceeds quality standards)"}
    - **Minor Issues:** {kpis['defect_counts']['Minor']} {"(Acceptable for release)" if kpis['defect_counts']['Minor'] <= 5 else "(Consider prioritization)"}
    - **Blocked Components:** {kpis['defect_counts']['Blocked']} {"✅ CLEAR" if kpis['defect_counts']['Blocked'] == 0 else "� RELEASE BLOCKER"}
    
    ### **📊 Risk Assessment & Compliance**
    **Quantitative Risk Analysis:**
    - **Overall Risk Score:** {risk_score:.3f} / 1.000
    - **Risk Classification:** {"MINIMAL" if risk_score < 0.2 else "MODERATE" if risk_score < 0.5 else "HIGH"}
    - **Compliance Status:** {"COMPLIANT" if decision == "GO" else "NON-COMPLIANT" if decision == "NO-GO" else "CONDITIONAL COMPLIANCE"}
    
    ### **🎯 RELEASE GATE DECISION**
    **Quality Gate Verdict: {decision}**
    
    {_generate_technical_recommendation(decision, kpis, risk_score)}
    
    ### **📈 Next Phase Actions**
    {"**PRODUCTION DEPLOYMENT AUTHORIZED** - All quality gates satisfied. Proceed with standard deployment procedures." if decision == "GO" else 
     "**CONDITIONAL RELEASE APPROVAL** - Address medium-priority issues. Monitor deployment closely with rollback procedures ready." if decision == "CONDITIONAL" else
     "**RELEASE HOLD** - Critical issues must be resolved. Schedule re-evaluation after defect remediation."}
    
    ---
    *Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Classification: Technical Assessment*
    """
    
    return story

def _generate_technical_recommendation(decision, kpis, risk_score):
    """Generate technical recommendations based on assessment"""
    if decision == "GO":
        return """
        **Technical Assessment: APPROVED FOR PRODUCTION**
        - All critical quality metrics meet or exceed established thresholds
        - System reliability indicators demonstrate production readiness
        - Risk factors are within acceptable operational parameters
        - Deployment confidence level: HIGH (>95%)
        """
    elif decision == "CONDITIONAL":
        return f"""
        **Technical Assessment: CONDITIONAL APPROVAL**
        - Core functionality validated with {kpis['pass_rate']:.1%} success rate
        - Medium-priority defects identified require monitoring during deployment
        - Risk mitigation strategies should be implemented
        - Deployment confidence level: MODERATE (75-95%)
        """
    else:
        return """
        **Technical Assessment: RELEASE BLOCKED**
        - Critical defects present significant operational risk
        - Quality thresholds not met according to established criteria
        - Immediate remediation required before production consideration
        - Deployment confidence level: LOW (<75%)
        """

def create_progress_bar(progress):
    """Create animated progress bar"""
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress}%"></div>
    </div>
    <p style="text-align: center; color: white; margin-top: 0.5rem;">Processing: {progress}%</p>
    """

def get_recommendations(summary):
    """Generate intelligent recommendations"""
    recommendations = []
    decision = summary['decision']
    kpis = summary['kpis']
    
    if decision == "NO-GO":
        recommendations.extend([
            "🔧 **Immediate Action Required**: Address all critical and blocked defects",
            "📊 **Focus Area**: Improve pass rate through targeted bug fixes",
            "⏰ **Timeline**: Plan for additional testing cycle before next gate review"
        ])
    elif decision == "CONDITIONAL":
        recommendations.extend([
            "⚠️ **Monitor Closely**: Track resolution of medium-priority issues",
            "📈 **Improvement Target**: Aim for >95% pass rate in final validation",
            "👥 **Stakeholder Review**: Get business approval for conditional release"
        ])
    else:
        recommendations.extend([
            "✅ **Green Light**: All quality gates passed successfully",
            "🚀 **Ready for Launch**: Proceed with production deployment",
            "📝 **Documentation**: Ensure all release notes are updated"
        ])
    
    return recommendations

def display_chatbot_responses():
    """Display chatbot responses"""
    chatbot_responses = {
        "help": "I'm here to guide you through the release gate process! Ask me about quality metrics, decision criteria, or next steps.",
        "decision": "The release decision is based on pass rates, defect counts, and policy thresholds. Would you like me to explain any specific metric?",
        "improve": "To improve your quality score, focus on: 1) Increasing pass rates 2) Reducing critical defects 3) Minimizing blocked tests",
        "policy": "You can adjust policy settings in the sidebar to match your organization's quality standards."
    }
    return chatbot_responses

# --- Core Functions ---
def normalize_priority(val):
    val = str(val).strip().lower()
    mapping = {
        "high": "High", "normal": "Normal", "low": "Low",
        "critical": "Critical", "crtical": "Critical",
        "medium": "Medium", "minor": "Minor", "blocked": "Blocked"
    }
    return mapping.get(val, val.title())

def compute_kpis(df):
    # Normalize columns
    df['TestCase Priority'] = df['TestCase Priority'].apply(normalize_priority)
    df['Status'] = df['Status'].apply(lambda x: str(x).strip().title())
    if 'Defect priority' in df.columns:
        df['Defect priority'] = df['Defect priority'].apply(normalize_priority)
    else:
        df['Defect priority'] = None

    total = len(df)
    passed = (df['Status'] == 'Pass').sum()
    blocked = (df['Status'] == 'Blocked').sum()
    pass_rate = passed / total if total else 0
    blocked_ratio = blocked / total if total else 0

    # Per-priority pass rates
    high_cases = df[df['TestCase Priority'] == 'High']
    high_passed = (high_cases['Status'] == 'Pass').sum()
    high_total = len(high_cases)
    high_pass_rate = high_passed / high_total if high_total else None

    # Defect priorities
    defect_counts = {}
    if df['Defect priority'].notnull().any():
        for p in ['Blocked', 'Critical', 'Medium', 'Minor']:
            defect_counts[p] = (df['Defect priority'] == p).sum()
    else:
        defect_counts = {'Blocked': 0, 'Critical': 0, 'Medium': 0, 'Minor': 0}

    return {
        "total_tests": total,
        "passed": passed,
        "blocked": blocked,
        "pass_rate": round(pass_rate, 4),
        "blocked_ratio": round(blocked_ratio, 4),
        "high_pass_rate": round(high_pass_rate, 4) if high_pass_rate is not None else None,
        "defect_counts": defect_counts
    }

def gate_decision(kpis, policy):
    reasons = []
    limitations = []
    risk_score = 0

    # Pass rate
    if kpis["pass_rate"] < policy["pass_rate_min"]:
        reasons.append(f"Pass rate {kpis['pass_rate']:.2%} below minimum {policy['pass_rate_min']:.2%}.")
        risk_score += policy["weights"]["pass_rate"]
    else:
        risk_score += policy["weights"]["pass_rate"] * (1 - kpis["pass_rate"])

    # High priority pass rate
    if kpis["high_pass_rate"] is not None:
        if kpis["high_pass_rate"] < policy["high_pass_rate_min"]:
            reasons.append(f"High priority pass rate {kpis['high_pass_rate']:.2%} below minimum {policy['high_pass_rate_min']:.2%}.")
            risk_score += policy["weights"]["high_pass_rate"]
        else:
            risk_score += policy["weights"]["high_pass_rate"] * (1 - kpis["high_pass_rate"])
    else:
        limitations.append("High priority pass rate not available (no high priority tests).")

    # Blocked tests
    if kpis["blocked"] > policy["max_blocked_tests"]:
        reasons.append(f"{kpis['blocked']} blocked tests (max allowed: {policy['max_blocked_tests']}).")
        risk_score += policy["weights"]["blocked_ratio"]
    else:
        risk_score += policy["weights"]["blocked_ratio"] * kpis["blocked_ratio"]

    # Defect priorities
    defect_penalty = 0
    if kpis["defect_counts"] is not None:
        if policy["forbid_critical_or_blocked_defects"]:
            crit = kpis["defect_counts"].get("Critical", 0)
            blocked = kpis["defect_counts"].get("Blocked", 0)
            if crit > 0 or blocked > 0:
                reasons.append(f"{crit} critical and {blocked} blocked defects found (forbidden).")
                defect_penalty += 1
        medium = kpis["defect_counts"].get("Medium", 0)
        if medium > policy["medium_defects_max"]:
            reasons.append(f"{medium} medium defects (max allowed: {policy['medium_defects_max']}).")
            defect_penalty += 0.5
        minor = kpis["defect_counts"].get("Minor", 0)
        if minor > policy["minor_defects_note_threshold"]:
            reasons.append(f"{minor} minor defects (note: threshold {policy['minor_defects_note_threshold']}).")
            defect_penalty += 0.2
        risk_score += policy["weights"]["defect_penalty"] * min(defect_penalty, 1)
    else:
        limitations.append("Defect priority data missing; defect gating skipped.")

    # Decision logic
    if reasons:
        if any("critical" in r.lower() or "blocked defects" in r.lower() for r in reasons):
            decision = "NO-GO"
        else:
            decision = "CONDITIONAL"
    else:
        decision = "GO"

    return {
        "decision": decision,
        "risk_score": round(risk_score, 3),
        "reasons": reasons,
        "kpis": kpis,
        "policy": policy,
        "limitations": "; ".join(limitations) if limitations else ""
    }

# --- Streamlit App ---
def main():
    # Page configuration
    st.set_page_config(
        page_title="ReleaseGate QA Decision Assistant",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    inject_custom_css()
    
    # Main header with dynamic logo
    st.markdown(get_logo_html() + """
    <div class="main-header">
        <div class="release-gate-logo">🚀 ReleaseGate</div>
        <div class="subtitle">Enterprise Quality Decision Platform</div>
        <p style="color: #64748b; margin: 0; font-size: 1.05rem;">Intelligent release decisions through data-driven quality analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'processing_stage' not in st.session_state:
        st.session_state.processing_stage = 0
    if 'manager_comments' not in st.session_state:
        st.session_state.manager_comments = []
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🔧 Policy Configuration")
        st.markdown("*Customize quality thresholds for your organization*")
        
        # Policy inputs
        pass_rate_min = st.slider("Minimum Pass Rate (%)", 0, 100, 95, help="Overall test pass rate threshold") / 100
        high_pass_rate_min = st.slider("High Priority Pass Rate (%)", 0, 100, 98, help="Critical test cases pass rate") / 100
        max_blocked_tests = st.number_input("Max Blocked Tests", min_value=0, value=0, step=1, help="Maximum acceptable blocked test cases")
        forbid_critical = st.checkbox("Forbid Critical Defects", value=True, help="Block release for critical/blocked defects")
        medium_defects_max = st.number_input("Max Medium Defects", min_value=0, value=2, step=1)
        minor_defects_threshold = st.number_input("Minor Defects Warning", min_value=0, value=5, step=1)
        
        # Chatbot toggle
        st.markdown("---")
        show_chatbot = st.checkbox("🤖 Enable AI Assistant", value=True)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📄 Export Options")
        st.markdown("### 📄 Export Options")
        incl_narrative = st.checkbox("Include Narrative", value=True)
        incl_recommend = st.checkbox("Include Recommendations", value=True)
        incl_policy = st.checkbox("Include Policy", value=False)
        generate_now = st.button("� Refresh Export Artifacts", use_container_width=True)

        if 'last_summary' not in st.session_state:
            st.info("Run an analysis to enable exports.")
        else:
            summary = st.session_state.last_summary
            # Rebuild PDF/JSON on demand or first load
            if generate_now or 'cached_pdf' not in st.session_state:
                # Optionally filter sections before PDF generation (basic for now)
                pdf_bytes, err = generate_pdf_report(summary)
                if err:
                    st.error(err)
                else:
                    st.session_state.cached_pdf = pdf_bytes
                st.session_state.cached_json = summary_to_json_bytes(summary)
            if 'cached_pdf' in st.session_state:
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=st.session_state.cached_pdf,
                    file_name=f"releasegate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            if 'cached_json' in st.session_state:
                st.download_button(
                    label="⬇️ Download JSON Data",
                    data=st.session_state.cached_json,
                    file_name=f"releasegate_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        st.markdown("---")
        st.markdown("### 🏷️ Branding")
        st.caption("Upload Allianz UK logo (PNG/SVG/JPG) to display top right. Ensure you have rights to use it.")
        uploaded_logo_file = st.file_uploader("Upload Logo", type=["png","jpg","jpeg","svg"], label_visibility="collapsed")
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            if uploaded_logo_file is not None:
                if st.button("Apply Logo", use_container_width=True):
                    import mimetypes
                    mime, _ = mimetypes.guess_type(uploaded_logo_file.name)
                    ext = uploaded_logo_file.name.split('.')[-1].lower()
                    if ext == 'svg':
                        svg_text = uploaded_logo_file.getvalue().decode('utf-8', errors='ignore')
                        st.session_state.uploaded_logo = { 'type':'svg', 'content': svg_text }
                        st.success("SVG logo applied")
                    else:
                        b64 = base64.b64encode(uploaded_logo_file.getvalue()).decode()
                        mime = mime or ('image/png' if ext=='png' else 'image/jpeg')
                        st.session_state.uploaded_logo = { 'type':'raster', 'b64': b64, 'mime': mime }
                        st.success("Logo applied")
                        st.rerun()
        with col_up2:
            if 'uploaded_logo' in st.session_state:
                if st.button("Remove Logo", use_container_width=True):
                    del st.session_state['uploaded_logo']
                    st.info("Logo removed")
                    st.rerun()
    
    # Update policy
    policy = DEFAULT_POLICY.copy()
    policy.update({
        "pass_rate_min": pass_rate_min,
        "high_pass_rate_min": high_pass_rate_min,
        "max_blocked_tests": int(max_blocked_tests),
        "forbid_critical_or_blocked_defects": forbid_critical,
        "medium_defects_max": int(medium_defects_max),
        "minor_defects_note_threshold": int(minor_defects_threshold)
    })
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Quality Assessment", "📊 Analytics Dashboard", "👥 Manager Portal"])
    
    with tab1:
        # Input method selection
        input_method = st.radio(
            "🔧 Select Input Method:",
            ["📝 Interactive Form", "📁 Excel Upload"],
            horizontal=True
        )
        
        if input_method == "📝 Interactive Form":
            st.markdown("### 📊 Enter Testing Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🎯 Test Execution")
                st.markdown('<div class="interactive-metric">', unsafe_allow_html=True)
                total_tests = st.number_input("Total Tests", min_value=1, value=100, step=1, help="Complete test suite size")
                passed_tests = st.number_input("Passed Tests", min_value=0, max_value=total_tests, value=85, help="Successfully executed tests")
                blocked_tests = st.number_input("Blocked Tests", min_value=0, max_value=total_tests, value=0, help="Tests unable to execute")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Live calculations with enhanced display
                failed_tests = total_tests - passed_tests - blocked_tests
                pass_rate = passed_tests / total_tests if total_tests > 0 else 0
                
                # Interactive metrics display
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📈 Execution Summary</h4>
                    <p><strong>Pass Rate:</strong> <span style="color: {'#00d4aa' if pass_rate >= 0.95 else '#ffaa00' if pass_rate >= 0.85 else '#ff4444'}; font-size: 1.2em;">{pass_rate:.1%}</span></p>
                    <p><strong>Failed Tests:</strong> <span style="color: {'#00d4aa' if failed_tests == 0 else '#ff4444'};">{failed_tests}</span></p>
                    <p><strong>Efficiency Score:</strong> {(pass_rate * 100):.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### ⭐ High Priority Tests")
                st.markdown('<div class="interactive-metric">', unsafe_allow_html=True)
                high_total = st.number_input("High Priority Total", min_value=0, value=20, help="Critical functionality tests")
                high_passed = st.number_input("High Priority Passed", min_value=0, max_value=high_total, value=19, help="Successful critical tests")
                st.markdown('</div>', unsafe_allow_html=True)
                
                high_pass_rate = high_passed / high_total if high_total > 0 else 0
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>⭐ Critical Path Analysis</h4>
                    <p><strong>High Priority Rate:</strong> <span style="color: {'#00d4aa' if high_pass_rate >= 0.98 else '#ffaa00' if high_pass_rate >= 0.90 else '#ff4444'}; font-size: 1.2em;">{high_pass_rate:.1%}</span></p>
                    <p><strong>Risk Level:</strong> <span style="color: {'#00d4aa' if high_pass_rate >= 0.98 else '#ffaa00' if high_pass_rate >= 0.90 else '#ff4444'};">{'LOW' if high_pass_rate >= 0.98 else 'MEDIUM' if high_pass_rate >= 0.90 else 'HIGH'}</span></p>
                    <p><strong>Business Impact:</strong> {'MINIMAL' if high_pass_rate >= 0.95 else 'MODERATE' if high_pass_rate >= 0.85 else 'SIGNIFICANT'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("#### 🐛 Defect Classification")
                st.markdown('<div class="interactive-metric">', unsafe_allow_html=True)
                critical_defects = st.number_input("Critical Defects", min_value=0, value=0, help="Production blockers")
                blocked_defects = st.number_input("Blocked Defects", min_value=0, value=0, help="Environment/dependency issues")
                medium_defects = st.number_input("Medium Defects", min_value=0, value=1, help="Functionality issues")
                minor_defects = st.number_input("Minor Defects", min_value=0, value=3, help="Cosmetic/minor issues")
                st.markdown('</div>', unsafe_allow_html=True)
                
                total_defects = critical_defects + blocked_defects + medium_defects + minor_defects
                severity_score = (critical_defects * 10) + (blocked_defects * 8) + (medium_defects * 3) + (minor_defects * 1)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🐛 Quality Assessment</h4>
                    <p><strong>Total Defects:</strong> <span style="font-size: 1.2em; color: {'#00d4aa' if total_defects <= 5 else '#ffaa00' if total_defects <= 10 else '#ff4444'};">{total_defects}</span></p>
                    <p><strong>Severity Score:</strong> <span style="color: {'#00d4aa' if severity_score <= 10 else '#ffaa00' if severity_score <= 25 else '#ff4444'};">{severity_score}/100</span></p>
                    <p><strong>Quality Status:</strong> {'EXCELLENT' if severity_score <= 5 else 'GOOD' if severity_score <= 15 else 'NEEDS ATTENTION'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Generate decision
            if st.button("🎯 Analyze Release Readiness", type="primary", use_container_width=True):
                # Create KPIs
                kpis = {
                    "total_tests": int(total_tests),
                    "passed": int(passed_tests),
                    "blocked": int(blocked_tests),
                    "pass_rate": round(pass_rate, 4),
                    "blocked_ratio": round(blocked_tests / total_tests, 4) if total_tests > 0 else 0,
                    "high_pass_rate": round(high_pass_rate, 4) if high_total > 0 else None,
                    "defect_counts": {
                        "Critical": int(critical_defects),
                        "Blocked": int(blocked_defects),
                        "Medium": int(medium_defects),
                        "Minor": int(minor_defects)
                    }
                }
                
                # Show processing animation
                progress_bar = st.empty()
                for i in range(0, 101, 20):
                    progress_bar.markdown(create_progress_bar(i), unsafe_allow_html=True)
                    time.sleep(0.1)
                
                progress_bar.empty()
                
                # Generate decision
                summary = gate_decision(kpis, policy)
                persist_summary(summary)
                display_results(summary)
        
        else:
            st.markdown("### 📁 Excel File Analysis")
            uploaded_file = st.file_uploader(
                "Upload your test results",
                type=['xlsx', 'xls'],
                help="Upload Excel file with test results and defect data"
            )
            
            if uploaded_file:
                # Processing animation
                with st.spinner("🔄 Processing Excel file..."):
                    progress_bar = st.empty()
                    for i in range(0, 101, 25):
                        progress_bar.markdown(create_progress_bar(i), unsafe_allow_html=True)
                        time.sleep(0.3)
                    progress_bar.empty()
                
                try:
                    df = pd.read_excel(uploaded_file)
                    st.success(f"✅ Successfully loaded {len(df)} records")
                    
                    # Preview
                    with st.expander("📋 Data Preview"):
                        st.dataframe(df.head())
                    
                    # Timeline visualization
                    st.markdown("### 📈 Processing Timeline")
                    timeline_fig = create_timeline_visualization({})
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    if st.button("🔍 Analyze Excel Data", type="primary"):
                        kpis = compute_kpis(df)
                        summary = gate_decision(kpis, policy)
                        persist_summary(summary)
                        display_results(summary)
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
    
    with tab2:
        st.markdown("### 📊 Analytics Dashboard")
        st.info("📈 Advanced analytics and trend analysis coming soon!")
        
        # Placeholder for analytics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📈 Trend Analysis")
            st.line_chart([85, 90, 88, 95, 92])
        
        with col2:
            st.markdown("#### 🎯 Quality Metrics")
            st.bar_chart({"Pass Rate": 85, "Coverage": 90, "Defect Rate": 15})
    
    with tab3:
        st.markdown("### 👥 Manager Portal")
        
        # Manager comments section
        st.markdown("#### 💬 Manager Comments & Actions")
        
        comment_text = st.text_area("Add your comments:", placeholder="Enter release notes, approvals, or next steps...")
        priority = st.selectbox("Priority Level:", ["Low", "Medium", "High", "Critical"])
        
        if st.button("💾 Add Comment", type="secondary"):
            if comment_text:
                st.session_state.manager_comments.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "comment": comment_text,
                    "priority": priority,
                    "author": "Release Manager"
                })
                st.success("Comment added successfully!")
        
        # Display comments
        if st.session_state.manager_comments:
            st.markdown("#### 📋 Comment History")
            for comment in st.session_state.manager_comments:
                st.markdown(f"""
                <div class="manager-comments">
                    <strong>🕒 {comment['timestamp']}</strong> | 
                    <span style="color: {'red' if comment['priority'] == 'Critical' else 'orange' if comment['priority'] == 'High' else 'blue'};">
                        {comment['priority']} Priority
                    </span><br>
                    <p>{comment['comment']}</p>
                    <small>- {comment['author']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Chatbot (render if enabled)
    if show_chatbot:
        display_chatbot_ui()

def display_results(summary):
    """Display release decision results"""
    decision = summary['decision']
    
    # Decision display
    if decision == "GO":
        st.markdown('<div class="decision-go">🚀 GO - Release Approved</div>', unsafe_allow_html=True)
    elif decision == "NO-GO":
        st.markdown('<div class="decision-nogo">🛑 NO-GO - Release Blocked</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="decision-conditional">⚠️ CONDITIONAL - Review Required</div>', unsafe_allow_html=True)
    
    # Risk score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Score", f"{summary['risk_score']:.3f}")
    with col2:
        st.metric("Total Tests", summary['kpis']['total_tests'])
    with col3:
        st.metric("Pass Rate", f"{summary['kpis']['pass_rate']:.1%}")
    
    # Story narrative
    st.markdown("### 📖 Release Story")
    story = generate_story_narrative(summary)
    st.markdown(f'<div class="story-narrative">{story}</div>', unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    recommendations = get_recommendations(summary)
    for rec in recommendations:
        st.markdown(f"• {rec}")
    
    # Detailed results in tabs (improved readability)
    tab1, tab2, tab3 = st.tabs(["📊 KPIs", "⚠️ Issues", "📋 Policy"])

    with tab1:
        kpis = summary['kpis']
        kcol1, kcol2, kcol3 = st.columns(3)
        with kcol1:
            st.metric("Total Tests", kpis['total_tests'])
            st.metric("Passed", kpis['passed'])
        with kcol2:
            st.metric("Blocked", kpis['blocked'])
            st.metric("Blocked %", f"{kpis['blocked_ratio']:.1%}")
        with kcol3:
            st.metric("Pass Rate", f"{kpis['pass_rate']:.1%}")
            st.metric("High Priority Rate", "N/A" if kpis['high_pass_rate'] is None else f"{kpis['high_pass_rate']:.1%}")

        st.markdown("#### Defect Breakdown")
        defect_counts = kpis['defect_counts']
        dtable = pd.DataFrame([
            {"Severity":"Blocked","Count": defect_counts.get('Blocked',0)},
            {"Severity":"Critical","Count": defect_counts.get('Critical',0)},
            {"Severity":"Medium","Count": defect_counts.get('Medium',0)},
            {"Severity":"Minor","Count": defect_counts.get('Minor',0)}
        ])
        st.table(dtable)
        with st.expander("Show Raw KPI JSON"):
            st.code(json.dumps(kpis, indent=2), language="json")

    with tab2:
        if summary['reasons']:
            for reason in summary['reasons']:
                st.error(f"❌ {reason}")
        else:
            st.success("✅ No gating issues found!")

    with tab3:
        policy = summary['policy']
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Min Pass Rate", f"{policy['pass_rate_min']:.0%}")
            st.metric("High Pri Min", f"{policy['high_pass_rate_min']:.0%}")
        with p2:
            st.metric("Max Blocked", policy['max_blocked_tests'])
            st.metric("Medium Defects Max", policy['medium_defects_max'])
        with p3:
            st.metric("Minor Defects Note", policy['minor_defects_note_threshold'])
            st.metric("Forbid Critical", "Yes" if policy['forbid_critical_or_blocked_defects'] else "No")
        st.markdown("#### Weight Configuration")
        w = policy['weights']
        wdf = pd.DataFrame([
            {"Component":"Pass Rate","Weight": w['pass_rate']},
            {"Component":"High Priority","Weight": w['high_pass_rate']},
            {"Component":"Blocked Ratio","Weight": w['blocked_ratio']},
            {"Component":"Defect Penalty","Weight": w['defect_penalty']}
        ])
        st.table(wdf)
        with st.expander("Show Raw Policy JSON"):
            st.code(json.dumps(policy, indent=2), language="json")

def display_chatbot_ui():
    """Display interactive chatbot interface (stateless UI with localStorage)."""
    # Initial seed messages (rendered as HTML only)
    initial_messages_html = '<div class="chat-message bot">Hello! I\'m your ReleaseGate AI Assistant. Ask about metrics, risk score, defects or next steps.</div>'

    st.markdown("""
    <div class="chatbot-toggle" onclick="window.__toggleChatbot && window.__toggleChatbot()">🤖</div>
    <div class="chatbot-container" id="chatbotContainer">
        <div class="chatbot-header">
            <span>ReleaseGate Assistant</span>
            <span class="chatbot-close" onclick="window.__toggleChatbot()">✖</span>
        </div>
        <div class="chat-messages" id="chatMessages">""" + initial_messages_html + """</div>
        <div class="chat-input-area">
            <div style="display:flex; gap:8px;">
                <input type="text" id="chatInput" placeholder="Ask about quality metrics..." style="flex:1; padding:8px; border:1px solid #cbd5e1; border-radius:8px;" onkeypress="if(event.key==='Enter'){window.__sendChat && window.__sendChat();}">
                <button onclick="window.__sendChat()" style="padding:8px 14px; background:#00478f; color:#fff; border:1px solid #00478f; border-radius:8px; cursor:pointer;">Send</button>
            </div>
            <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:6px;">
                <button onclick="window.__quickChat('How to improve pass rate?')" class="quick-btn">📈 Improve Pass Rate</button>
                <button onclick="window.__quickChat('Explain risk score')" class="quick-btn">🎯 Risk Score</button>
                <button onclick="window.__quickChat('Policy recommendations')" class="quick-btn">⚙️ Policy Help</button>
                <button onclick="window.__quickChat('Next steps for release')" class="quick-btn">🚀 Next Steps</button>
            </div>
        </div>
    </div>
    <script>
    (function(){
        const STORAGE_KEY = 'releasegate_chat_state_v1';
        const MSG_KEY = 'releasegate_chat_messages_v1';
        function loadState(){
            try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {open:false}; } catch(e){ return {open:false}; }
        }
        function saveState(s){ localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); }
        function loadMessages(){
            try { return JSON.parse(localStorage.getItem(MSG_KEY)) || []; } catch(e){ return []; }
        }
        function saveMessages(msgs){ localStorage.setItem(MSG_KEY, JSON.stringify(msgs)); }
        const container = document.getElementById('chatbotContainer');
        const messagesDiv = document.getElementById('chatMessages');
        const inputEl = document.getElementById('chatInput');
        let state = loadState();
        let messages = loadMessages();
        function renderMessages(){
            if(messages.length){
                messagesDiv.innerHTML = messages.map(m=>`<div class='chat-message ${m.role}'>${m.content}</div>`).join('');
            }
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        function addMessage(content, role){
            messages.push({content, role});
            saveMessages(messages);
            renderMessages();
        }
        function botResponse(userText){
            const catalog = {
                'pass rate': '📈 Improve pass rate: fix failing tests, stabilize environments, refine flaky cases, prioritize high-impact scenarios.',
                'risk score': '🎯 Risk score weights: Pass Rate 40%, High-Priority 30%, Blocked 15%, Defects 15%. Lower = better.',
                'policy': '⚙️ Adjust sidebar thresholds to align with criticality. Stricter for production, moderate for staging.',
                'next steps': '🚀 GO: deploy; CONDITIONAL: address medium issues & monitor; NO-GO: remediate critical blockers first.',
                'improve': '💡 Raise quality via automation, CI discipline, root cause analysis, and proactive defect triage.',
                'defects': '🐛 Critical/Blocked: immediate fix; Medium: planned sprint; Minor: backlog grooming.',
                'timeline': '⏰ Typical cycle: Planning→Execution→Analysis→Review→Decision.'
            };
            const lt = userText.toLowerCase();
            for (const k in catalog){ if(lt.includes(k)) return catalog[k]; }
            return '🤖 I can help with metrics, policy, risk, defects, and release readiness. Ask: pass rate, risk score, defects, next steps.';
        }
        window.__toggleChatbot = function(){
            state.open = !state.open; saveState(state); applyState(); };
        function applyState(){ if(state.open){ container.classList.add('active'); } else { container.classList.remove('active'); } }
        window.__sendChat = function(){ const txt = inputEl.value.trim(); if(!txt) return; addMessage(txt, 'user'); inputEl.value=''; setTimeout(()=>{ addMessage(botResponse(txt),'bot'); }, 400); };
        window.__quickChat = function(q){ addMessage(q,'user'); setTimeout(()=>{ addMessage(botResponse(q),'bot'); }, 350); };
        // Initialize
        applyState(); renderMessages();
    })();
    </script>
    <style>
      .quick-btn { padding:6px 10px; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:12px; font-size:12px; cursor:pointer; color:#0f172a; }
      .quick-btn:hover { background:#e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()