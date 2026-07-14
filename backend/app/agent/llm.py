import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_PRIMARY = os.getenv("GROQ_MODEL_PRIMARY", "llama-3.1-8b-instant")
MODEL_CONTEXT = os.getenv("GROQ_MODEL_CONTEXT", "llama-3.3-70b-versatile")

# Primary fast/cheap model -- used for structured extraction, edits, summaries
llm_primary = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_PRIMARY,
    temperature=0.2,
)

# Larger context model -- used when we need to reason over longer HCP history
llm_context = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_CONTEXT,
    temperature=0.3,
)


def extract_json(text: str) -> dict:
    """Groq/gemma sometimes wraps JSON in markdown fences -- strip and parse safely."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("json", "", 1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # last-resort: find the first {...} block
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass
    return {}
