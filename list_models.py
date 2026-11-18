from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
for m in client.models.list():
    actions = getattr(m, "supported_actions", None) or []
    if "generateContent" in actions:
        print(m.name)