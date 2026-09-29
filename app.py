"""Streamlit presentation and session orchestration only."""
import hashlib
import json
import os
from html import escape

import streamlit as st
from dotenv import load_dotenv

from analyzer import AnalysisError, DEFAULT_MODEL, SenseNovaClient, analyze_resume
from utils import InputError, MAX_JOB_CHARS, extract_resume_text, validate_inputs

load_dotenv()
st.set_page_config(page_title='AI Resume Analyzer', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background: #f5f7fb;}
.block-container {max-width: 1180px; padding-top: 2.5rem;}
h1,h2,h3 {letter-spacing:-.035em; color:#17243d;}
.hero {background:linear-gradient(115deg,#111f3a,#254d67); padding:38px 40px;
 border-radius:22px;color:white;margin-bottom:24px;}
.hero h1 {color:white;font-size:2.65rem;margin:10px 0;}
.hero p {color:#cedde9;max-width:680px;font-size:1.05rem;}
.eyebrow {font-size:.75rem;letter-spacing:.18em;color:#75e1c3;font-weight:700;}
.chip {display:inline-block;background:#e7f5ef;color:#146344;border:1px solid #c3e5d5;
 border-radius:8px;padding:6px 11px;margin:4px;font-size:.88rem;}
.chip.gap {background:#fff2e6;color:#8d4817;border-color:#f1d5ba;}
[data-testid="stMetric"] {background:white;border:1px solid #e2e7ef;border-radius:15px;padding:18px;}
[data-testid="stSidebar"] {background:#fff;}
.stButton > button[kind="primary"] {background:#146e61;border:0;border-radius:10px;}
</style>''', unsafe_allow_html=True)


def setting(name, default=''):
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return os.getenv(name, default)


def chips(items, gap=False):
    if not items:
        st.caption('None identified.')
    else:
        st.markdown(''.join(f'<span class="chip {"gap" if gap else ""}">{escape(x)}</span>' for x in items), unsafe_allow_html=True)


def bullets(items):
    for item in items:
        st.write('• ' + item)
    if not items:
        st.caption('No items reported.')


server_key = setting('SENSENOVA_API_KEY')
model = setting('SENSENOVA_MODEL', DEFAULT_MODEL)

with st.sidebar:
    st.markdown('### ◈ Resume Analyzer')
    st.caption('YOUR NEXT ROLE, WITH CLARITY')
    st.divider()
    st.markdown('**How it works**')
    st.write('1. Upload your resume\n2. Paste the target job\n3. Review your match and next steps')
    st.caption('PDF / DOCX • Up to 5 MB • Text-based resumes')
    st.info('The score is a transparent estimate, not an employer ATS score or hiring prediction.')

st.markdown('''<div class="hero"><div class="eyebrow">RESUME INTELLIGENCE / POWERED BY SENSENOVA</div>
<h1>Turn your resume into<br>a stronger application.</h1>
<p>See where you match, find the gaps, and get practical guidance for the role you want.</p></div>''', unsafe_allow_html=True)
left, right = st.columns([1, 1.35], gap='large')
with left:
    st.subheader('01  Your resume')
    upload = st.file_uploader('Upload PDF or DOCX', type=['pdf', 'docx'])
    st.caption('Export scanned resumes as readable text before uploading.')
with right:
    st.subheader('02  Target role')
    job = st.text_area('Paste the complete job description', height=190, max_chars=MAX_JOB_CHARS,
                       placeholder='Include responsibilities, required skills, experience and qualifications...')
consent = st.checkbox('I agree to send the extracted resume text and job description to SenseNova for analysis.')
st.caption('Files are processed in memory. This app does not save resumes to disk or a database. SenseNova processes submitted text under its own policies.')

file_data = upload.getvalue() if upload else b''
fingerprint = hashlib.sha256(file_data + job.encode() + model.encode()).hexdigest()
if st.session_state.get('fingerprint') != fingerprint:
    st.session_state.pop('result', None)
    st.session_state.pop('resume_text', None)

if st.button('Analyze my resume  →', type='primary', use_container_width=True):
    st.session_state.pop('result', None)
    try:
        if not upload:
            raise InputError('Upload your resume first.')
        if not consent:
            raise InputError('Please agree to send the text to SenseNova before continuing.')
        resume = extract_resume_text(file_data, upload.name)
        resume, cleaned_job = validate_inputs(resume, job)
        client = SenseNovaClient(server_key, model)
        with st.spinner('Reading evidence, comparing requirements and preparing recommendations...'):
            result = analyze_resume(client, resume, cleaned_job)
        st.session_state.update(result=result, fingerprint=fingerprint, resume_text=resume)
    except (InputError, AnalysisError) as exc:
        st.error(str(exc))

result = st.session_state.get('result')
if result:
    st.divider()
    st.subheader('Your application snapshot')
    a, b, c, d = st.columns(4)
    a.metric('Overall match', f"{result['match_score']:g}%")
    b.metric('Assessment', result['final_result'])
    c.metric('Required skills matched', str(len(result['matching_skills'])))
    d.metric('Keywords found', str(len(result['ats_keywords_found'])))
    st.progress(result['match_score'] / 100)
    st.caption('Scores reflect evidence in this resume. Missing evidence does not prove a lack of ability. AI extraction can vary between runs.')
    if result['advice_warning']:
        st.warning(result['advice_warning'])
    skills, keywords, advice, evidence = st.tabs(['Skills & score', 'ATS keywords', 'Action plan', 'Evidence & method'])
    with skills:
        x, y = st.columns(2)
        with x:
            st.markdown('#### Matching required skills')
            chips(result['matching_skills'])
            st.markdown('#### Preferred skills matched')
            chips(result['preferred_skills_matched'])
        with y:
            st.markdown('#### Required skills not evidenced')
            chips(result['missing_skills'], True)
            st.markdown('#### Preferred skills not evidenced')
            chips(result['preferred_skills_missing'], True)
        st.markdown('#### Score breakdown')
        st.dataframe([{'Category': k.title(), 'Category match': 'Not applicable' if v['rate'] is None else f"{v['rate']:g}%",
                       'Effective weight': f"{v['effective_weight']:g}%", 'Points / 100': v['points']}
                      for k, v in result['score_breakdown'].items()], hide_index=True, use_container_width=True)
    with keywords:
        x, y = st.columns(2)
        with x:
            st.markdown('#### Found in your resume')
            chips(result['ats_keywords_found'])
        with y:
            st.markdown('#### Not found in your resume')
            chips(result['ats_keywords_missing'], True)
        st.info('Keyword checks use literal phrases with word boundaries. Include missing terms only when they truthfully describe your skills.')
    with advice:
        st.markdown('#### Final assessment')
        st.write(result['final_assessment'])
        x, y = st.columns(2)
        with x:
            st.markdown('#### Strengths')
            bullets(result['strengths'])
            st.markdown('#### Resume problems')
            bullets(result['problems'])
        with y:
            st.markdown('#### Recommended next steps')
            bullets(result['recommendations'])
    with evidence:
        st.caption('Base weights: skills 35%, keywords 25%, experience 20%, education 10%, text quality 10%. Unspecified categories are excluded and remaining weights are normalized. Preferred skills affect the score only when no required skills are listed. Experience/education: met = 1, partial = 0.5, not evidenced = 0. Python calculates all weighted totals.')
        st.caption('Experience and education statuses are AI judgments checked for supporting quotes. Quote validation verifies text presence, not the truth of a claim. Review the evidence below.')
        for category, entries in result['evidence'].items():
            if entries:
                with st.expander(category.replace('_', ' ').title()):
                    st.dataframe(entries, hide_index=True, use_container_width=True)
        st.markdown('#### Text quality checks')
        for check in result['quality_checks']:
            st.write(('✓ ' if check['passed'] else '○ ') + check['check'])
        st.caption('Each check has equal weight. These simple English-text heuristics do not assess layout, columns or actual ATS parsing.')
        with st.expander('Extracted resume text'):
            st.text(st.session_state['resume_text'])
    st.download_button('Download full JSON report', json.dumps(result, indent=2, ensure_ascii=False),
                       'resume_analysis.json', 'application/json', use_container_width=True)
else:
    st.divider()
    a, b, c = st.columns(3)
    with a:
        st.markdown('#### Find your fit')
        st.caption('Understand which requirements your resume already supports.')
    with b:
        st.markdown('#### See the evidence')
        st.caption('Review source quotes and a transparent score breakdown.')
    with c:
        st.markdown('#### Know what to improve')
        st.caption('Get specific suggestions without inventing experience.')
