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
:root {--ink:#232238;--muted:#747386;--purple:#7055db;}
.stApp {background:#f8f7fc;color:var(--ink);}
.block-container {max-width:1240px;padding:2.2rem 2.4rem 3rem;}
h1,h2,h3,h4 {letter-spacing:-.04em;color:var(--ink);}
[data-testid="stHeader"] {background:rgba(248,247,252,.92);}
[data-testid="stSidebar"] {background:#eeecf7;border-right:1px solid #e4e0f1;}
[data-testid="stSidebar"] .block-container {padding:2rem 1.2rem;}
.brand {display:flex;align-items:center;gap:11px;font-weight:750;font-size:21px;letter-spacing:-.7px;}
.brand-icon {background:#7055db;color:white;border-radius:13px;padding:7px 12px;font-size:25px;}
.brand small {display:block;font-size:10px;letter-spacing:2px;color:#85819b;margin-top:2px;}
.side-label {font-size:10px;letter-spacing:2px;color:#89849d;margin:34px 0 13px;font-weight:700;}
.side-item {padding:12px 14px;border-radius:10px;color:#6e687f;margin:5px 0;font-size:14px;}
.side-item.active {background:#ddd6f6;color:#5d43be;font-weight:650;}
.side-note {background:#e5e0f4;border:1px solid #dad3ee;padding:19px;border-radius:15px;margin-top:35px;font-size:13px;line-height:1.7;color:#706882;}
.topline {display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#817b91;margin:4px 0 30px;}
.pill {background:#eee9fc;color:#6b4ed1;border:1px solid #ded5fa;padding:6px 11px;border-radius:30px;font-size:11px;font-weight:650;}
.hero {display:grid;grid-template-columns:1.5fr 1fr;gap:30px;align-items:center;margin:0 0 28px;padding:34px 38px;background:linear-gradient(115deg,#eee9fc,#f3f0fc 58%,#e9e4f8);border:1px solid #e3ddf3;border-radius:24px;overflow:hidden;}
.eyebrow {font-size:10px;letter-spacing:2px;color:#7961bd;font-weight:750;}
.hero h1 {font-size:clamp(30px,3.1vw,44px);line-height:1.13;margin:16px 0;letter-spacing:-1.8px;font-weight:750;}
.hero h1 span {color:#7854d4;}
.hero p {color:#79728a;font-size:14px;line-height:1.8;max-width:430px;margin-bottom:16px;}
.hero-tags {display:flex;gap:14px;font-size:10px;color:#736b84;flex-wrap:wrap;}
.document-scene {position:relative;min-height:230px;display:flex;align-items:center;justify-content:center;}
.document {width:172px;background:white;border:1px solid #e8e2f4;border-radius:13px;padding:22px;transform:rotate(-7deg);box-shadow:0 18px 45px #63538d20;}
.doc-head {display:flex;gap:10px;align-items:center;margin-bottom:20px;}
.doc-avatar {width:32px;height:32px;border-radius:50%;background:#e5dcfa;color:#9165d3;display:grid;place-items:center;}
.doc-line {height:5px;background:#eae6f1;border-radius:4px;margin:8px 0;}
.doc-line.purple {background:#cec0ee;width:65%;}
.float-label {position:absolute;background:white;border:1px solid #e7e0f1;border-radius:11px;box-shadow:0 8px 26px #65558214;padding:12px 15px;font-size:11px;color:#635976;}
.float-label.first {right:0;top:21px;transform:rotate(4deg);}
.float-label.second {left:0;bottom:10px;transform:rotate(3deg);}
.float-label b {color:#7854d4;}
.section-header {display:flex;align-items:center;justify-content:space-between;margin:27px 0 13px;}
.section-header h3 {font-size:20px;margin:0;}.section-header span {font-size:12px;color:#918b9d;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:18px!important;border-color:#e7e3ef!important;background:#fff;}
.card-title {display:flex;gap:12px;align-items:center;margin:2px 0 18px;}
.card-number {background:#f0eafa;border-radius:10px;color:#7954ca;padding:9px 12px;font-size:13px;font-weight:700;}
.card-title strong {font-size:16px;}.card-title small {display:block;color:#938b9d;font-size:11px;margin-top:3px;}
[data-testid="stFileUploaderDropzone"] {background:#faf8fe;border:1.5px dashed #cfc4e7;border-radius:13px;padding:30px 14px;}
[data-testid="stTextArea"] textarea {background:#fcfbff;border-radius:12px;font-size:13px;line-height:1.7;}
.stButton > button[kind="primary"] {background:#7452d6;border:0;border-radius:12px;min-height:49px;box-shadow:0 5px 15px #7452d620;font-weight:650;}
.stButton > button[kind="primary"]:hover {background:#6442c4;box-shadow:0 7px 20px #7452d632;}
.stButton > button:focus-visible {outline:3px solid #bfaef0;outline-offset:3px;}
[data-testid="stMetric"] {background:white;border:1px solid #e7e2ef;border-radius:15px;padding:18px;}
[data-testid="stMetricValue"] {font-size:27px;color:#6542bd;}
[data-testid="stMetricLabel"] {color:#82788e;font-size:12px;}
[data-baseweb="tab-list"] {gap:8px;background:#efecf7;padding:5px;border-radius:12px;margin:18px 0;}
[data-baseweb="tab"] {padding:10px 17px!important;border-radius:9px!important;height:auto;}
[data-baseweb="tab"][aria-selected="true"] {background:white;color:#6c49c7;box-shadow:0 2px 7px #66558212;}
[data-baseweb="tab-highlight"] {display:none;}
.chip {display:inline-block;background:#edf7f2;color:#347959;border:1px solid #d7ebdf;border-radius:8px;padding:7px 11px;margin:4px;font-size:12px;}
.chip.gap {background:#fff3e8;color:#a16836;border-color:#f3dfc9;}
.feature {background:white;border:1px solid #e9e4f0;border-radius:16px;padding:22px;min-height:159px;}
.feature .icon {background:#f1eafa;color:#815bcb;padding:8px 11px;border-radius:10px;display:inline-block;margin-bottom:12px;}
.feature strong {display:block;font-size:14px;margin-bottom:6px;}.feature p {color:#92899d;font-size:12px;line-height:1.65;margin:0;}
.advice-item {display:flex;gap:11px;background:#fff;border:1px solid #e9e4f1;border-radius:12px;padding:15px;margin:9px 0;font-size:13px;line-height:1.7;color:#61586e;}
.advice-item span {color:#8767cd;font-weight:700;}
.score-row {display:flex;align-items:center;gap:22px;background:white;border:1px solid #e6e0ef;padding:25px;border-radius:18px;margin-bottom:20px;}
.score-ring {height:110px;width:110px;flex-shrink:0;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#805bd6 var(--score),#ede8f5 0);}
.score-ring div {height:89px;width:89px;border-radius:50%;background:white;display:grid;place-content:center;text-align:center;font-size:26px;font-weight:750;color:#7250bf;}
.score-ring small {font-size:9px;color:#a296b4;font-weight:500;letter-spacing:1px;}
.score-copy h3 {margin:4px 0 8px;font-size:24px;}.score-copy p {margin:0;color:#8b8096;font-size:13px;}
.footer {text-align:center;color:#a499b1;font-size:10px;letter-spacing:.4px;margin-top:38px;}
@media(max-width:800px) {.block-container {padding:1.5rem 1rem;}.hero {grid-template-columns:1fr;padding:25px;}.document-scene {display:none;}.hero h1 {font-size:33px;}.topline {margin-bottom:20px;}.section-header span {display:none;}.score-row {padding:18px;gap:15px;}.score-copy h3 {font-size:20px;}}
@media(prefers-reduced-motion:no-preference) {.hero {animation:enter .45s ease-out;}@keyframes enter {from {opacity:0;transform:translateY(6px)}to {opacity:1;transform:translateY(0)}}}
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
    for index, item in enumerate(items, 1):
        st.markdown(f'<div class="advice-item"><span>{index:02}</span><div>{escape(item)}</div></div>', unsafe_allow_html=True)
    if not items:
        st.caption('No items reported.')


server_key = setting('SENSENOVA_API_KEY')
model = setting('SENSENOVA_MODEL', DEFAULT_MODEL)

with st.sidebar:
    st.markdown('''<div class="brand"><div class="brand-icon">◈</div><div>Resume Analyzer<small>CAREER WORKSPACE</small></div></div>
<div class="side-label">YOUR WORKSPACE</div><div class="side-item active">◈ &nbsp; Resume analysis</div>
<div class="side-label">THREE SIMPLE STEPS</div><div class="side-item">01 &nbsp; Upload your resume</div><div class="side-item">02 &nbsp; Add the job description</div><div class="side-item">03 &nbsp; Discover your next steps</div>
<div class="side-note"><b>A little detail goes a long way.</b><br>Paste the full job description for a more useful comparison. Include the skills, qualifications and responsibilities.</div>''', unsafe_allow_html=True)
    st.caption('Match scores are estimates, not hiring predictions.')

st.markdown('''<div class="topline"><span>Workspace &nbsp; / &nbsp; <b>Resume analysis</b></span><span class="pill">✦ &nbsp; AI-powered insights</span></div>
<div class="hero"><div><div class="eyebrow">YOUR EXPERIENCE. YOUR NEXT OPPORTUNITY.</div>
<h1>A stronger resume.<br><span>A clearer next step.</span></h1>
<p>Discover how your experience fits the role, what’s missing, and where a few thoughtful changes can make a difference.</p>
<div class="hero-tags"><span>✓ Skill matching</span><span>✓ Keyword insights</span><span>✓ Practical guidance</span></div></div>
<div class="document-scene" aria-hidden="true"><div class="document"><div class="doc-head"><div class="doc-avatar">◈</div><div><div class="doc-line purple" style="width:65px"></div><div class="doc-line" style="width:45px"></div></div></div><div class="doc-line purple"></div><div class="doc-line"></div><div class="doc-line"></div><br><div class="doc-line purple"></div><div class="doc-line"></div><div class="doc-line" style="width:75%"></div></div><div class="float-label first">✦ &nbsp; <b>Discover your strengths</b></div><div class="float-label second">✓ &nbsp; Every match, with evidence</div></div></div>
<div class="section-header"><h3>Let’s find your fit</h3><span>Start with your resume and the role you want</span></div>''', unsafe_allow_html=True)
left, right = st.columns([1, 1.2], gap='medium')
with left:
    with st.container(border=True):
        st.markdown('<div class="card-title"><span class="card-number">01</span><div><strong>Your resume</strong><small>The experience you bring to the table</small></div></div>', unsafe_allow_html=True)
        upload = st.file_uploader('Upload PDF or DOCX', type=['pdf', 'docx'])
        st.caption('PDF or DOCX · Max 5 MB · Readable text required')
        if upload:
            st.success(f'Ready: {upload.name}')
        else:
            st.caption('Tip: use your most recent resume for the best comparison.')
with right:
    with st.container(border=True):
        st.markdown('<div class="card-title"><span class="card-number">02</span><div><strong>Your next opportunity</strong><small>Tell us what the employer is looking for</small></div></div>', unsafe_allow_html=True)
        job = st.text_area('Job description', height=185, max_chars=MAX_JOB_CHARS,
                           placeholder='Paste the job description here…\n\nInclude required skills, responsibilities, experience and qualifications.')
        st.caption(f'{len(job.split()):,} words · Include the full description for a detailed analysis')
consent = st.checkbox('I agree to send the extracted resume text and job description to SenseNova for analysis.')
st.caption('Your file is processed in memory. Analysis sends extracted text to SenseNova under its data policies.')

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
    score = max(0, min(100, result['match_score']))
    st.markdown(f'''<div class="section-header"><h3>Your match report</h3><span>From evidence to action</span></div><div class="score-row"><div class="score-ring" style="--score:{score}%"><div>{score:g}%<small>MATCH SCORE</small></div></div><div class="score-copy"><div class="eyebrow">YOUR APPLICATION SNAPSHOT</div><h3>{escape(result['final_result'])}</h3><p>Explore your strengths and focus on the gaps that matter for this role.</p></div></div>''', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header"><h3>Clarity for your next move</h3><span>Your report will appear here after analysis</span></div>', unsafe_allow_html=True)
    for column, icon, title, description in zip(st.columns(3), ['◈', '⌕', '↗'],
            ['Know your strengths', 'Spot the missing pieces', 'Make your next move'],
            ['See which skills and qualifications already align with the role.',
             'Identify important keywords and requirements your resume hasn’t shown yet.',
             'Get specific, honest recommendations you can put into practice.']):
        with column:
            st.markdown(f'<div class="feature"><span class="icon">{icon}</span><strong>{title}</strong><p>{description}</p></div>', unsafe_allow_html=True)
st.markdown('<div class="footer">BUILT FOR YOUR NEXT CHAPTER &nbsp; · &nbsp; AI RESUME ANALYZER</div>', unsafe_allow_html=True)
