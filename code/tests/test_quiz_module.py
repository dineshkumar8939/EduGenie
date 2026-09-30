from quiz_module import clean_json_block


def test_clean_json_block():
    raw = """```json
[
  {
    "question": "2 + 2?",
    "options": ["1", "2", "3", "4"],
    "answer": "4"
  }
]
```"""
    cleaned = clean_json_block(raw)
    assert cleaned.startswith("[")
    assert cleaned.endswith("]")
