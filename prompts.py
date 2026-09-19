"""Prompt templates and builders for Gap Analysis, Interviewing, Scoring, and Reporting."""

import json


def build_gap_analysis_prompt(resume_text: str, jd_text: str) -> list[dict[str, str]]:
    """
    Constructs the prompt for comparing the resume and job description to identify
    match score, matched skills, missing skills, weak areas, and resume red flags in JSON.
    """
    system_prompt = (
        "You are an expert technical recruiter and talent assessor. "
        "Your task is to conduct an objective, thorough gap analysis between a candidate's resume "
        "and a target Job Description (JD). "
        "You must output ONLY a valid JSON object matching the requested schema. "
        "GROUNDING RULE: Base your analysis STRICTLY on the provided Resume and JD text. "
        "Do NOT invent or assume skills, certifications, or experience not explicitly evidenced in the resume."
    )

    user_prompt = f"""Analyze the candidate's resume against the Job Description below.

[JOB DESCRIPTION]
{jd_text}

[CANDIDATE RESUME]
{resume_text}

Provide the analysis as a JSON object with this exact structure:
{{
  "match_score": <integer between 0 and 100 representing overall alignment>,
  "summary": "<2-3 sentence executive summary of overall candidate fit, strengths, and primary gaps>",
  "matched_skills": [
    "<skill or experience explicitly evidenced in both resume and JD>"
  ],
  "missing_skills": [
    {{
      "skill": "<skill/technology/requirement required in JD but absent from resume>",
      "importance": "<high | medium | low>",
      "reason": "<clear explanation of why this skill is needed for this role>"
    }}
  ],
  "weak_areas": [
    "<skill or domain mentioned in the resume but with weak evidence, no metrics, or shallow project depth>"
  ],
  "resume_red_flags": [
    "<formatting, phrasing, lack of measurable impact/KPIs, vague bullet points, or unexplained gaps>"
  ]
}}
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_interviewer_prompt(mode: str, level: str, gaps: dict | None = None) -> str:
    """
    Constructs the system prompt for the AI interviewer, embedding mode, difficulty level,
    and priority candidate skill gaps to probe.
    """
    mode_guidance = {
        "Technical": (
            "- Focus heavily on core engineering concepts, architecture, problem-solving, debugging, "
            "tools/frameworks mentioned in the JD, and scenario-based technical design questions."
        ),
        "HR/Behavioral": (
            "- Focus strictly on STAR-style (Situation, Task, Action, Result) behavioral questions covering teamwork, "
            "conflict resolution, leadership, failure recovery, motivation, and culture fit."
        ),
        "Mixed": (
            "- Blend approximately 60% technical depth with 40% behavioral/situational questions, "
            "alternating between practical engineering challenges and interpersonal/leadership scenarios."
        ),
    }.get(mode, "- Balanced technical and behavioral interview.")

    level_guidance = {
        "Fresher": (
            "- Difficulty: Junior / Entry-Level. Probe CS fundamentals, academic/personal projects, "
            "problem breakdown, fast learning ability, and enthusiasm."
        ),
        "Mid-level": (
            "- Difficulty: Mid-Level. Probe hands-on production experience, technical trade-offs, ownership, "
            "debugging real incidents, and independent delivery."
        ),
        "Senior": (
            "- Difficulty: Senior / Lead. Probe high-level system architecture, cross-functional leadership, "
            "mentoring, trade-offs at scale, long-term technical vision, and strategic decision-making under uncertainty."
        ),
    }.get(level, "- Standard professional level.")

    gap_summary_items = []
    if gaps:
        if isinstance(gaps, dict):
            missing = gaps.get("missing_skills", [])
            for item in missing[:5]:
                if isinstance(item, dict):
                    gap_summary_items.append(f"- Missing/Target Skill: {item.get('skill')} (Importance: {item.get('importance', 'medium')}) - {item.get('reason', '')}")
                elif hasattr(item, "skill"):
                    gap_summary_items.append(f"- Missing/Target Skill: {item.skill} (Importance: {item.importance}) - {item.reason}")
            
            weak = gaps.get("weak_areas", [])
            for w in weak[:4]:
                gap_summary_items.append(f"- Weak Resume Area: {w}")

    gaps_section = ""
    if gap_summary_items:
        gaps_section = "\nTarget Skill Gaps to Probe in this candidate:\n" + "\n".join(gap_summary_items) + "\n"

    system_prompt = f"""You are a top-tier hiring manager and technical interviewer conducting a live mock interview.
