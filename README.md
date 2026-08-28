# Skill Gap Analyzer

**Live demo:** https://skill-gap-analyzerr.streamlit.app
An individual project by Ana — built for my own job search, then put through a real UX audit.

Upload a resume (or just paste the text) and a job posting. Get an honest match score, a breakdown of matched vs. missing skills, honest suggestions for closing the gaps, a tailored cover letter, and a rewritten resume that actually incorporates the fix — all without ever inventing experience you don't have.

## The problem

Job postings list a wall of required skills. Comparing that against your own resume by hand — then writing a cover letter that actually responds to it — is slow, and it's easy to either undersell what you have or overclaim what you don't.

Before building this out further, I talked to a small group of college students — freshmen through seniors — who were actively applying to internships and entry-level roles. The same frustrations came up again and again: getting ghosted after applying, and having to rewrite a resume and write a brand-new cover letter for every single posting, even with real experience already on the page. Asked to rate their confidence that their resume actually matched a posting before hitting submit, on a scale of 1 to 5, they answered 1, 2, and 3 — nobody rated higher. None of them had tried an AI tool for any of this yet.

That gap is what this project is for.

## What it does

- **A real front door.** The app opens on a landing page — the problem, how it works, and what the students I talked to actually said — with a button that drops you straight into the tool. A back button returns you to it without losing your place.
- **Upload or paste your resume.** PDF, DOCX, TXT, or just paste the text directly — whichever is faster.
- **An honest match score.** A radial score ring colored by tier (green/amber/red for strong/partial/weak) so a weak match *looks* weak at a glance, not just in a caption underneath it.
- **A categorized skill breakdown.** What you have and what's missing, each marked with an icon as well as color, so the signal doesn't depend on being able to distinguish red from green.
- **Gap-closing suggestions that don't lie.** For each missing skill, the tool either suggests a resume bullet grounded in experience you actually have, or tells you what kind of project would genuinely close the gap — it never invents experience for you.
- **A generated cover letter and an updated resume**, both editable and downloadable, both grounded in your real resume text.

## Design decisions worth naming

- **The analysis and the cover letter are separate steps**, not one combined action. You see the score and decide if you agree with it before spending an API call generating a letter.
- **The score ring's color is tied to the match tier**, not fixed. I initially shipped it with a static near-black stroke regardless of score — a weak 38% match looked just as bold and confident as an 82% one. Caught it by actually looking at a bad result next to a good one, not from a checklist.
- **Structured JSON output**, not free-text prose, so the UI can render a scannable score/pills/cards layout instead of a wall of AI-generated text.
- **No fabrication, anywhere.** Every generated output — the match, the suggestions, the cover letter, the rewritten resume — is explicitly constrained to never invent experience, employers, or credentials that aren't in the original resume.

## The UX audit

Once the core tool worked, I ran it through a real audit and fixed what I found:

- **Accessibility** — skills were originally distinguished by color alone (a WCAG 1.4.1 violation, and unreadable for colorblind users). Fixed with icons on every pill.
- **Onboarding** — first-time users hit a blank upload box with no sense of what a good result looks like. Added an example card showing a sample result before anyone uploads anything.
- **Error handling** — every error used to say some version of "something went wrong." Rewritten to say what happened and what to do about it — and a corrupted or password-protected file used to crash the app outright with a raw Python traceback; now it fails gracefully.
- **Responsiveness** — added a mobile breakpoint, fixed tap targets to the 44px minimum, and caught a CSS specificity bug where the page title silently ignored its own font-size override on small screens.
- **Dark mode** — follows the system's `prefers-color-scheme` rather than adding another toggle to manage, including the score ring's tier colors.

## What I'd still improve

Everything above came from watching myself use the tool and from informal conversations with a handful of students — not a real usability study. The honest next step is putting it in front of people actively job-hunting and watching where they hesitate, not asking whether they liked it.

## Run it locally

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

## Tech

Python, Gemini API (`gemini-3.6-flash`) with structured JSON output, Streamlit, pypdf, python-docx

---

## Meeting Action Item Extractor (earlier project)

A CLI tool that extracts structured action items from unstructured meeting notes, using the same schema-constrained generation pattern this project builds on.

**Input:**
```
Sarah will send the updated budget spreadsheet by Friday.
Mike needs to follow up with the vendor about pricing next week.
```

**Output:**
```json
{
  "action_items": [
    { "task": "Send the updated budget spreadsheet", "owner": "Sarah", "deadline": "Friday" },
    { "task": "Follow up with the vendor about pricing", "owner": "Mike", "deadline": "Next week" }
  ]
}
```

```bash
python3 main.py --file sample_notes.txt
python3 main.py --text "Sarah will send the report by Friday."
python3 main.py --file sample_notes.txt --output results.json
```

**Tech:** Python, Gemini API with structured JSON output
