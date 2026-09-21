"""Unit and integration tests for AI Interview Coach components."""

import sys
import os
import io
import unittest
import pandas as pd
from pypdf import PdfWriter

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    MODES,
    DIFFICULTY_LEVELS,
    DEFAULT_QUESTIONS,
    MIN_QUESTIONS,
    MAX_QUESTIONS,
    validate_config,
)
from schemas import GapAnalysisResult, MissingSkillItem, AnswerScore
from utils import (
    extract_text_from_pdf,
    truncate_text,
    sanitize_text_for_pdf,
    compute_aggregate_scores,
)
from charts import make_radar_chart
from exporter import build_markdown, build_pdf
from prompts import (
    build_gap_analysis_prompt,
    build_interviewer_prompt,
    build_next_question_messages,
    build_answer_scoring_prompt,
    build_final_report_prompt,
)


class TestConfigAndSchemas(unittest.TestCase):
    def test_config_constants(self):
        self.assertIn("Technical", MODES)
        self.assertIn("HR/Behavioral", MODES)
        self.assertIn("Mixed", MODES)
        self.assertIn("Senior", DIFFICULTY_LEVELS)
        self.assertEqual(MIN_QUESTIONS, 3)
        self.assertEqual(MAX_QUESTIONS, 15)
        self.assertEqual(DEFAULT_QUESTIONS, 5)

    def test_schema_gap_analysis_valid(self):
        data = {
            "match_score": 85,
            "summary": "Strong candidate with solid cloud and backend background.",
            "matched_skills": ["Python", "FastAPI", "Azure"],
            "missing_skills": [
                {"skill": "Kubernetes", "importance": "high", "reason": "Microservices deployment"},
                {"skill": "Terraform", "importance": "medium", "reason": "IaC provisioning"}
            ],
            "weak_areas": ["Docker container optimization metrics"],
            "resume_red_flags": ["No quantifiable metrics in latest role"]
        }
        res = GapAnalysisResult.model_validate(data)
        self.assertEqual(res.match_score, 85)
        self.assertEqual(len(res.missing_skills), 2)
        self.assertEqual(res.missing_skills[0].importance, "high")

    def test_schema_answer_score(self):
        data = {
            "relevance": 8,
            "depth": 7,
            "structure": 9,
            "clarity": 8,
            "strengths": "Clear explanation of distributed cache invalidation.",
            "weaknesses": "Could provide specific latency improvement metrics.",
            "improved_answer": "In my previous role at X, I reduced latency by 40% using Redis..."
        }
        score = AnswerScore.model_validate(data)
        self.assertEqual(score.relevance, 8)
        self.assertEqual(score.average, 8.0)


class TestUtils(unittest.TestCase):
    def test_text_truncation(self):
        long_str = "A" * 15000
        truncated, was_trunc = truncate_text(long_str, limit=1000)
        self.assertTrue(was_trunc)
        self.assertTrue(len(truncated) < 1100)

        short_str = "Short text"
        clean, was_trunc = truncate_text(short_str, limit=1000)
        self.assertFalse(was_trunc)
        self.assertEqual(clean, "Short text")

    def test_sanitize_text_for_pdf(self):
        raw = "Smart quotes “hello” and ‘world’ — em-dash and • bullet"
        clean = sanitize_text_for_pdf(raw)
        self.assertNotIn("“", clean)
        self.assertNotIn("”", clean)
        self.assertNotIn("—", clean)

    def test_compute_aggregate_scores(self):
        history = [
            {
                "question": "Q1",
                "answer": "A1",
                "score": AnswerScore(
                    relevance=8, depth=6, structure=8, clarity=10,
                    strengths="Good", weaknesses="None", improved_answer="Better"
                ),
            },
            {
                "question": "Q2",
                "answer": "A2",
                "score": {
                    "relevance": 6, "depth": 8, "structure": 8, "clarity": 6,
                    "strengths": "Good", "weaknesses": "None", "improved_answer": "Better"
                },
            },
        ]
        avg = compute_aggregate_scores(history)
        self.assertEqual(avg["relevance"], 7.0)
        self.assertEqual(avg["depth"], 7.0)
        self.assertEqual(avg["structure"], 8.0)
        self.assertEqual(avg["clarity"], 8.0)
        self.assertEqual(avg["overall"], 7.5)

    def test_pdf_extraction(self):
        # Create a mock PDF in-memory using pypdf.PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        pdf_buf = io.BytesIO()
        writer.write(pdf_buf)
        pdf_buf.seek(0)

        text, warn = extract_text_from_pdf(pdf_buf)
        self.assertIsNotNone(warn)  # Blank page should trigger short length warning


class TestChartsAndExporters(unittest.TestCase):
    def test_make_radar_chart(self):
        avg_scores = {"relevance": 8.5, "depth": 7.0, "structure": 9.0, "clarity": 8.0}
        png_bytes = make_radar_chart(avg_scores)
        self.assertIsInstance(png_bytes, bytes)
        self.assertTrue(len(png_bytes) > 500)
        # PNG signature check: \x89PNG\r\n\x1a\n
        self.assertTrue(png_bytes.startswith(b"\x89PNG"))

    def test_markdown_and_pdf_export(self):
        score_df = pd.DataFrame([
            {"#": 1, "Question": "Explain CAP Theorem", "Relevance": 9, "Depth": 8, "Structure": 8, "Clarity": 9, "Avg": 8.5},
            {"#": 2, "Question": "Describe a conflict", "Relevance": 8, "Depth": 7, "Structure": 9, "Clarity": 8, "Avg": 8.0},
        ])
        avg_scores = {"relevance": 8.5, "depth": 7.5, "structure": 8.5, "clarity": 8.5, "overall": 8.25}
        radar_bytes = make_radar_chart(avg_scores)
        meta = {"mode": "Mixed", "level": "Senior", "n_questions": 2}
        report_md = "# Overall Verdict\nCandidate performed very well.\n\n## Skill Gaps\n- Kubernetes: Needed for container orchestration."

        # Markdown check
        md_res = build_markdown(report_md, score_df, {}, avg_scores, meta)
        self.assertIn("# AI Interview Coach - Final Assessment Report", md_res)
        self.assertIn("Explain CAP Theorem", md_res)

        # PDF check
        pdf_bytes = build_pdf(report_md, radar_bytes, score_df, {}, avg_scores, meta)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


class TestPrompts(unittest.TestCase):
    def test_build_gap_analysis_prompt(self):
        messages = build_gap_analysis_prompt("Resume text here", "JD text here")
        self.assertEqual(len(messages), 2)
        self.assertIn("JSON", messages[0]["content"])
        self.assertIn("Resume text here", messages[1]["content"])

    def test_build_interviewer_prompt(self):
        gaps = {
            "missing_skills": [{"skill": "Docker", "importance": "high", "reason": "Containerization"}],
            "weak_areas": ["Kubernetes scaling"]
        }
        prompt = build_interviewer_prompt("Technical", "Senior", gaps)
        self.assertIn("Technical", prompt)
        self.assertIn("Senior", prompt)
        self.assertIn("Docker", prompt)
        self.assertIn("ONE question per turn", prompt)


if __name__ == "__main__":
    unittest.main()