Interview Mode: {mode}
Target Seniority Level: {level}

Mode Guidelines:
{mode_guidance}

Seniority Level Guidelines:
{level_guidance}
{gaps_section}
STRICT INTERVIEWER RULES:
1. Ask exactly ONE question per turn.
2. Output ONLY the question text. Do NOT add greetings, pleasantries, hints, feedback, scores, or conversational padding (e.g. NEVER say 'Great answer!', 'Thanks for sharing', or 'Question 2:').
3. Personalize your questions using specific details from the candidate's resume (companies, projects, tools, metrics).
4. Prioritize probing the identified skill gaps and weak areas across the interview questions.
5. If the candidate gives a vague, brief, or evasive answer, ask a targeted follow-up question to drill into specifics.
6. Never repeat a question or ask multi-part compound questions that overwhelm the candidate.
"""
    return system_prompt


def build_next_question_messages(
    resume_text: str,
    jd_text: str,
    gaps: dict,
    mode: str,
    level: str,
    history: list[dict],
    current_q_idx: int,
    total_questions: int,
) -> list[dict[str, str]]:
    """
    Builds the message list sent to the LLM to generate the next interview question.
    """
    system_prompt = build_interviewer_prompt(mode, level, gaps)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"""Candidate's Resume:\n{resume_text}\n\nJob Description:\n{jd_text}\n\nThis is Question {current_q_idx + 1} of {total_questions}. Ask your next question now:""",
        },
    ]

    # Replay previous interview turns
    for turn in history:
        q = turn.get("question", "")
        a = turn.get("answer", "")
        if q:
            messages.append({"role": "assistant", "content": q})
        if a:
            messages.append({"role": "user", "content": a})

    if history:
        # Prompt next question
        messages.append({
            "role": "user",
            "content": f"Generate Question {current_q_idx + 1} of {total_questions}. Output ONLY the question.",
        })

    return messages


def build_answer_scoring_prompt(
    question: str,
    answer: str,
    jd_text: str,
    mode: str,
    level: str,
) -> list[dict[str, str]]:
    """
    Constructs the prompt for strictly scoring a single candidate answer on 4 dimensions
    and producing constructive feedback in JSON.
    """
    system_prompt = (
        "You are an expert interview evaluator. "
        "Score the candidate's response strictly, objectively, and constructively. "
        "You must output ONLY a valid JSON object matching the requested schema."
    )

    user_prompt = f"""Evaluate the candidate's answer for the following interview question.

Role Context / Job Description:
{jd_text}

Interview Mode: {mode}
Target Seniority: {level}

INTERVIEW QUESTION:
"{question}"

CANDIDATE'S ANSWER:
"{answer}"

SCORING RUBRIC (Each score must be an INTEGER from 1 to 10):
- relevance (1-10): Does the answer directly address the question and connect to the job requirements?
- depth (1-10): Technical or experiential substance, specific tools, numbers, and concrete examples (penalize high-level fluff).
- structure (1-10): Organization, logical flow, problem-to-solution progression, STAR method for behavioral questions.
- clarity (1-10): Concise, articulate, confident communication without rambling or filler words.

SCORING RULES:
- Be strict and realistic: an average answer is 5-6; 9-10 is reserved for exceptional, production-grade responses with measurable metrics.
- Penalize empty, vague, or one-sentence answers harshly (1-3).
- Focus only on the content provided.

Output the evaluation in this exact JSON format:
{{
  "relevance": <int 1-10>,
  "depth": <int 1-10>,
  "structure": <int 1-10>,
  "clarity": <int 1-10>,
  "strengths": "<one concise sentence detailing what was done well>",
  "weaknesses": "<one concise sentence detailing what was missing or needs improvement>",
  "improved_answer": "<a comprehensive, high-scoring sample answer demonstrating how the candidate should have answered (using STAR where applicable)>"
}}
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_final_report_prompt(
    resume_text: str,
    jd_text: str,
    gap: dict,
    history: list[dict],
    avg_scores: dict,
) -> list[dict[str, str]]:
    """
    Constructs the prompt for generating the comprehensive final markdown coaching report.
    """
    # Format interview summary
    interview_log_parts = []
    for idx, turn in enumerate(history):
        q = turn.get("question", "")
        a = turn.get("answer", "")
        score_obj = turn.get("score")
        score_str = ""
        if score_obj:
            if hasattr(score_obj, "model_dump"):
                score_str = json.dumps(score_obj.model_dump())
            elif isinstance(score_obj, dict):
                score_str = json.dumps(score_obj)
        interview_log_parts.append(
            f"Question {idx + 1}: {q}\nCandidate Answer: {a}\nTurn Scores & Feedback: {score_str}\n"
        )
    interview_log = "\n---\n".join(interview_log_parts)

    system_prompt = (
        "You are an elite career coach, principal engineer, and talent assessor. "
        "Generate a comprehensive, encouraging yet rigorous Final Interview Assessment & Action Report in GitHub-flavored Markdown. "
        "Format headers, bullet points, and tables cleanly for readability."
    )

    user_prompt = f"""Generate the Final Interview Coaching Report based on the mock interview performance below.

