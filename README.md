# Meeting Action Item Extractor

A CLI tool that extracts structured action items from unstructured meeting notes using Gemini's structured output (JSON schema) capability.

## Example

**Input** (`sample_notes.txt`):

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
    },
    {
      "task": "Review the design mockups",
      "owner": "The team",
      "deadline": "Before the next sprint planning"
    }
  ]
}
```

## How it works

Uses Google's Gemini API with a defined JSON response schema to force structured, reliable output — no manual parsing or regex needed on the model's response.

## Setup

```bash
pip3 install google-genai
export GOOGLE_API_KEY="your-key-here"
```

## Usage

```bash
# From a file
python3 main.py --file sample_notes.txt

# From pasted text
python3 main.py --text "Sarah will send the report by Friday."

# Save output to a file
python3 main.py --file sample_notes.txt --output results.json
```

## Tech

- Python
- Gemini API (`gemini-3.6-flash`) with structured JSON output
