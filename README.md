# AI Career Tools

Two small AI-powered tools built to explore structured LLM output and practical AI application engineering — built as an individual project by Ana.

## Skill Gap Analyzer (main project)

**Live demo:** https://skill-gap-analyzerr.streamlit.app

Upload a resume (PDF/DOCX/TXT) and paste a job posting to get a match score, a breakdown of matched vs. missing skills, honest suggestions for closing the gaps, and a tailored, editable cover letter.

### The problem

Job postings list a wall of required skills, and manually comparing that against your resume — then writing a tailored cover letter — is tedious and easy to get wrong.

### How it works

The resume is parsed to plain text, then sent to the Gemini API alongside the job posting using a strict JSON response schema, so the model returns a categorized skill match (not vague prose) plus suggested resume bullet points. A second, chained LLM call then uses that structured result to draft a cover letter — explicitly instructed not to fabricate experience not present in the resume.

### What I learned

Chaining two LLM calls — one for structured extraction, one for generation grounded in that extracted data — showed me how real AI features are composed from multiple steps, not a single prompt. Building this also meant handling practical, unglamorous engineering: parsing PDF/DOCX files, managing API keys and secrets correctly, and debugging real integration issues (auth header formatting, deprecated model versions, environment setup).

### Run it locally

```bash
pip3 install -r requirements.txt
```

Create `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-key-here"
```

```bash
streamlit run skillgap_app.py
```

### Tech

Python, Gemini API (`gemini-3.6-flash`) with structured JSON output, Streamlit, pypdf, python-docx

---

## Meeting Action Item Extractor (earlier project)

A CLI tool that extracts structured action items from unstructured meeting notes using the same schema-constrained generation pattern.

### Example

**Input:**
Sarah will send the updated budget spreadsheet by Friday.
Mike needs to follow up with the vendor about pricing next week. 
**Output:**
```json
{
  "action_items": [
    {
      "task": "Send the updated budget spreadsheet",
      "owner": "Sarah",
      "deadline": "Friday"
    },
    {
      "task": "Follow up with the vendor about pricing",
      "owner": "Mike",
      "deadline": "Next week"
    }
  ]
}
```

### Usage

```bash
# From a file
python3 main.py --file sample_notes.txt

# From pasted text
python3 main.py --text "Sarah will send the report by Friday."

# Save output to a file
python3 main.py --file sample_notes.txt --output results.json
```

### Tech

Python, Gemini API with structured JSON output
