from google import genai
from google.genai import types
import json, argparse, sys

client = genai.Client()

def extract_action_items(notes: str):
    if not notes or not notes.strip():
        print("Error: No text provided. Pass a file with --file or paste text with --text.")
        sys.exit(1)

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
        return json.loads(response.text)
    except json.JSONDecodeError:
        print("Error: Model did not return valid JSON. Try again or check your input.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract action items from meeting notes using AI.")
    parser.add_argument("--file", help="Path to a text file with meeting notes")
    parser.add_argument("--text", help="Meeting notes pasted directly as a string")
    parser.add_argument("--output", help="Path to save results as a JSON file (optional)")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file) as f:
                notes = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
    elif args.text:
        notes = args.text
    else:
        print("Error: Provide input with --file <path> or --text \"your notes here\"")
        sys.exit(1)

    result = extract_action_items(notes)
    output_json = json.dumps(result, indent=2)
    print(output_json)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"\nSaved to {args.output}")
