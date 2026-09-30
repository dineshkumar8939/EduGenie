from gemini_client import generate_text, GeminiError


def get_learning_recommendations(
    topic: str,
    level: str = "Beginner",
) -> str:
    prompt = f"""
Create a personalized learning path for the topic "{topic}".
The learner currently describes their level as "{level}".

Organize the response from beginner to advanced.

For each stage include:
- Concepts to learn
- What the learner should be able to do
- A small practice task or project

Also provide useful resource TYPES to look for, such as official
documentation, books, courses, or videos. Do not invent exact URLs.

Keep the plan practical and progressive.
"""
    try:
        return generate_text(
            prompt,
            temperature=0.4,
            max_output_tokens=1800,
        )
    except GeminiError as exc:
        return f"Unable to create a learning path right now. {exc}"
