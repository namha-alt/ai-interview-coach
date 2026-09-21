"""AI Interview Coach - Streamlit Application.
Main entrypoint and stage routing (setup -> analysis -> interview -> report).
"""

import streamlit as st
import pandas as pd
from config import (
    MODES,
    DIFFICULTY_LEVELS,
    DEFAULT_QUESTIONS,
    MIN_QUESTIONS,
    MAX_QUESTIONS,
    validate_config,
)
from utils import (
    extract_text_from_pdf,
    truncate_text,
    compute_aggregate_scores,
)
from samples import (
    SAMPLE_RESUME,
    SAMPLE_JD,
    DEMO_QUESTIONS,
    DEMO_ANSWERS,
)
from analysis import (
    analyze_gap,
    get_next_question,
    score_answer,
    generate_report,
)
from charts import make_radar_chart
from exporter import build_markdown, build_pdf

# Set page config
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, modern UI
st.markdown(
    """
    <style>
    /* Global styling enhancements */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .skill-badge-matched {
        display: inline-block;
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        margin: 0.25rem;
        border: 1px solid #86EFAC;
    }
    .skill-badge-high {
        display: inline-block;
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        margin: 0.25rem;
        border: 1px solid #FCA5A5;
    }
    .skill-badge-med {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        margin: 0.25rem;
        border: 1px solid #FDE68A;
    }
    .skill-badge-low {
        display: inline-block;
        background-color: #E0F2FE;
        color: #075985;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        margin: 0.25rem;
        border: 1px solid #BAE6FD;
    }
    .interview-q-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
        border-left: 5px solid #2563EB;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        margin: 1.2rem 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1E293B;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08);
    }
    .demo-box {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initializes default session state variables."""
    defaults = {
        "stage": "setup",  # setup -> analysis -> interview -> report
        "resume_text": "",
        "jd_text": "",
        "mode": "Technical",
        "level": "Mid-level",
        "n_questions": DEFAULT_QUESTIONS,
        "demo_mode": False,
        "gap": None,
        "history": [],  # list of {question, answer, score}
        "current_q": "",
        "report_md": "",
        "radar_png": None,
        "score_df": None,
        "avg_scores": None,
        "error_msg": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


def reset_interview():
    """Clears interview progress and returns to setup stage."""
    st.session_state.stage = "setup"
    st.session_state.resume_text = ""
    st.session_state.jd_text = ""
    st.session_state.demo_mode = False
    st.session_state.gap = None
    st.session_state.history = []
    st.session_state.current_q = ""
    st.session_state.report_md = ""
    st.session_state.radar_png = None
    st.session_state.score_df = None
    st.session_state.avg_scores = None
    st.session_state.error_msg = None
    st.rerun()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🎯 AI Interview Coach")
    st.caption("Powered by Azure AI Foundry")

    # Environment Validation Status
    is_valid_env, missing_keys = validate_config()
    if is_valid_env:
        st.success("🟢 Azure AI Foundry Connected", icon="✅")
    else:
        st.warning(
            f"⚠️ Missing Azure OpenAI Config:\n`{', '.join(missing_keys)}`\nPlease configure `.env` file.",
            icon="⚠️",
        )

    st.markdown("---")
    st.subheader("Interview Settings")
    st.write(f"**Stage:** `{st.session_state.stage.upper()}`")
    st.write(f"**Mode:** {st.session_state.mode}")
    st.write(f"**Seniority:** {st.session_state.level}")
    st.write(f"**Total Questions:** {st.session_state.n_questions}")
    if st.session_state.demo_mode:
        st.info("⚡ Presentation Demo Mode Active")

    if st.session_state.stage in ["interview", "report"]:
        completed = len(st.session_state.history)
        st.write(f"**Progress:** {completed} / {st.session_state.n_questions} Questions")

    st.markdown("---")
    if st.button("🔄 Reset / Start New Interview", use_container_width=True):
        reset_interview()

    st.markdown("---")
    st.caption(
        "💡 **Responsible AI Notice:**\n"
        "This tool provides coaching insights and mock interview preparation. "
        "It is not used for actual hiring decisions. Resume data is processed in-session only."
    )


# ==========================================
# STAGE 1: SETUP
# ==========================================
if st.session_state.stage == "setup":
    st.markdown('<div class="main-header">🎯 AI Interview Coach</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Upload your resume and the target job description to practice personalized, high-impact mock interviews tailored to your exact skill gaps.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)
        st.session_state.error_msg = None

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Candidate Resume")
        uploaded_pdf = st.file_uploader(
            "Upload your Resume (PDF format only)",
            type=["pdf"],
            help="Your PDF will be extracted locally and analyzed against the job description.",
        )
        
        sample_col1, sample_col2 = st.columns([1, 1])
        with sample_col1:
            if st.button("📋 Load Sample Profile & JD", help="Loads pre-configured sample resume & JD for quick testing"):
                st.session_state.resume_text = SAMPLE_RESUME
                st.session_state.jd_text = SAMPLE_JD
                st.session_state.mode = "Technical"
                st.session_state.level = "Mid-level"
                st.rerun()
        with sample_col2:
            if st.session_state.resume_text:
                st.caption(f"✓ Resume text loaded ({len(st.session_state.resume_text)} chars)")

        st.subheader("2. Target Job Description")
        jd_input = st.text_area(
            "Paste the complete Job Description (JD)",
            value=st.session_state.jd_text,
            height=240,
            placeholder="Paste responsibilities, requirements, and tech stack here...",
        )

    with col2:
        st.subheader("3. Interview Configuration")
        
        demo_mode_val = st.checkbox(
            "⚡ Presentation Demo Mode (3 Relatable Questions + 1-Click Fast Answers)",
            value=st.session_state.demo_mode,
            help="Designed for 5-minute class presentations: uses 3 relatable student-friendly questions and 1-click answer buttons.",
        )

        mode_val = st.selectbox(
            "Interview Mode",
            options=MODES,
            index=MODES.index(st.session_state.mode) if st.session_state.mode in MODES else 0,
            help=(
                "- Technical: Deep dive into tools, systems, code, and debugging.\n"
                "- HR/Behavioral: STAR-method questions on leadership, conflict, and teamwork.\n"
                "- Mixed: 60% technical + 40% behavioral."
            ),
        )

        level_val = st.selectbox(
            "Target Seniority Level",
            options=DIFFICULTY_LEVELS,
            index=DIFFICULTY_LEVELS.index(st.session_state.level) if st.session_state.level in DIFFICULTY_LEVELS else 1,
            help="Adjusts difficulty, complexity of scenarios, and depth expectation.",
        )

        default_q_count = 3 if demo_mode_val else st.session_state.n_questions
        n_questions_val = st.slider(
            "Number of Interview Questions",
            min_value=MIN_QUESTIONS,
            max_value=MAX_QUESTIONS,
            value=default_q_count,
            step=1,
            help="Choose between 3 to 15 questions for the mock interview session.",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Analyze Fit & Start Interview", type="primary", use_container_width=True)

    if start_btn:
        if not uploaded_pdf and not st.session_state.resume_text:
            st.warning("⚠️ Please upload a resume in PDF format (or click 'Load Sample Profile & JD').")
        elif not jd_input.strip():
            st.warning("⚠️ Please paste the target Job Description.")
        else:
            with st.spinner("Extracting resume and running pre-interview gap analysis..."):
                try:
                    # Extract text from uploaded PDF
                    if uploaded_pdf:
                        extracted_text, warn_msg = extract_text_from_pdf(uploaded_pdf)
                        if warn_msg:
                            st.warning(warn_msg)
                        resume_text = extracted_text
                    else:
                        resume_text = st.session_state.resume_text

                    # Truncate if excessively long
                    safe_resume, r_trunc = truncate_text(resume_text)
                    safe_jd, j_trunc = truncate_text(jd_input)

                    # Update session state
                    st.session_state.resume_text = safe_resume
                    st.session_state.jd_text = safe_jd
                    st.session_state.mode = mode_val
                    st.session_state.level = level_val
                    st.session_state.demo_mode = demo_mode_val
                    st.session_state.n_questions = 3 if demo_mode_val else n_questions_val

                    # Run Gap Analysis
                    gap_result = analyze_gap(safe_resume, safe_jd)
                    st.session_state.gap = gap_result
                    st.session_state.stage = "analysis"
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during setup and gap analysis: {str(e)}")


# ==========================================
# STAGE 2: PRE-INTERVIEW GAP ANALYSIS
# ==========================================
elif st.session_state.stage == "analysis":
    st.markdown('<div class="main-header">📊 Pre-Interview Gap Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Review your alignment with the target role before the interview begins. The AI interviewer will tailor questions to probe identified gaps.</div>',
        unsafe_allow_html=True,
    )

    gap = st.session_state.gap
    if gap is None:
        st.warning("No gap analysis data found. Returning to setup.")
        st.session_state.stage = "setup"
        st.rerun()

    # Match Score & Summary Metric
    m_col1, m_col2 = st.columns([1, 3], gap="medium")
    with m_col1:
        match_val = gap.match_score if hasattr(gap, "match_score") else gap.get("match_score", 0)
        st.metric(label="🎯 Role Match Score", value=f"{match_val} / 100")
        st.progress(max(0, min(100, match_val)) / 100.0)

    with m_col2:
        summary_val = gap.summary if hasattr(gap, "summary") else gap.get("summary", "")
        st.markdown(f"**Executive Fit Summary:**\n\n{summary_val}")

    st.markdown("---")

    # Matched vs Missing Skills
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.subheader("✅ Matched Skills & Strengths")
        matched = gap.matched_skills if hasattr(gap, "matched_skills") else gap.get("matched_skills", [])
        if matched:
            chips_html = "".join([f'<span class="skill-badge-matched">✓ {skill}</span>' for skill in matched])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("No explicit skill matches found in resume.")

        st.markdown("<br>", unsafe_allow_html=True)
        weak = gap.weak_areas if hasattr(gap, "weak_areas") else gap.get("weak_areas", [])
        if weak:
            with st.expander("🔍 Weak / Low-Evidence Resume Areas", expanded=True):
                for item in weak:
                    st.markdown(f"- **{item}**")

    with c2:
        st.subheader("⚠️ Missing / Required Skills")
        missing = gap.missing_skills if hasattr(gap, "missing_skills") else gap.get("missing_skills", [])
        if missing:
            for item in missing:
                skill_name = item.skill if hasattr(item, "skill") else item.get("skill", "")
                importance = (item.importance if hasattr(item, "importance") else item.get("importance", "medium")).lower()
                reason = item.reason if hasattr(item, "reason") else item.get("reason", "")
                
                badge_class = "skill-badge-high" if importance == "high" else "skill-badge-med" if importance == "medium" else "skill-badge-low"
                
                st.markdown(
                    f'<span class="{badge_class}">! {skill_name} ({importance.capitalize()})</span> - {reason}',
                    unsafe_allow_html=True,
                )
        else:
            st.success("No critical skill gaps identified!")

        st.markdown("<br>", unsafe_allow_html=True)
        flags = gap.resume_red_flags if hasattr(gap, "resume_red_flags") else gap.get("resume_red_flags", [])
        if flags:
            with st.expander("🚩 Resume Red Flags & Formatting Gaps", expanded=False):
                for f in flags:
                    st.markdown(f"- {f}")

    st.markdown("---")
    b_col1, b_col2, _ = st.columns([2, 1, 3])

    with b_col1:
        if st.button("🎙️ Begin Live Mock Interview", type="primary", use_container_width=True):
            with st.spinner("Preparing your personalized opening interview question..."):
                try:
                    if st.session_state.demo_mode and len(DEMO_QUESTIONS) > 0:
                        first_q = DEMO_QUESTIONS[0]
                    else:
                        first_q = get_next_question(
                            resume_text=st.session_state.resume_text,
                            jd_text=st.session_state.jd_text,
                            gaps=st.session_state.gap,
                            mode=st.session_state.mode,
                            level=st.session_state.level,
                            history=[],
                            current_q_idx=0,
                            total_questions=st.session_state.n_questions,
                        )
                    st.session_state.current_q = first_q
                    st.session_state.stage = "interview"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate first question: {str(e)}")

    with b_col2:
        if st.button("⬅️ Back to Setup", use_container_width=True):
            st.session_state.stage = "setup"
            st.rerun()


# ==========================================
# STAGE 3: INTERACTIVE INTERVIEW
# ==========================================
elif st.session_state.stage == "interview":
    current_idx = len(st.session_state.history)
    total_q = st.session_state.n_questions

    st.markdown('<div class="main-header">🎙️ Live Mock Interview</div>', unsafe_allow_html=True)

    # Progress indicator
    progress_val = min(1.0, current_idx / float(total_q))
    st.progress(progress_val)
    st.caption(f"**Question {current_idx + 1} of {total_q}** | Mode: *{st.session_state.mode}* | Level: *{st.session_state.level}*")

    # Render previous dialogue turns
    for idx, turn in enumerate(st.session_state.history):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**Question {idx + 1}:** {turn['question']}")
        with st.chat_message("user", avatar="👤"):
            st.markdown(turn["answer"])

    # Active Question Display
    if st.session_state.current_q:
        st.markdown(
            f'<div class="interview-q-box"><b>Interviewer:</b> {st.session_state.current_q}</div>',
            unsafe_allow_html=True,
        )

    # 1-Click Presentation Demo Helper
    demo_selected_answer = None
    if st.session_state.demo_mode and current_idx < len(DEMO_ANSWERS):
        sample_ans = DEMO_ANSWERS[current_idx]
        with st.container():
            st.markdown(
                f'<div class="demo-box">💡 <b>5-Min Presentation Quick-Answer:</b><br><i>"{sample_ans}"</i></div>',
                unsafe_allow_html=True,
            )
            if st.button("⚡ 1-Click Submit Demo Answer", key=f"demo_btn_{current_idx}", type="secondary", use_container_width=True):
                demo_selected_answer = sample_ans

    # Candidate text-only input via st.chat_input
    candidate_answer = st.chat_input(
        placeholder=f"Type your answer to Question {current_idx + 1} here and press Enter..."
    )

    final_answer = demo_selected_answer or (candidate_answer.strip() if candidate_answer else None)

    if final_answer:
        cleaned_answer = final_answer.strip()
        if not cleaned_answer:
            st.warning("⚠️ Answer cannot be empty. Please type your response.")
        else:
            with st.spinner("Scoring response silently & preparing next turn..."):
                try:
                    # 1. Silently score the current answer
                    score_res = score_answer(
                        question=st.session_state.current_q,
                        answer=cleaned_answer,
                        jd_text=st.session_state.jd_text,
                        mode=st.session_state.mode,
                        level=st.session_state.level,
                    )

                    # 2. Append to history
                    st.session_state.history.append({
                        "question": st.session_state.current_q,
                        "answer": cleaned_answer,
                        "score": score_res,
                    })

                    # 3. Check termination condition
                    if len(st.session_state.history) >= total_q:
                        # Interview finished -> Generate final report & radar chart
                        with st.spinner("Synthesizing comprehensive final coaching report..."):
                            avg_scores = compute_aggregate_scores(st.session_state.history)
                            st.session_state.avg_scores = avg_scores
                            st.session_state.radar_png = make_radar_chart(avg_scores)
                            
                            # Build score dataframe
                            table_rows = []
                            for i, t in enumerate(st.session_state.history):
                                sc = t["score"]
                                r = sc.relevance if hasattr(sc, "relevance") else sc.get("relevance", 0)
                                d = sc.depth if hasattr(sc, "depth") else sc.get("depth", 0)
                                s = sc.structure if hasattr(sc, "structure") else sc.get("structure", 0)
                                c = sc.clarity if hasattr(sc, "clarity") else sc.get("clarity", 0)
                                a = round((r + d + s + c) / 4.0, 2)
                                table_rows.append({
                                    "#": i + 1,
                                    "Question": t["question"],
                                    "Relevance": r,
                                    "Depth": d,
                                    "Structure": s,
                                    "Clarity": c,
                                    "Avg": a,
                                })
                            st.session_state.score_df = pd.DataFrame(table_rows)

                            # Generate final markdown report
                            report_text = generate_report(
                                resume_text=st.session_state.resume_text,
                                jd_text=st.session_state.jd_text,
                                gap=st.session_state.gap,
                                history=st.session_state.history,
                                avg_scores=avg_scores,
                            )
                            st.session_state.report_md = report_text
                            st.session_state.stage = "report"
                            st.rerun()
                    else:
                        # Generate next question
                        if st.session_state.demo_mode and len(st.session_state.history) < len(DEMO_QUESTIONS):
                            next_q = DEMO_QUESTIONS[len(st.session_state.history)]
                        else:
                            next_q = get_next_question(
                                resume_text=st.session_state.resume_text,
                                jd_text=st.session_state.jd_text,
                                gaps=st.session_state.gap,
                                mode=st.session_state.mode,
                                level=st.session_state.level,
                                history=st.session_state.history,
                                current_q_idx=len(st.session_state.history),
                                total_questions=total_q,
                            )
                        st.session_state.current_q = next_q
                        st.rerun()

                except Exception as e:
                    st.error(f"Error processing interview answer: {str(e)}")


# ==========================================
# STAGE 4: FINAL REPORT & VISUALS
# ==========================================
elif st.session_state.stage == "report":
    st.markdown('<div class="main-header">📈 Final Interview Assessment & Report</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Congratulations on completing your interview! Review your score breakdown, radar chart, skill gap evaluation, and actionable recommendations below.</div>',
        unsafe_allow_html=True,
    )

    avg_scores = st.session_state.avg_scores or compute_aggregate_scores(st.session_state.history)
    radar_png = st.session_state.radar_png
    score_df = st.session_state.score_df
    report_md = st.session_state.report_md

    # Top Metric Cards & Radar Chart
    r_col1, r_col2 = st.columns([1, 1], gap="large")

    with r_col1:
        st.subheader("Performance Metrics (Scale 1 - 10)")
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            st.metric("Overall Average", f"{avg_scores.get('overall', 0)} / 10")
            st.metric("Relevance", f"{avg_scores.get('relevance', 0)} / 10")
            st.metric("Structure", f"{avg_scores.get('structure', 0)} / 10")
        with sc_col2:
            st.metric("Target Seniority", st.session_state.level)
            st.metric("Technical / Domain Depth", f"{avg_scores.get('depth', 0)} / 10")
            st.metric("Clarity & Delivery", f"{avg_scores.get('clarity', 0)} / 10")

    with r_col2:
        if radar_png:
            st.image(radar_png, caption="Competency Radar Chart", use_container_width=True)

    st.markdown("---")

    # Score Breakdown Table
    st.subheader("📋 Per-Question Score Breakdown")
    if score_df is not None and not score_df.empty:
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    # Detailed Turn-by-Turn Expanders
    with st.expander("🔍 View Question-by-Question Strengths & Sample Answers", expanded=False):
        for idx, turn in enumerate(st.session_state.history):
            sc = turn["score"]
            strengths = sc.strengths if hasattr(sc, "strengths") else sc.get("strengths", "")
            weaknesses = sc.weaknesses if hasattr(sc, "weaknesses") else sc.get("weaknesses", "")
            improved = sc.improved_answer if hasattr(sc, "improved_answer") else sc.get("improved_answer", "")

            st.markdown(f"### Question {idx + 1}: {turn['question']}")
            st.markdown(f"**Your Answer:** {turn['answer']}")
            st.success(f"**Strengths:** {strengths}")
            st.warning(f"**Areas for Improvement:** {weaknesses}")
            st.info(f"**Ideal High-Scoring Response (STAR):**\n\n{improved}")
            st.markdown("---")

    st.markdown("---")

    # Full Markdown Report
    st.subheader("📑 Detailed Assessment & 2-Week Action Plan")
    st.markdown(report_md)

    st.markdown("---")

    # Downloads & Action Buttons
    meta_dict = {
        "mode": st.session_state.mode,
        "level": st.session_state.level,
        "n_questions": st.session_state.n_questions,
    }

    full_md_export = build_markdown(
        report_md=report_md,
        score_df=score_df,
        gap_data=st.session_state.gap,
        avg_scores=avg_scores,
        metadata=meta_dict,
    )

    pdf_bytes = None
    try:
        pdf_bytes = build_pdf(
            report_md=report_md,
            radar_png=radar_png,
            score_df=score_df,
            gap_data=st.session_state.gap,
            avg_scores=avg_scores,
            metadata=meta_dict,
        )
    except Exception as e:
        st.warning(f"⚠️ Note: PDF compilation encountered an issue: {str(e)}. Markdown download is fully available below.")

    d_col1, d_col2, d_col3 = st.columns([1, 1, 1], gap="medium")

    with d_col1:
        st.download_button(
            label="📥 Download Report as Markdown (.md)",
            data=full_md_export,
            file_name=f"interview_coach_report_{st.session_state.mode.lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with d_col2:
        if pdf_bytes:
            st.download_button(
                label="📄 Download Report as PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"interview_coach_report_{st.session_state.mode.lower()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("📄 PDF Unavailable", disabled=True, use_container_width=True)

    with d_col3:
        if st.button("🔄 Start New Mock Interview", type="primary", use_container_width=True):
            reset_interview()
