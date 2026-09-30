import json
import re
from typing import Any

from gemini_client import generate_text, GeminiError


def clean_json_block(text: str) -> str:
    """Remove Markdown fences and surrounding text around a JSON array/object."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start_array = text.find("[")
    end_array = text.rfind("]")
    if start_array != -1 and end_array > start_array:
        return text[start_array:end_array + 1]

    start_obj = text.find("{")
    end_obj = text.rfind("}")
    if start_obj != -1 and end_obj > start_obj:
        return text[start_obj:end_obj + 1]

    return text


def _validate_quiz(data: Any, count: int) -> list[dict]:
    if not isinstance(data, list):
        raise ValueError("Quiz response is not a list.")

    validated = []
    for item in data[:count]:
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        options = item.get("options", [])
        answer = str(item.get("answer", "")).strip()

        if not question or not isinstance(options, list) or len(options) != 4:
            continue

        options = [str(x).strip() for x in options]
        if any(not x for x in options):
            continue

        if answer not in options:
            # Accept an answer index from a model that returns one.
            index = item.get("correct_option_index")
            if isinstance(index, int) and 0 <= index < 4:
                answer = options[index]
            else:
                continue

        validated.append(
            {
                "question": question,
                "options": options,
                "answer": answer,
            }
        )

    if len(validated) < count:
        raise ValueError(
            f"Only {len(validated)} valid quiz questions were returned; "
            f"{count} were requested."
        )

    return validated


def generate_quiz(topic: str, count: int = 3) -> list[dict]:
    prompt = f"""
Create a multiple-choice educational quiz about: {topic}

Generate exactly {count} questions.
Each question must have exactly four options.
Make questions appropriate for a general learner.
Do not use trick questions.

Return ONLY valid JSON. No Markdown and no commentary.

JSON format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Exactly one option from the options array"
  }}
]
"""

    try:
        raw = generate_text(
            prompt,
            temperature=0.45,
            max_output_tokens=1800,
        )
        data = json.loads(clean_json_block(raw))
        return _validate_quiz(data, count)
    except (GeminiError, json.JSONDecodeError, ValueError) as exc:
        return [
            {
                "question": "Quiz generation failed",
                "options": [
                    "Try again",
                    "Check your API key",
                    "Use a shorter topic",
                    "Check the server logs",
                ],
                "answer": "Try again",
                "error": str(exc),
            }
        ]
