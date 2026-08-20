import streamlit as st
from google import genai
from google.genai import types
import json
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
        padding: 0.6rem; border-radius: 6px; border: none;
    }
    .stButton > button:hover { background-color: #374151; color: white; }
    .stTextArea textarea { border-radius: 6px; border: 1px solid #d1d5db; font-size: 0.95rem; }
    h1 { font-weight: 600; color: #111827; font-size: 1.75rem; margin-bottom: 0.25rem; }
    .subtitle { color: #6b7280; font-size: 0.95rem; margin-bottom: 0.5rem; }
    .project-note { color: #9ca3af; font-size: 0.82rem; margin-bottom: 1.5rem; }
    .skill-pill {
        display: inline-block; border-radius: 6px; padding: 0.3rem 0.75rem;
        margin: 0.2rem 0.3rem 0.2rem 0; font-size: 0.88rem;
    }
    .have { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .missing { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .score-box {
        text-align: center; padding: 1.5rem; background-color: #F9FAFB;
        border-radius: 8px; margin-bottom: 1.5rem;
    }
    .score-num { font-size: 2.2rem; font-weight: 700; color: #111827; }
    .score-label { color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.03em; }
    .section-divider { border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0 1.5rem 0; }
    .section-label {
        color: #9ca3af; text-transform: uppercase; font-size: 0.75rem;
        letter-spacing: 0.03em; margin-bottom: 0.5rem;
    }
    .bullet-card {
        background-color: #F9FAFB; border: 1px solid #e5e7eb; border-radius: 8px;
        padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; font-size: 0.9rem; color: #111827;
    }
</style>
""", unsafe_allow_html=True)

st.title("Skill Gap Analyzer")
st.markdown('<div class="subtitle">Upload your resume and paste a job posting — see your skill match and generate a tailored cover letter.</div>', unsafe_allow_html=True)
st.markdown('<div class="project-note">An individual project by Ana · Built to help prep for real job applications.</div>', unsafe_allow_html=True)

with st.expander("About this project"):
    st.markdown("""
**The problem**

Job postings list a wall of required skills, and manually comparing that against your resume — then writing a tailored cover letter — is tedious and easy to get wrong.

**How it works**

The resume file is parsed to plain text, then sent to Gemini alongside the job posting using a structured JSON schema, so the model returns a categorized skill match (not vague prose) plus suggested resume bullet points. A second chained LLM call then drafts a cover letter grounded in that structured result, without inventing experience not present in the resume.

**What I learned**

Chaining two LLM calls — one for structured extraction, one for generation grounded in that extracted data — taught me how real AI features are composed from multiple steps rather than a single prompt, and how to handle file parsing (PDF/DOCX) as a practical part of an AI pipeline, not just clean pasted text.
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
resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"], label_visibility="collapsed")

st.write("")
st.markdown('<div class="section-label">Job posting</div>', unsafe_allow_html=True)
job_posting = st.text_area("Job posting", height=200, placeholder="Paste the job description here...", label_visibility="collapsed")

analyze = st.button("Analyze gap")

for key in ["result", "resume_text", "cover_letter"]:
    if key not in st.session_state:
        st.session_state[key] = None

if analyze:
    if not resume_file or not job_posting.strip():
        st.error("Please upload a resume and paste a job posting.")
    else:
        with st.spinner("Reading resume..."):
            resume_text = extract_text_from_file(resume_file)
            st.session_state.resume_text = resume_text

        if not resume_text.strip():
            st.error("Couldn't extract text from that file. Try a different format.")
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
                except json.JSONDecodeError:
                    st.error("Something went wrong parsing the response. Try again.")

if st.session_state.result:
    result = st.session_state.result
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
        <div class="score-num">{result.get('match_score', 0)}%</div>
        <div class="score-label">Match score</div>
    </div>
    """, unsafe_allow_html=True)

    st.write(result.get("summary", ""))
    st.write("")

    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    bullets = result.get("bullet_suggestions", [])

    st.markdown('<div class="section-label">Skills you have</div>', unsafe_allow_html=True)
    if matched:
        st.markdown("".join([f'<span class="skill-pill have">{s}</span>' for s in matched]), unsafe_allow_html=True)
    else:
        st.write("None found.")

    st.write("")
    st.markdown('<div class="section-label">Skills you\'re missing</div>', unsafe_allow_html=True)
    if missing:
        st.markdown("".join([f'<span class="skill-pill missing">{s}</span>' for s in missing]), unsafe_allow_html=True)
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
