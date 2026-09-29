# ◈ AI Resume Analyzer

**Understand your fit. See the gaps. Build a stronger application.**

A modular Python + Streamlit application that compares a PDF/DOCX resume with a job description using SenseNova. It displays a transparent match score, matching and missing skills, ATS keywords, evidence, text-quality checks and job-specific recommendations.

> AI understands the documents. Python calculates the score. This is an advisory estimate, not an employer ATS score or a hiring prediction.

## Project structure

```text
ai_resume_analyzer/
├── app.py                  # Streamlit UI, configuration, session state
├── analyzer.py             # Typed schemas, SenseNova adapter, comparison/scoring
├── utils.py                # Extraction, normalization and input validation
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .streamlit/config.toml
└── tests/test_analyzer.py   # Offline regression and integration tests
```

There are exactly three application Python files. Utilities have no UI/network dependencies. The analyzer knows nothing about Streamlit; its scoring functions are pure Python. A small `JsonClient` protocol decouples analysis from HTTP, enabling offline tests or another provider adapter. Pydantic schemas define the boundary between AI and Python.

## Setup and run

Use Python 3.10 or newer (3.11 recommended).

```bash
git clone https://github.com/sabirprogrammer/ai_resume_analyzer.git
cd ai_resume_analyzer
python -m venv .venv
```

Activate on **Windows PowerShell**:

```powershell
.venv\Scripts\Activate.ps1
```

Or on **Windows Command Prompt**:

```bat
.venv\Scripts\activate.bat
```

Or on **macOS/Linux**:

```bash
source .venv/bin/activate
```

Install and start:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Configure your key in `.streamlit/secrets.toml` using the secrets example below. Open `http://localhost:8501`, upload a resume, paste a detailed job description, enable the data-sharing checkbox and click **Analyze my resume**. Visitors are never asked for an API key.

Alternatively, copy `.env.example` to `.env` and fill in your key before starting. Never commit `.env` or real credentials. Credentials and model settings are read only from server configuration. Streamlit secrets take precedence over environment variables.

## SenseNova configuration

Obtain a key from [SenseNova Console](https://platform.sensenova.ai/console/keys). Check that your account has access to the model. This app uses the same international SenseNova endpoint as the working Study Pack project:

- Endpoint: `https://token.sensenova.ai/v1/chat/completions`
- Authentication: bearer API key
- Default model: `sensenova-6.8-flash-lite` (preview; configurable through SENSENOVA_MODEL in server secrets)
- Non-streaming response: `choices[0].message.content`

This adapter targets the international `.ai` token endpoint. Keys from `.ai` and `.cn` platforms should not be assumed interchangeable. A valid key and available model are required for real analysis. Provider availability, quotas and costs depend on your account.

The app requests JSON through schema instructions and validates it with Pydantic; it does not assume the endpoint supports a provider-enforced `response_format`. Malformed JSON gets one regeneration attempt. Ungrounded evidence is rejected. HTTP 429/5xx receive bounded retries; authentication and configuration errors are displayed without exposing provider response bodies or secrets. Reasoning fields are ignored.

## Workflow

1. Python validates file size/type and extracts text locally.
2. SenseNova extracts resume skills, required/preferred job skills, keywords and experience/education evidence in one structured response.
3. Python validates verbatim source quotes, removes duplicates, normalizes aliases and compares skills.
4. Python calculates the weighted score and final match label.
5. SenseNova explains the fixed comparison and suggests truthful improvements.
6. Streamlit displays results, evidence and a downloadable JSON report.

## Scoring method

| Category | Base weight | Rule |
|---|---:|---|
| Skills | 35% | Matched required skills / all required skills |
| Keywords | 25% | Literal job keyword phrases found / extracted keywords |
| Experience | 20% | Average requirement status: met 1, partial 0.5, not evidenced 0 |
| Education | 10% | Same status rubric as experience |
| Text quality | 10% | Five equally weighted checks: email, skills, experience/projects, education, possible quantified outcome |

If no required skills are specified, preferred skills supply the skills category. Otherwise preferred skills are informational. Unspecified categories are **not applicable**, and active weights are normalized to 100. No division by zero or free points for absent job requirements. The displayed total is rounded once; displayed component points can differ by 0.01 due to rounding.

Labels: **Strong** ≥85, **Good** ≥70, **Moderate** ≥50, **Low** <50.

The same validated extraction always gives the same score. AI extraction and experience/education judgments may vary. Skills use case-insensitive matching and a small explicit alias map; keywords use literal phrase boundaries, so `Java` does not match `JavaScript`. Keywords and skills intentionally overlap under the requested rubric. Missing means **not evidenced**, not necessarily absent ability. Text quality heuristics are English-oriented and do not inspect visual formatting.

## Deploy to Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect GitHub.
2. Create an app for `sabirprogrammer/ai_resume_analyzer`, branch `main`, entry file `app.py`.
3. In app secrets, add:

```toml
SENSENOVA_API_KEY = "your_real_key"
SENSENOVA_MODEL = "sensenova-6.8-flash-lite"
```

4. Save secrets and deploy. The app reads the key automatically. There are no API key or model fields in the interface. If the key is missing, analysis shows a configuration message for the app owner.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

Tests use mocked AI/HTTP responses, in-memory PDF/DOCX files, pure scoring tests and Streamlit's app harness. They do not use a live API key or incur charges. Run a real analysis with your own key to verify your account/model access.

## Privacy and limitations

- Upload limit: 5 MB; PDF limit: 20 pages; resume text: 30,000 characters; job text: 20,000 characters.
- Files are processed in memory, not persisted by the app. Results stay in the browser session's server-side state; no global resume cache is used.
- On consent, resume text and job text are sent to SenseNova for both extraction and recommendations. SenseNova's data policies apply. Remove unnecessary personal details before submitting.
- Scanned/image-only PDF pages, protected PDFs, corrupted files and insufficient text receive clear errors. No OCR. DOCX text boxes and deeply nested tables are not guaranteed to extract; review the extracted text.
- Quotes are validated for presence. This does not prove a claim is true or that the AI interpreted it correctly. Review requirement statuses and recommendations.
- No guaranteed ATS compatibility, candidate ranking, background checks or automated hiring decisions.
- If recommendation generation fails after successful comparison, the score and evidence remain available.
