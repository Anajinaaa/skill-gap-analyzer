import streamlit as st
from google import genai
from google.genai import types
import json

st.set_page_config(
    page_title="Action Item Extractor",
    page_icon=None,
    layout="centered"
)

st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }
    .block-container {
        padding-top: 3rem;
        max-width: 700px;
    }
    .stButton > button {
        width: 100%;
        background-color: #111827;
        color: white;
        font-weight: 500;
        padding: 0.6rem;
        border-radius: 6px;
        border: none;
        transition: background-color 0.15s;
    }
    .stButton > button:hover {
        background-color: #374151;
        color: white;
    }
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 0.95rem;
    }
    h1 {
        font-weight: 600;
        color: #111827;
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .project-note {
        color: #9ca3af;
        font-size: 0.82rem;
        margin-bottom: 1.5rem;
    }
    .project-note a {
        color: #6b7280;
    }
    .item-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
    }
    .item-task {
        font-weight: 500;
        font-size: 1rem;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    .item-meta {
        color: #6b7280;
        font-size: 0.85rem;
        margin-right: 1rem;
    }
    .item-label {
        color: #9ca3af;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.03em;
        margin-right: 0.3rem;
    }
    .section-divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("Action Item Extractor")
st.markdown('<div class="subtitle">Turn unstructured meeting notes into a clean task list — with owners and deadlines.</div>', unsafe_allow_html=True)
st.markdown('<div class="project-note">An individual project by Ana · <a href="https://github.com/Anajinaaa/meeting-action-extractor" target="_blank">View source on GitHub</a></div>', unsafe_allow_html=True)

with st.expander("About this project"):
    st.markdown("""
**The problem**

Meeting notes are usually messy, unstructured text — decisions, tasks, and casual comments all mixed together. Manually pulling out "who owes what by when" is tedious and things get missed.

**How it works**

This tool sends the raw notes to Gemini along with a strict JSON schema, so the model is constrained to return exactly `{task, owner, deadline}` for each item — not free-form prose that would need extra parsing. That structured output is what makes it usable as a real building block, not just a chat response.

**What I learned**

Building this taught me the difference between "calling an LLM" and integrating one into an application: designing schemas for reliable structured output, handling real API errors (auth formatting, deprecated models), and the gap between a script that works on one machine versus a tool other people can actually use — which is what pushed me to turn it into this web app.
    """)

notes = st.text_area(
    "Meeting notes",
    height=200,
    placeholder="Paste your meeting notes here...",
    label_visibility="collapsed"
)

extract = st.button("Extract action items")

if extract:
    if not notes.strip():
        st.error("Please paste some meeting notes first.")
    else:
        with st.spinner("Processing..."):
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"Extract action items from these meeting notes:\n\n{notes}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "action_items": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "task": {"type": "STRING"},
                                        "owner": {"type": "STRING"},
                                        "deadline": {"type": "STRING"}
                                    },
                                    "required": ["task"]
                                }
                            }
                        },
                        "required": ["action_items"]
                    }
                )
            )
            try:
                result = json.loads(response.text)
                items = result.get("action_items", [])

                if not items:
                    st.warning("No action items found in that text.")
                else:
                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                    st.markdown(f"**{len(items)} action item{'s' if len(items) != 1 else ''} found**")
                    st.write("")
                    for item in items:
                        owner = item.get("owner", "Unassigned")
                        deadline = item.get("deadline", "No deadline")
                        st.markdown(f"""
                        <div class="item-card">
                            <div class="item-task">{item.get('task', '—')}</div>
                            <span class="item-label">Owner</span><span class="item-meta">{owner}</span>
                            <span class="item-label">Due</span><span class="item-meta">{deadline}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")
                    st.download_button(
                        "Download as JSON",
                        data=json.dumps(result, indent=2),
                        file_name="action_items.json",
                        mime="application/json"
                    )
            except json.JSONDecodeError:
                st.error("Something went wrong parsing the response. Try again.")