[JOB DESCRIPTION]
{jd_text}

[CANDIDATE RESUME]
{resume_text}

[GAP ANALYSIS SUMMARY]
{json.dumps(gap if isinstance(gap, dict) else gap.model_dump() if hasattr(gap, "model_dump") else {}, indent=2)}

[AGGREGATE SCORES (Out of 10)]
- Overall Average: {avg_scores.get('overall', 0)} / 10
- Relevance: {avg_scores.get('relevance', 0)} / 10
- Depth: {avg_scores.get('depth', 0)} / 10
- Structure: {avg_scores.get('structure', 0)} / 10
- Clarity: {avg_scores.get('clarity', 0)} / 10

[COMPLETE INTERVIEW TRANSCRIPT & TURN-BY-TURN SCORES]
{interview_log}

REQUIREMENTS:
Write a well-structured report in Markdown containing EXACTLY these 6 sections:

# 1. Overall Verdict
- State the overall Fit Score (0 to 100) and Seniority Assessment.
- Provide a 2-3 paragraph executive summary of the candidate's interview performance, readiness for the target role, key strengths, and highest-priority areas for growth.

# 2. Skill Gaps Analysis
- Categorize and rank missing or weak skills by importance (High, Medium, Low).
- For each skill gap, explain WHY it is critical for this specific role and what real-world impact is expected.

# 3. Resume Optimization Recommendations
- Specific bullet rewrites: show before/after examples of resume bullet points to incorporate missing keywords and quantifiable metrics (STAR format, percentages, latency, scale, revenue).
- Missing critical keywords to add to the resume for ATS and recruiter screening.
- Structure and formatting improvements.

# 4. Detailed Question-by-Question Coaching
- For each question asked in the interview:
  - Summarize what the interviewer was looking for.
  - Candidate's Strengths & Weaknesses in their response.
  - The Gold-Standard Sample Answer demonstrating the ideal STAR/technical approach.

# 5. Communication & Delivery Assessment
- Analysis of candidate's clarity, conciseness, technical vocabulary, and structure.
- Actionable tips to improve confidence, avoid filler words, and present complex ideas clearly.

# 6. 2-Week Personalized Action Plan
- A structured, step-by-step roadmap (broken down into Week 1 and Week 2 or Day-by-Day) covering:
  - Topics/tools to master.
  - Hands-on micro-projects to build proof-of-work.
  - Mock interview practice drills.
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
