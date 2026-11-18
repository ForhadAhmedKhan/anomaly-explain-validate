import json
import os

from dotenv import load_dotenv

load_dotenv()

INSTRUCTIONS = """You explain flagged sensor anomalies to a maintenance engineer.

Rules:
- Use ONLY the numbers in the evidence below. Do not invent or estimate any number.
- Write 2 to 3 plain sentences: what happened, how big it was versus normal, how long it lasted.
- You may suggest one possible cause, but label it clearly as "possible" and do not state it as fact.
- If the evidence is thin or missing, say so instead of guessing.
- The data is synthetic test data; do not mention real-world incidents.
"""


def build_prompt(evidence):
    return INSTRUCTIONS + "\nEvidence (JSON):\n" + json.dumps(evidence, indent=2)


def explain(evidence, model=None):
    """Ask Gemini for a plain-language explanation of one anomaly."""
    from google import genai  # imported here so tests don't need the SDK or a key

    model = model or os.getenv("GEMINI_MODEL")
    if not model:
        raise RuntimeError("Set GEMINI_MODEL in your .env file (see list_models.py)")
    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    response = client.models.generate_content(model=model, contents=build_prompt(evidence))
    return response.text