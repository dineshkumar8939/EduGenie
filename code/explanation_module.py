import os
from functools import lru_cache

from gemini_client import generate_text, GeminiError


@lru_cache(maxsize=1)
def _load_local_model():
    """
    Loads LaMini-Flan-T5-783M only when ENABLE_LOCAL_EXPLAIN=true.

    The model is several GB in its original PyTorch form, so it is deliberately
    lazy-loaded instead of being loaded during FastAPI startup.
    """
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    model_name = os.getenv(
        "LOCAL_EXPLAIN_MODEL",
        "MBZUAI/LaMini-Flan-T5-783M",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


def _local_explanation(topic: str) -> str:
    tokenizer, model = _load_local_model()

    prompt = (
        "Explain the following topic to a beginner in simple language. "
        "Use a short definition, an analogy, and one example.\n\n"
        f"Topic: {topic}"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    output = model.generate(
        **inputs,
        max_new_tokens=180,
        num_beams=4,
        early_stopping=True,
    )

    return tokenizer.decode(output[0], skip_special_tokens=True).strip()


def explain_concept(topic: str) -> str:
    use_local = os.getenv("ENABLE_LOCAL_EXPLAIN", "false").lower() == "true"

    if use_local:
        try:
            return _local_explanation(topic)
        except Exception as exc:
            # Falling back to Gemini makes the application usable if the local
            # model is not installed, cannot fit in memory, or fails to load.
            fallback_note = (
                "The optional local LaMini model was unavailable, "
                "so EduGenie used the cloud model instead."
            )
            try:
                result = generate_text(
                    f"""
Explain this topic to a beginner: {topic}

Structure:
1. Simple definition
2. How it works
3. Easy analogy
4. Example
5. Key takeaway
""",
                    temperature=0.35,
                    max_output_tokens=900,
                )
                return f"{result}\n\n_{fallback_note}_"
            except GeminiError:
                return f"Unable to generate an explanation. Local model error: {exc}"

    try:
        return generate_text(
            f"""
Explain the following concept to a beginner.

Topic: {topic}

Use this structure:
1. Simple definition
2. How it works
3. Easy analogy
4. Example
5. Key takeaway

Avoid unnecessary jargon.
""",
            temperature=0.35,
            max_output_tokens=900,
        )
    except GeminiError as exc:
        return f"Unable to explain the topic right now. {exc}"
