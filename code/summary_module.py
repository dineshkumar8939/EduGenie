from gemini_client import generate_text, GeminiError


def summarize_text(text: str) -> str:
    prompt = f"""
Summarize the educational text below for quick revision.

Requirements:
- Preserve the important facts and relationships.
- Remove repetition and filler.
- Use simple language.
- Return a short heading followed by concise bullet points.
- Do not add information that is not present in the source.

Text:
{text}
"""
    try:
        return generate_text(
            prompt,
            temperature=0.25,
            max_output_tokens=1200,
        )
    except GeminiError as exc:
        return f"Unable to summarize right now. {exc}"
