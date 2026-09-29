<div align="center">

# ◈ AI Resume Analyzer

### Your experience. Your next opportunity.

Compare your resume with a job description, understand your strengths, and discover what to improve before you apply.

[![Open Live App](https://img.shields.io/badge/OPEN_LIVE_APP-7452D6?style=for-the-badge&logo=streamlit&logoColor=white)](https://airesumeanalyzer-ft.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](#quick-start)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](#the-experience)
[![SenseNova](https://img.shields.io/badge/AI-SenseNova-9270D5?style=for-the-badge)](#sensenova-configuration)

**[Try the app](https://airesumeanalyzer-ft.streamlit.app/)** · **[Quick start](#quick-start)** · **[Scoring](#how-the-score-works)** · **[Architecture](#project-architecture)**

</div>

---

## A clearer picture before you apply

A resume can contain relevant experience without clearly showing how it fits a specific role. AI Resume Analyzer helps you see that gap. Upload a PDF or DOCX, paste the target job description, and receive an evidence-based comparison with practical recommendations.

**AI interprets the documents. Python calculates the score.** Every report includes supporting quotes and a visible score breakdown so you can review the reasoning behind the result.

> The match score is an advisory estimate, not an employer’s ATS score or a prediction of hiring success.

## Try it live

### [Launch AI Resume Analyzer →](https://airesumeanalyzer-ft.streamlit.app/)

1. **Upload your resume** in PDF or DOCX format.
2. **Paste the job description**, including skills, responsibilities and qualifications.
3. **Agree to send the extracted text to SenseNova**, then select **Analyze my resume**.
4. **Explore your report** and download the full analysis as JSON.

Visitors do not need to enter an API key. Credentials are configured by the app owner through Streamlit Secrets.

## What you get

| Feature | What it helps you understand |
|---|---|
| **Overall match score** | How the evidence in your resume aligns with the target role |
| **Required and preferred skills** | Which skills match and which are not evidenced |
| **ATS keyword insights** | Important job phrases found or missing in your resume |
| **Experience and education review** | How your background compares with explicit requirements |
| **Resume quality checks** | Whether key sections and possible quantified outcomes are present |
| **Personalized action plan** | Job-specific improvements that avoid inventing experience |
| **Evidence explorer** | Resume and job-description quotes behind the comparison |
| **Downloadable report** | A structured JSON copy of the results |

## The experience

A purple and lavender workspace keeps the application easy to scan:

- Separate resume and job-description cards with input progress indicators.
- Circular match score, summary cards and visual category bars.
- Dedicated tabs for skills, keywords, recommendations and source evidence.
- Responsive styling for smaller screens.
- Clear validation messages for unreadable files, missing inputs and API failures.

## How it works

| Stage | Responsibility | Output |
|---|---|---|
| **1. Read** | Python extracts and validates document text | Clean resume and job text |
| **2. Understand** | SenseNova identifies skills, requirements and supporting quotes | Schema-validated JSON |
| **3. Compare** | Python verifies quote presence, normalizes aliases and compares skills | Matches, gaps and keyword coverage |
| **4. Score** | Python applies the weighted rubric | Category scores and final label |
| **5. Explain** | SenseNova generates recommendations from the comparison | Strengths, problems and next steps |
| **6. Present** | Streamlit renders the report | Interactive results and JSON download |

## How the score works

| Category | Base weight | Calculation |
|---|---:|---|
| Required skills | **35%** | Matched required skills ÷ required skills |
| Job keywords | **25%** | Literal keyword phrases found ÷ extracted keywords |
| Experience | **20%** | Average requirement status: met = 1, partial = 0.5, not evidenced = 0 |
| Education | **10%** | Same status rubric as experience |
| Text quality | **10%** | Five equally weighted text checks |

The five quality checks look for a contact email, skills section, experience/projects section, education section and a possible quantified outcome.

| Score | Assessment |
|---|---|
| 85–100 | **Strong Match** |
| 70–<85 | **Good Match** |
| 50–<70 | **Moderate Match** |
| Below 50 | **Low Match** |

**Scoring details:**

- If no required skills are listed, preferred skills supply the skills category. Otherwise they are informational.
- Unspecified categories are marked **not applicable** and remaining weights are normalized to 100.
- Skills are matched case-insensitively with a small explicit alias map. Keywords use literal phrase boundaries, so `Java` does not match `JavaScript`.
- The same validated extraction produces the same score. AI extraction and requirement judgments can vary between runs.
- “Missing” means **not evidenced in this resume**, not proof that a person lacks the ability.
- Skills and keywords intentionally overlap in this rubric. Displayed component points may differ from the total by 0.01 due to rounding.

## Tech stack

| Technology | Purpose |
|---|---|
| Python | Validation, orchestration and deterministic scoring |
| Streamlit | Upload flow, session state and results dashboard |
| SenseNova API | Document interpretation and recommendations |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX paragraph, table, header and footer extraction |
| Pydantic | Typed schemas and structured JSON validation |
| Requests | HTTP API integration |
| python-dotenv | Optional local environment configuration |
| pytest | Offline regression and integration tests |

## Project architecture

```text
ai_resume_analyzer/
├── app.py                  # Streamlit interface and session orchestration
├── analyzer.py             # AI adapter, schemas, comparison and scoring
├── utils.py                # File extraction and input normalization
├── requirements.txt        # Runtime dependencies
├── .env.example            # Optional local configuration template
├── .gitignore              # Excludes credentials and generated files
├── .streamlit/
│   └── config.toml          # Theme and upload settings
├── tests/
│   └── test_analyzer.py     # Offline tests
└── README.md
```

Only **three application Python files** are needed. Utilities have no UI or network dependencies. The analyzer does not import Streamlit, and scoring functions remain independent of API calls. A small `JsonClient` protocol lets tests supply mock responses without changing the analysis workflow.

This keeps responsibilities focused, related logic together, and dependencies loose.

## Quick start

Use **Python 3.10+**; Python 3.11 is recommended.

### 1. Clone and create an environment

```bash
git clone https://github.com/sabirprogrammer/ai_resume_analyzer.git
cd ai_resume_analyzer
python -m venv .venv
```

Activate it using the command for your terminal:

| Terminal | Command |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure your key

Create `.streamlit/secrets.toml`:

```toml
SENSENOVA_API_KEY = "your_sensenova_api_key"
SENSENOVA_MODEL = "sensenova-6.8-flash-lite"
```

Alternatively, copy `.env.example` to `.env` and fill in the values. Streamlit Secrets take precedence over environment variables. **Never commit real credentials.** Both local secret files are excluded by `.gitignore`.

### 4. Run

```bash
python -m streamlit run app.py
```

Open **[localhost:8501](http://localhost:8501)** in your browser.

## SenseNova configuration

Create your key in the **[SenseNova international console](https://platform.sensenova.ai/console/keys)**.

| Setting | Value |
|---|---|
| API endpoint | `https://token.sensenova.ai/v1/chat/completions` |
| Authentication | Bearer API key |
| Default model | `sensenova-6.8-flash-lite` |
| Model override | `SENSENOVA_MODEL` in server secrets |

The app targets the **`.ai` endpoint**. Do not assume `.ai` and `.cn` credentials are interchangeable. Model access, availability, quotas and costs depend on your provider account.

JSON is requested through schema instructions and validated with Pydantic. The app does not assume provider-enforced `response_format` support. Invalid JSON receives one regeneration attempt, ungrounded evidence is rejected, and HTTP 429/5xx errors receive bounded retries. Provider response bodies and API keys are not displayed in error messages.

## Deploy your own copy

The deployed app is available at **[airesumeanalyzer-ft.streamlit.app](https://airesumeanalyzer-ft.streamlit.app/)**.

To host another instance on [Streamlit Community Cloud](https://share.streamlit.io/):

1. Connect your GitHub account and select this repository or your fork.
2. Use branch **`main`** and entry file **`app.py`**.
3. Add `SENSENOVA_API_KEY` and `SENSENOVA_MODEL` to app secrets using the TOML example above.
4. Save and deploy.

API configuration remains server-side. Visitors see the resume workflow without credential fields.

## Testing

```bash
python -m pip install pytest
python -m pytest -q
```

The test suite covers scoring, absent-category handling, phrase boundaries, unsupported evidence, duplicate skills, PDF/DOCX extraction, invalid uploads, JSON regeneration, authentication errors, rate-limit retries, truncated responses, recommendation fallback and Streamlit rendering.

Tests use mocked AI/HTTP responses and in-memory files. They do not incur API charges or verify live account access.

## Troubleshooting

| Problem | What to check |
|---|---|
| API key rejected / HTTP 401 | Use an active key from `platform.sensenova.ai` and check the secret name |
| Model not found / HTTP 404 | Set `SENSENOVA_MODEL` to an identifier available to your account |
| Rate limit / HTTP 429 | Wait and retry; check your provider quota |
| Little or no readable text | Upload a text-based PDF or DOCX; scanned pages need OCR first |
| Invalid structured data or unsupported evidence | Retry the analysis and review the extracted document text |
| Recommendations unavailable | The completed score and evidence remain available |

## Privacy and practical limits

- **Files:** PDF/DOCX up to 5 MB; PDFs up to 20 pages.
- **Text:** Resume up to 30,000 characters; job description up to 20,000 characters. Each needs at least 100 characters and 20 words.
- **Processing:** Files are processed in memory. The app does not persist resumes to disk or a database and does not use a global resume cache. Results remain in server-side session state.
- **AI requests:** With consent, extracted resume and job text are sent to SenseNova. Its data policies apply.
- **Extraction:** No OCR. Password-protected PDFs are rejected. DOCX text boxes and deeply nested tables may not extract completely.
- **Interpretation:** Quote checks verify text presence, not factual truth or perfect AI interpretation. Review the evidence and recommendations.
- **ATS limits:** Text checks are English-oriented and do not verify document layout, actual employer ATS parsing or hiring outcomes.

---

<div align="center">

**Built by [Sanaullah Sabir](https://github.com/sabirprogrammer)**

A practical project combining document processing, structured AI output and transparent Python scoring.

**[Open the live app →](https://airesumeanalyzer-ft.streamlit.app/)**

</div>
