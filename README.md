# 🎯 AI Interview Coach

An intelligent, interactive mock interview and coaching application built with **Streamlit** and powered by **Azure AI Foundry** (`gpt-4o` / `gpt-4.1`).

AI Interview Coach automates end-to-end interview preparation: analyzing resume-to-JD alignment, identifying critical skill gaps, conducting dynamic text-only mock interviews that adapt to the candidate's weaknesses, silently scoring answers across 4 rubric dimensions, and generating exportable coaching reports with radar charts, score tables, bullet rewrites, and a personalized 2-week action plan.

---

## 🌟 Key Features

1. **Pre-Interview Gap Analysis (Stage 1 & 2)**
   - Extract candidate profile directly from PDF resumes using `pypdf`.
   - Calculate role match score (0–100) and identify matched vs. missing skills categorized by importance (High, Medium, Low).
   - Flag weak resume areas (lack of metrics, shallow project evidence) and formatting red flags.

2. **Adaptive Mock Interview (Stage 3)**
   - Configurable **Modes**: `Technical`, `HR/Behavioral`, and `Mixed` (60% Tech / 40% Behavioral).
   - Configurable **Seniority**: `Fresher`, `Mid-level`, and `Senior`.
   - Dynamic prompt injection: The AI interviewer probes identified skill gaps and asks follow-ups to vague responses.
   - Text-only input interface using `st.chat_input` (strict single-question turn loop).

3. **Silent 4-Dimension Rubric Scoring**
   - Each answer is scored silently on a 1–10 scale:
     - **Relevance**: Direct alignment with the question and target JD.
     - **Depth**: Concrete technical substance, architectural trade-offs, and metrics.
     - **Structure**: Logical progression and STAR method adherence.
     - **Clarity**: Articulate, concise, and professional communication.
   - Generates strengths, weaknesses, and a gold-standard sample answer for every turn.

4. **Comprehensive Final Report & Visualization (Stage 4)**
   - **Performance Radar Chart**: High-resolution 4-axis polar plot rendered with `matplotlib`.
   - **Score Breakdown Table**: Pandas dataframe showing turn-by-turn dimension scores.
   - **Executive Coaching Report**: Overall verdict, ranked skill gaps, ATS resume bullet rewrites, and a structured 2-Week Action Plan.

5. **Multi-Format Export**
   - 📥 **Markdown (`.md`)**: Full report with markdown tables and timestamps.
   - 📄 **PDF (`.pdf`)**: Multi-page report built with `fpdf2`, embedding metadata badges, score table, and the radar chart image.

---

## 🏗️ Architecture & Data Flow

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT UI (app.py)                         │
│                                                                         │
│   [ Setup Screen ] ──► [ Gap Analysis ] ──► [ Interview ] ──► [ Report ]│
│    (PDF Upload / JD)    (Match Score / Gaps) (st.chat_input)   (Radar/PDF)│
└────────────┬──────────────────┬───────────────────┬─────────────────┬───┘
             │                  │                   │                 │
             ▼                  ▼                   ▼                 ▼
   ┌──────────────────┐ ┌───────────────┐  ┌────────────────┐ ┌───────────────┐
   │     utils.py     │ │  prompts.py   │  │  analysis.py   │ │  exporter.py  │
   │ (PDF Extraction) │ │ (Interviewer /│  │(analyze_gap,   │ │ (Markdown &   │
   │ (Sanitization)   │ │  Scoring /    │  │ score_answer,  │ │  fpdf2 PDF)   │
   │                  │ │  Report Prompts│ │ next_question) │ │   charts.py   │
   └──────────────────┘ └───────┬───────┘  └───────┬────────┘ └───────────────┘
                                │                  │
                                └─────────┬────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │       llm.py        │
                               │(chat, json_chat +   │
                               │ Pydantic Validation)│
                               └──────────┬──────────┘
                                          │
                                          ▼
                       ┌─────────────────────────────────────┐
                       │          Azure AI Foundry           │
                       │    (Azure OpenAI gpt-4o Service)    │
                       └─────────────────────────────────────┘
```

---

## 📂 Project Structure

```
azure_project/
├── app.py                 # Streamlit UI + Stage routing (setup -> analysis -> interview -> report)
├── config.py              # Environment variables, app constants, configuration validator
├── llm.py                 # Azure OpenAI client wrappers (chat, json_chat with Pydantic validation)
├── prompts.py             # Prompt builders for gap analysis, interviewer, scoring, and reports
├── schemas.py             # Pydantic schemas (GapAnalysisResult, AnswerScore, MissingSkillItem)
├── analysis.py            # Core orchestration (analyze_gap, score_answer, generate_report, get_next_question)
├── charts.py              # Matplotlib radar chart generator (returns PNG bytes)
├── exporter.py            # Multi-format report builder (Markdown & fpdf2 PDF with chart embed)
├── utils.py               # PDF text extraction, text truncation, score calculations, sanitization
├── samples.py             # Sample resume and JD profile for quick testing
├── tests/
│   └── test_coach.py      # Automated unit & integration tests
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore file (excludes .env, venv, cache)
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- An active **Azure AI Foundry** or **Azure OpenAI** deployment with `gpt-4o` or `gpt-4.1`.

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd azure_project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and provide your Azure OpenAI credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-10-21
```

### 4. Running the Application

Launch the Streamlit app:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python tests/test_coach.py
```
Or with `pytest`:
```bash
pytest tests/
```

---

## 📸 App Walkthrough & Stages

1. **Setup Screen**:
   - Upload your resume PDF and paste the target Job Description.
   - Choose your interview mode (`Technical`, `HR/Behavioral`, `Mixed`), target seniority (`Fresher`, `Mid-level`, `Senior`), and number of questions (3–15).
   - *(Optional)* Click **"Load Sample Profile & JD"** for instant 1-click evaluation.

2. **Gap Analysis**:
   - Review your **Match Score** (0–100) and executive summary.
   - Inspect matched skills, high/medium/low priority missing skills, weak areas, and resume red flags.

3. **Live Mock Interview**:
   - Answer each personalized question directly in the text input (`st.chat_input`).
   - The AI probes your skill gaps, asks contextual follow-ups, and secretly grades each answer.

4. **Final Coaching Report**:
   - View your **Performance Radar Chart** and **Score Table**.
   - Review question-by-question strengths and gold-standard sample answers.
   - Read the 2-week personalized action plan and download the full report in **Markdown (.md)** or **PDF (.pdf)** format.

---

## 🛡️ Responsible AI & Privacy Statement

- **Coaching Purpose Only**: AI Interview Coach is designed strictly as a self-study and coaching tool to help candidates prepare for interviews. It is **not** an automated hiring tool and should not be used to make employment decisions.
- **In-Session Ephemeral Data**: Candidate resumes, job descriptions, and interview transcripts are processed entirely in memory (`st.session_state`) during the user's active session. No candidate data is permanently stored or persisted to disk.

---

## 🎥 Demo Video

> *Link to demo video / walkthrough recording: [Demo Video URL]*
