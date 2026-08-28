import streamlit as st
from google import genai
from google.genai import types
import json
import math
import os
from pypdf import PdfReader
import docx

if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

st.set_page_config(page_title="Skill Gap Analyzer", page_icon=None, layout="centered")

st.markdown("""
<style>
    .main { background-color: #ffffff; }
    .block-container { padding-top: 3rem; max-width: 700px; }
    .stButton > button {
        width: 100%; background-color: #111827; color: white; font-weight: 500;
        padding: 0.6rem; border-radius: 6px; border: none; min-height: 44px;
    }
    .stButton > button:hover { background-color: #374151; color: white; }
    .stTextArea textarea { border-radius: 6px; border: 1px solid #d1d5db; font-size: 0.95rem; }
    h1 { font-weight: 600; color: #111827; font-size: 1.75rem; margin-bottom: 0.25rem; }
    .subtitle { color: #6b7280; font-size: 0.95rem; margin-bottom: 0.5rem; }
    .project-note { color: #9ca3af; font-size: 0.82rem; margin-bottom: 1.5rem; }
    .skill-pill {
        display: inline-flex; align-items: center; gap: 4px; border-radius: 6px; padding: 0.3rem 0.75rem;
        margin: 0.2rem 0.3rem 0.2rem 0; font-size: 0.88rem;
    }
    .have { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .missing { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .score-box {
        text-align: center; padding: 1.5rem; background-color: #F9FAFB;
        border-radius: 8px; margin-bottom: 1.5rem;
        display: flex; flex-direction: column; align-items: center;
    }
    .ring-wrap { position: relative; width: 132px; height: 132px; }
    .ring-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .ring-num { font-size: 2.15rem; font-weight: 700; color: #111827; line-height: 1; }
    .ring-label { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 5px; }
    .score-badge { display: inline-flex; align-items: center; padding: 5px 13px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; margin-top: 16px; }
    .score-badge.strong { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .score-badge.partial { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .score-badge.weak { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .score-caption { color: #6b7280; font-size: 0.82rem; margin-top: 8px; }
    .section-divider { border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0 1.5rem 0; }
    .section-label {
        color: #9ca3af; text-transform: uppercase; font-size: 0.75rem;
        letter-spacing: 0.03em; margin-bottom: 0.5rem;
    }
    .bullet-card {
        background-color: #F9FAFB; border: 1px solid #e5e7eb; border-radius: 8px;
        padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; font-size: 0.9rem; color: #111827;
    }
    .example-card {
        position: relative; border: 1.5px dashed #d1d5db; border-radius: 10px;
        background-color: #FAFAFB; padding: 1.5rem 1.5rem 1.25rem 1.5rem; margin-top: 0.5rem;
    }
    .example-tag {
        position: absolute; top: -0.65rem; left: 1rem; background-color: #111827; color: white;
        font-size: 0.72rem; font-weight: 500; padding: 0.15rem 0.7rem; border-radius: 999px;
        letter-spacing: 0.02em;
    }
    .example-row { display: flex; align-items: center; gap: 1.25rem; }
    .mini-ring-wrap { position: relative; width: 78px; height: 78px; flex-shrink: 0; }
    .mini-ring-center {
        position: absolute; inset: 0; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
    }
    .mini-ring-num { font-size: 1.05rem; font-weight: 700; color: #111827; line-height: 1.1; }
    .mini-ring-label { color: #9ca3af; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.03em; }
    .example-copy { color: #374151; font-size: 0.88rem; line-height: 1.45; }
    .example-pills { margin-top: 1rem; }
    .example-caption { color: #9ca3af; font-size: 0.78rem; margin-top: 0.6rem; }
    .lp { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .lp-eyebrow {
        display: block; text-align: center; color: #9ca3af; text-transform: uppercase;
        font-size: 0.76rem; letter-spacing: 0.08em; font-weight: 600; font-family: 'IBM Plex Mono', monospace;
        margin-bottom: 8px;
    }
    h1.lp-h1 {
        font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 2.3rem; line-height: 1.15;
        letter-spacing: -0.02em; color: #111827; margin: 0; text-align: center;
    }
    p.lp-lead { font-size: 1.05rem; color: #6b7280; line-height: 1.6; text-align: center; margin: 16px 0 0 0; }
    h2.lp-h2 { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.55rem; margin: 0 0 14px 0; color: #111827; text-align: center; }
    a.lp-ghost-link { display: block; text-align: center; margin-top: 18px; font-size: 0.92rem; color: #6b7280; font-weight: 600; }

    .lp-result-card {
        position: relative; display: flex; align-items: center; gap: 20px;
        border: 1.5px dashed #d1d5db; border-radius: 14px; background: #FAFAFB; padding: 24px 26px; margin-top: 32px;
    }
    .lp-result-tag {
        position: absolute; top: -13px; left: 20px; background: #111827; color: white;
        font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 600; padding: 4px 12px; border-radius: 999px;
    }
    .lp-quote-card {
        margin-top: 26px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 26px 28px; text-align: left;
    }
    .lp-quote-card p { font-size: 1.02rem; line-height: 1.6; font-style: italic; margin: 0; color: #111827; }
    .lp-quote-attr { margin-top: 14px; font-size: 0.86rem; color: #6b7280; font-weight: 600; font-style: normal; }

    .lp-reaction-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px 20px; margin-bottom: 10px; }
    .lp-reaction-name { font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 0.96rem; color: #111827; }
    .lp-reaction-meta { font-family: -apple-system, sans-serif; font-weight: 500; font-size: 0.83rem; color: #9ca3af; }
    .lp-reaction-card p { margin: 8px 0 0 0; font-size: 0.89rem; color: #6b7280; line-height: 1.55; }

    .lp-step { display: flex; gap: 14px; padding: 14px 0; border-bottom: 1px solid #e5e7eb; }
    .lp-step:last-child { border-bottom: none; }
    .lp-step-num {
        font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 0.8rem; color: #6b7280;
        border: 1px solid #d1d5db; border-radius: 999px; width: 26px; height: 26px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
    }
    .lp-step h3 { font-family: 'Archivo', sans-serif; font-size: 0.98rem; font-weight: 700; margin: 0 0 4px 0; color: #111827; }
    .lp-step p { font-size: 0.88rem; color: #6b7280; margin: 0; line-height: 1.5; }

    .lp-principle { background: #111827; border-radius: 14px; padding: 36px 30px; text-align: center; }
    .lp-principle .lp-eyebrow { color: #9ca3af; }
    .lp-principle h2 { color: #ffffff; }
    .lp-principle p { color: #d1d5db; font-size: 0.95rem; line-height: 1.6; margin: 0; }
    @media (max-width: 480px) {
        .block-container { padding-top: 1.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
        h1 { font-size: 1.4rem !important; }
        .subtitle { font-size: 0.88rem; }
        .score-box { padding: 1rem; }
        .ring-num { font-size: 1.75rem; }
        .bullet-card { padding: 0.75rem 0.9rem; }
    }
    @media (prefers-color-scheme: dark) {
        .stApp, .main { background-color: #0B0E14; }
        header[data-testid="stHeader"] { background-color: #0B0E14; }
        h1 { color: #F3F4F6; }
        .subtitle { color: #9CA3AF; }
        .project-note { color: #6B7280; }
        .section-label { color: #6B7280; }
        .stTextArea textarea { background-color: #161B24; color: #F3F4F6; border-color: #323A4A; }
        .stButton > button { background-color: #F3F4F6; color: #0B0E14; }
        .stButton > button:hover { background-color: #E5E7EB; color: #0B0E14; }
        .score-box { background-color: #161B24; }
        .ring-num { color: #F3F4F6; }
        .ring-label { color: #9CA3AF; }
        .ring-wrap svg circle:nth-child(1) { stroke: #262D3A; }
        .ring-progress.strong { stroke: #34D399; }
        .ring-progress.partial { stroke: #FBBF24; }
        .ring-progress.weak { stroke: #F87171; }
        .score-badge.strong { background: rgba(52,211,153,0.14); color: #34D399; border: 1px solid rgba(52,211,153,0.35); }
        .score-badge.partial { background: rgba(245,158,11,0.14); color: #FBBF24; border: 1px solid rgba(245,158,11,0.35); }
        .score-badge.weak { background: rgba(248,113,113,0.14); color: #F87171; border: 1px solid rgba(248,113,113,0.35); }
        .score-caption { color: #9CA3AF; }
        .section-divider { border-top: 1px solid #262D3A; }
        .bullet-card { background-color: #161B24; border: 1px solid #262D3A; color: #F3F4F6; }
        .have { background-color: rgba(52,211,153,0.14); color: #34D399; border: 1px solid rgba(52,211,153,0.35); }
        .missing { background-color: rgba(248,113,113,0.14); color: #F87171; border: 1px solid rgba(248,113,113,0.35); }
        .example-card { background-color: #161B24; border-color: #323A4A; }
        .example-copy { color: #D1D5DB; }
        .mini-ring-num { color: #F3F4F6; }
        .mini-ring-wrap svg circle:nth-child(1) { stroke: #262D3A; }
        .mini-ring-wrap svg circle:nth-child(2) { stroke: #F3F4F6; }
        h1.lp-h1 { color: #F3F4F6; }
        p.lp-lead { color: #9CA3AF; }
        a.lp-ghost-link { color: #9CA3AF; }
        h2.lp-h2 { color: #F3F4F6; }
        .lp-result-card { background: #161B24; border-color: #323A4A; }
        .lp-quote-card { background: #0B0E14; border-color: #262D3A; }
        .lp-quote-card p { color: #F3F4F6; }
        .lp-quote-attr { color: #9CA3AF; }
        .lp-reaction-card { background: #0B0E14; border-color: #262D3A; }
        .lp-reaction-name { color: #F3F4F6; }
        .lp-reaction-card p { color: #9CA3AF; }
        .lp-step { border-color: #262D3A; }
        .lp-step h3 { color: #F3F4F6; }
        .lp-principle { background: #F3F4F6; }
        .lp-principle .lp-eyebrow { color: #6B7280; }
        .lp-principle h2 { color: #0B0E14; }
        .lp-principle p { color: #4B5563; }
    }
</style>
""", unsafe_allow_html=True)

