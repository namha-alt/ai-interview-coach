"""Analysis, interview question generation, answer scoring, and report orchestration."""

import logging
from schemas import GapAnalysisResult, AnswerScore
from prompts import (
    build_gap_analysis_prompt,
    build_next_question_messages,
    build_answer_scoring_prompt,
    build_final_report_prompt,
)
from llm import chat, json_chat

logger = logging.getLogger(__name__)


def analyze_gap(resume_text: str, jd_text: str) -> GapAnalysisResult:
    """
    Performs gap analysis between resume and job description.
    Returns structured GapAnalysisResult.
    """
    messages = build_gap_analysis_prompt(resume_text, jd_text)
    result = json_chat(messages, schema_model=GapAnalysisResult, temperature=0.2)
    return result


def get_next_question(
    resume_text: str,
    jd_text: str,
    gaps: dict | GapAnalysisResult,
    mode: str,
    level: str,
    history: list[dict],
    current_q_idx: int,
    total_questions: int,
) -> str:
    """
    Generates the next personalized interview question.
    """
    gaps_dict = gaps.model_dump() if hasattr(gaps, "model_dump") else gaps
    messages = build_next_question_messages(
        resume_text=resume_text,
        jd_text=jd_text,
        gaps=gaps_dict,
        mode=mode,
        level=level,
        history=history,
        current_q_idx=current_q_idx,
        total_questions=total_questions,
    )
    raw_question = chat(messages, temperature=0.6)
    
    # Strip any accidental formatting or numbering prefixes (e.g. "Question 1: ...")
    clean_question = raw_question.strip()
    if clean_question.startswith('"') and clean_question.endswith('"'):
        clean_question = clean_question[1:-1].strip()
    return clean_question


def score_answer(
    question: str,
    answer: str,
    jd_text: str,
    mode: str,
    level: str,
) -> AnswerScore:
    """
    Scores a single candidate answer against rubric dimensions (1-10) with critique.
    """
    messages = build_answer_scoring_prompt(
        question=question,
        answer=answer,
        jd_text=jd_text,
        mode=mode,
        level=level,
    )
    score_result = json_chat(messages, schema_model=AnswerScore, temperature=0.1)
    return score_result


def generate_report(
    resume_text: str,
    jd_text: str,
    gap: dict | GapAnalysisResult,
    history: list[dict],
    avg_scores: dict[str, float],
) -> str:
    """
    Generates the comprehensive final markdown report summarizing candidate performance,
    skill gaps, resume rewrites, answer evaluations, and a 2-week action plan.
    """
    gap_dict = gap.model_dump() if hasattr(gap, "model_dump") else gap
    messages = build_final_report_prompt(
        resume_text=resume_text,
        jd_text=jd_text,
        gap=gap_dict,
        history=history,
        avg_scores=avg_scores,
    )
    report_markdown = chat(messages, temperature=0.5)
    return report_markdown
