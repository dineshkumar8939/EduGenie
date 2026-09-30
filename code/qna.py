from gemini_client import generate_text, GeminiError


def answer_question(question: str) -> str:
    prompt = f"""
You are EduGenie, a careful educational assistant.

Answer the student's question below accurately and concisely.
- Use simple language.
- If the question is ambiguous, state the assumption you are making.
- Do not invent facts.
- For calculations, show the important steps.
- Keep the response useful for a student.

Student question:
{question}
"""
    try:
        return generate_text(prompt, temperature=0.25, max_output_tokens=900)
    except GeminiError as exc:
        return f"Unable to answer right now. {exc}"