if "show_landing" not in st.session_state:
    st.session_state.show_landing = True

if st.session_state.show_landing:
    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500;600&display=swap">',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="lp">
        <div class="lp-eyebrow">Built for college students &amp; new grads</div>
        <h1 class="lp-h1">Stop rewriting your resume for every application.</h1>
        <p class="lp-lead">Upload your resume and a job posting. Get an honest match score, see exactly what's missing, and generate a cover letter that doesn't oversell it — in under a minute.</p>
    </div>
    """, unsafe_allow_html=True)

    _, cta_col, _ = st.columns([1, 2, 1])
    with cta_col:
        if st.button("Try Skill Gap Analyzer", key="cta_hero", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("""
    <div class="lp">
      <a class="lp-ghost-link" href="#how-it-works">See how it works ↓</a>
      <div class="lp-result-card">
        <span class="lp-result-tag">Example result</span>
        <div class="ring-wrap" style="width:88px; height:88px;">
          <svg width="88" height="88" viewBox="0 0 88 88">
            <circle cx="44" cy="44" r="37" fill="none" stroke="#e5e7eb" stroke-width="8"/>
            <circle cx="44" cy="44" r="37" fill="none" stroke="#047857" stroke-width="8" stroke-linecap="round"
              stroke-dasharray="232.5" stroke-dashoffset="41.9" transform="rotate(-90 44 44)"/>
          </svg>
          <div class="ring-center">
            <div class="ring-num" style="font-size:1.3rem;">82%</div>
            <div class="ring-label">Match</div>
          </div>
        </div>
        <div>
          <span class="score-badge strong" style="margin-top:0;">Strong match</span>
          <div style="margin-top:8px;">
            <span class="skill-pill have">Python</span><span class="skill-pill have">SQL</span><span class="skill-pill missing">Docker</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" id="why-we-built-this">', unsafe_allow_html=True)

    st.markdown("""
    <div class="lp">
        <div class="lp-eyebrow">Why we built this</div>
        <h2 class="lp-h2">We talked to college students who were already job hunting.</h2>
        <p class="lp-lead" style="margin-top:0;">
            We asked freshmen, sophomores, juniors, and seniors — students actually applying to internships and entry-level roles — about their job search experience. The same frustrations came up again and again: getting ghosted after applying, and having to rewrite a resume and write a brand-new cover letter for every single posting, even with real experience already on the page.
        </p>
        <div class="lp-quote-card">
            <p>"I had a hard time finding a job even with experience. Companies would ghost me, and I had to update my resume and write a new cover letter every time."</p>
            <div class="lp-quote-attr">— Altynai, senior, Chemistry</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="lp-eyebrow">Same gap, three different reactions</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="lp-reaction-card">
        <span class="lp-reaction-name">Altynai</span> <span class="lp-reaction-meta">· Senior, Chemistry</span>
        <p>Found a posting she wasn't fully qualified for — decided not to apply at all.</p>
    </div>
    <div class="lp-reaction-card">
        <span class="lp-reaction-name">Arsh</span> <span class="lp-reaction-meta">· Junior, CS</span>
        <p>Same situation — moved on and looked for a different listing instead.</p>
    </div>
    <div class="lp-reaction-card">
        <span class="lp-reaction-name">Rima</span> <span class="lp-reaction-meta">· Sophomore, Data Analytics</span>
        <p>Added the missing skills to her resume based on the job description, and started teaching herself.</p>
    </div>
    <p class="lp-lead" style="font-size: 0.92rem; margin-top: 18px;">
        Asked to rate their confidence that their resume actually matched a posting, before hitting submit, on a scale of 1 to 5: they answered 1, 2, and 3. Nobody rated higher. None of them had tried an AI tool for any of this yet.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" id="how-it-works">', unsafe_allow_html=True)

    st.markdown("""
    <div class="lp">
        <div class="lp-eyebrow">How it works</div>
        <h2 class="lp-h2">Four steps. No account needed.</h2>
        <div class="lp-step">
            <div class="lp-step-num">01</div>
            <div><h3>Add your resume</h3><p>Upload a PDF, DOCX, or TXT — or just paste the text directly. No account, no file left behind.</p></div>
        </div>
        <div class="lp-step">
            <div class="lp-step-num">02</div>
            <div><h3>Paste the job posting</h3><p>Drop in the full listing. The tool reads the actual required skills, not just keywords.</p></div>
        </div>
        <div class="lp-step">
            <div class="lp-step-num">03</div>
            <div><h3>See your real match score</h3><p>What you have, what's missing, and honest suggestions for closing the gap — never a fabricated bullet point.</p></div>
        </div>
        <div class="lp-step">
            <div class="lp-step-num">04</div>
            <div><h3>Generate your cover letter</h3><p>A tailored, editable draft grounded in your actual resume — ready to download in seconds.</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="lp-principle">
        <div class="lp-eyebrow">Built on one rule</div>
        <h2 class="lp-h2" style="margin-bottom:10px;">The tool never lies for you.</h2>
        <p>When a skill is missing, Skill Gap Analyzer doesn't invent experience you don't have — it tells you what kind of project would actually close the gap. A tool that helps you get a job by fabricating your background isn't helping you. It's setting up the interview to fail.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="lp">
        <h2 class="lp-h2">Ready to see your match score?</h2>
        <p class="lp-lead" style="margin-top:0;">Free. No account. Built for students actually applying right now.</p>
    </div>
    """, unsafe_allow_html=True)

    _, cta_col2, _ = st.columns([1, 2, 1])
    with cta_col2:
        if st.button("Try Skill Gap Analyzer", key="cta_final", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown(
        '<p style="text-align:center; margin-top:14px;"><a class="lp-ghost-link" style="display:inline; margin-top:0;" href="https://github.com/Anajinaaa/skill-gap-analyzer" target="_blank" rel="noopener noreferrer">View on GitHub</a></p>',
        unsafe_allow_html=True,
    )

    st.stop()

back_col, _ = st.columns([1, 5])
with back_col:
    if st.button("← Back", key="back_to_landing"):
        st.session_state.show_landing = True
        st.rerun()

st.title("Skill Gap Analyzer")
st.markdown('<div class="subtitle">Built for STEM students — see how your resume stacks up against a job posting, close the gaps that matter, and draft a cover letter that doesn\'t oversell it.</div>', unsafe_allow_html=True)
st.markdown('<div class="project-note">An individual project by Ana · Built for STEM students prepping for internship and new-grad applications.</div>', unsafe_allow_html=True)

with st.expander("About this project"):
    st.markdown("""
**The problem**

Job postings list a wall of required skills, and manually comparing that against your resume — then writing a tailored cover letter — is tedious and easy to get wrong.

**How it works**

The resume file is parsed to plain text, then sent to Gemini alongside the job posting using a structured JSON schema, so the model returns a categorized skill match (not vague prose) plus suggested resume bullet points. A second chained LLM call then drafts a cover letter grounded in that structured result, without inventing experience not present in the resume.

**What I learned**

Chaining two LLM calls — one for structured extraction, one for generation grounded in that extracted data — taught me how real AI features are composed from multiple steps rather than a single prompt, and how to handle file parsing (PDF/DOCX) as a practical part of an AI pipeline, not just clean pasted text.
    """)

with st.expander("Tips for STEM students"):
    st.markdown("""
**What employers actually screen for**

NACE's Job Outlook surveys ask employers what they look for on student resumes. The gap is rarely the skills themselves — it's whether students actually write them down with evidence:

- Problem-solving ability — nearly 90% of employers screen for it
- Teamwork — about 80%
- Written and verbal communication — 70%+
- Technical skills — 70%+
- Initiative, work ethic, adaptability, and analytical/quantitative skills — all cited by a majority
- More than half of employers said they look for 10+ distinct skills — breadth matters, but only if each one has proof behind it

**Common mistakes students make**

- Listing tools without evidence — say what you built and what problem it solved, not just "Python, React, SQL"
- Treating every bullet as equally important — three well-explained projects beat eleven generic ones
- Sending the same resume to every posting — tailor it to what the listing actually asks for
- Skipping proofreading — a typo in your contact info can cost you the interview before it starts
- Leaving off older or "basic" technical skills — list your full stack, most to least proficient, don't just show off the impressive parts
- Disguising experience gaps instead of showing your actual thought process — employers can tell, and it reads worse than an honest gap

*Sources: NACE Job Outlook 2026, College Recruiter (2026), Emory University Career & Professional Development STEM Resume Guide.*
    """)

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document = docx.Document(uploaded_file)
        return "\n".join([para.text for para in document.paragraphs])
    else:
        return uploaded_file.read().decode("utf-8")

st.markdown('<div class="section-label">Resume</div>', unsafe_allow_html=True)
upload_tab, paste_tab = st.tabs(["Upload file", "Paste text"])
with upload_tab:
    resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"], label_visibility="collapsed", help="Upload a PDF, DOCX, or TXT file, up to 10MB.")
    st.caption("PDF, DOCX, or TXT · up to 10MB")
with paste_tab:
    resume_pasted_text = st.text_area("Paste your resume", height=182, placeholder="Paste your resume text here...", label_visibility="collapsed")

has_resume_input = bool(resume_file) or bool(resume_pasted_text and resume_pasted_text.strip())

st.write("")
st.markdown('<div class="section-label">Job posting</div>', unsafe_allow_html=True)
job_posting = st.text_area("Job posting", height=200, placeholder="Paste the job description here...", label_visibility="collapsed")

analyze = st.button("Analyze gap")

for key in ["result", "resume_text", "cover_letter", "updated_resume"]:
    if key not in st.session_state:
        st.session_state[key] = None

if not st.session_state.result:
    st.markdown('<div class="section-label">See what you\'ll get</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="example-card">
        <span class="example-tag">Example</span>
        <div class="example-row">
            <div class="mini-ring-wrap">
                <svg width="78" height="78" viewBox="0 0 78 78">
                    <circle cx="39" cy="39" r="35.5" fill="none" stroke="#e5e7eb" stroke-width="7" />
                    <circle cx="39" cy="39" r="35.5" fill="none" stroke="#111827" stroke-width="7"
                        stroke-linecap="round" stroke-dasharray="223.05" stroke-dashoffset="40.15"
                        transform="rotate(-90 39 39)" />
                </svg>
                <div class="mini-ring-center">
                    <div class="mini-ring-num">82%</div>
                    <div class="mini-ring-label">Match</div>
                </div>
            </div>
            <div class="example-copy">A match score, which skills you already show, and which ones are worth adding — plus a cover letter you can edit and download.</div>
        </div>
        <div class="example-pills">
            <span class="skill-pill have">Figma</span><span class="skill-pill have">User research</span><span class="skill-pill missing">Design systems</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="example-caption">Sample data — your results will use your own resume and job posting.</div>', unsafe_allow_html=True)

if analyze:
    if not has_resume_input or not job_posting.strip():
        st.error("Add your resume (upload a file or paste the text) and the job posting — both are needed to run the comparison.")
    else:
        with st.spinner("Reading resume..."):
            if resume_file:
                try:
                    resume_text = extract_text_from_file(resume_file)
                except Exception:
                    resume_text = ""
            else:
                resume_text = resume_pasted_text
            st.session_state.resume_text = resume_text

        if len(resume_text.strip()) < 40:
            if resume_file:
                st.error("We couldn't read enough text from that file — it might be corrupted, password-protected, or a scanned/image-based PDF. Try a DOCX or TXT file instead, or paste your resume text directly.")
            else:
                st.error("That doesn't look like enough resume text to compare against a job posting — paste more and try again.")
        else:
            with st.spinner("Comparing..."):
                client = genai.Client()
                prompt = f"""Compare this resume against this job posting. Extract the required skills from the job posting, then determine which ones appear in the resume (matched) and which are missing. Give a match score from 0-100. For each missing skill, suggest one honest, non-fabricated resume bullet point rewrite that could naturally incorporate it IF the candidate's existing experience plausibly supports it — otherwise suggest what kind of project or experience would close that gap.

JOB POSTING:
{job_posting}

RESUME:
{resume_text}"""

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema={
                            "type": "OBJECT",
                            "properties": {
                                "match_score": {"type": "INTEGER"},
                                "matched_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "missing_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "summary": {"type": "STRING"},
                                "bullet_suggestions": {
                                    "type": "ARRAY",
                                    "items": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "skill": {"type": "STRING"},
                                            "suggestion": {"type": "STRING"}
                                        },
                                        "required": ["skill", "suggestion"]
                                    }
                                }
                            },
                            "required": ["match_score", "matched_skills", "missing_skills", "summary", "bullet_suggestions"]
                        }
                    )
                )
                try:
                    st.session_state.result = json.loads(response.text)
                    st.session_state.cover_letter = None
                    st.session_state.updated_resume = None
                except json.JSONDecodeError:
                    st.error("That comparison didn't come through cleanly — this is usually temporary. Press Analyze gap again and it should go through.")

if st.session_state.result:
    result = st.session_state.result
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    score = result.get('match_score', 0)
    circumference = 2 * math.pi * 54
    dash_offset = circumference * (1 - score / 100)

    if score >= 75:
        tier_label, tier_class, tier_color = "Strong match", "strong", "#047857"
    elif score >= 50:
        tier_label, tier_class, tier_color = "Partial match", "partial", "#B45309"
    else:
        tier_label, tier_class, tier_color = "Needs work", "weak", "#B91C1C"

    matched_count = len(result.get('matched_skills', []))
    total_count = matched_count + len(result.get('missing_skills', []))
    caption = f"{matched_count} of {total_count} required skills found"

    st.markdown(f"""
    <div class="score-box">
        <div class="ring-wrap">
          <svg width="132" height="132" viewBox="0 0 132 132">
            <circle cx="66" cy="66" r="54" fill="none" stroke="#e5e7eb" stroke-width="11"/>
            <circle cx="66" cy="66" r="54" fill="none" stroke="{tier_color}" stroke-width="11" stroke-linecap="round" stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{dash_offset:.1f}" transform="rotate(-90 66 66)" class="ring-progress {tier_class}"/>
          </svg>
          <div class="ring-center">
            <div class="ring-num">{score}%</div>
            <div class="ring-label">Match</div>
          </div>
        </div>
        <div class="score-badge {tier_class}">{tier_label}</div>
        <div class="score-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write(result.get("summary", ""))
    st.write("")

    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    bullets = result.get("bullet_suggestions", [])

    st.markdown('<div class="section-label">Skills you have</div>', unsafe_allow_html=True)
    if matched:
        st.markdown("".join([f'<span class="skill-pill have"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M3.5 8.5L6.5 11.5L12.5 4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{s}</span>' for s in matched]), unsafe_allow_html=True)
    else:
        st.write("None found.")

    st.write("")
    st.markdown('<div class="section-label">Skills you\'re missing</div>', unsafe_allow_html=True)
    if missing:
        st.markdown("".join([f'<span class="skill-pill missing"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>{s}</span>' for s in missing]), unsafe_allow_html=True)
    else:
        st.write("None — great match!")

    if bullets:
        st.write("")
        st.markdown('<div class="section-label">How to close the gaps</div>', unsafe_allow_html=True)
        for b in bullets:
            st.markdown(f"""
            <div class="bullet-card">
                <strong>{b.get('skill', '')}</strong><br>{b.get('suggestion', '')}
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.download_button(
        "Download analysis as JSON",
        data=json.dumps(result, indent=2),
        file_name="skill_gap_analysis.json",
        mime="application/json"
    )

    if bullets:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Updated resume</div>', unsafe_allow_html=True)

        if st.button("Generate updated resume"):
            with st.spinner("Rewriting..."):
                client = genai.Client()
                suggestions_text = "\n".join([f"- {b.get('skill', '')}: {b.get('suggestion', '')}" for b in bullets])

                resume_prompt = f"""Rewrite this resume to incorporate the following suggested changes, where the candidate's existing experience plausibly supports them. Do not fabricate experience, employers, dates, or credentials not present in the original resume. Keep the original resume's structure, section order, and formatting style. No placeholder brackets.

SUGGESTED CHANGES:
{suggestions_text}

ORIGINAL RESUME:
{st.session_state.resume_text}"""

                resume_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=resume_prompt
                )
                st.session_state.updated_resume = resume_response.text

        if st.session_state.updated_resume:
            edited_resume = st.text_area(
                "Edit your updated resume",
                value=st.session_state.updated_resume,
                height=350,
                label_visibility="collapsed"
            )
            st.download_button(
                "Download updated resume",
                data=edited_resume,
                file_name="updated_resume.txt",
                mime="text/plain"
            )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Cover letter</div>', unsafe_allow_html=True)

    tone = st.selectbox("Tone", ["Professional", "Conversational", "Concise"], label_visibility="collapsed")

    if st.button("Generate cover letter"):
        with st.spinner("Drafting..."):
            client = genai.Client()
            tone_instruction = {
                "Professional": "Use a polished, formal professional tone.",
                "Conversational": "Use a warm, conversational but still professional tone.",
                "Concise": "Keep it tight and direct — no more than 3 short paragraphs, minimal filler."
            }[tone]

            cover_prompt = f"""Write a cover letter for this job posting, based on this resume. {tone_instruction} Emphasize these matched skills naturally: {', '.join(matched)}. Do not fabricate experience not present in the resume. No placeholder brackets.

JOB POSTING:
{job_posting}

RESUME:
{st.session_state.resume_text}"""

            letter_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=cover_prompt
            )
            st.session_state.cover_letter = letter_response.text

    if st.session_state.cover_letter:
        edited_letter = st.text_area(
            "Edit your cover letter",
            value=st.session_state.cover_letter,
            height=350,
            label_visibility="collapsed"
        )
        st.download_button(
            "Download cover letter",
            data=edited_letter,
            file_name="cover_letter.txt",
            mime="text/plain"
        )
