# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational assistant based on the supplied project
documentation. It provides:

- Question & Answer
- Concept explanation
- Quiz generation with 4 options per question
- Text summarization
- Personalized learning paths

## Architecture

```text
Browser
  |
  | HTTP POST
  v
FastAPI (main.py)
  |
  +--> qna.py --------------------+
  +--> summary_module.py ---------|
  +--> quiz_module.py ------------|--> Gemini API
  +--> learning_path.py ----------+
  |
  +--> explanation_module.py --> Gemini by default
                              \-> optional local LaMini-Flan-T5-783M
```

## Important model note

The supplied document names Gemini 1.5 Pro and LaMini-Flan-T5-783M.

Gemini model availability changes over time, so the application does not hard-code
the historical model name. Set `GEMINI_MODEL` in `.env` to a model available to
your Gemini API account.

The LaMini model is optional and lazy-loaded. The original model is large, so
`ENABLE_LOCAL_EXPLAIN=false` is the easiest setup. Set it to `true` only if you
want the local explanation path and have installed the optional ML dependencies.

## 1. Prerequisites

Install:

- Python 3.10 or newer
- VS Code
- A Gemini API key

## 2. Open the project

Extract the ZIP and open the `EduGenie` folder in VS Code.

## 3. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

```cmd
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and replace:

```env
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
```

Do not commit `.env` to GitHub.

## 6. Start the application

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 7. Test the application

### Browser

Try:

1. Ask a Question
2. Explain a Concept
3. Generate Quiz
4. Summarize Text
5. Recommend Learning Path

### Health check

Open:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","service":"EduGenie"}
```

### PowerShell API test

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/qa `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"text":"What is the largest ocean?"}'
```

Quiz:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/quiz `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"topic":"Pythagoras theorem","count":3}'
```

## Optional: enable the local LaMini explanation model

The project documentation specifies LaMini-Flan-T5-783M for explanations.

Install the optional dependencies:

```bash
pip install torch transformers
```

Then edit `.env`:

```env
ENABLE_LOCAL_EXPLAIN=true
LOCAL_EXPLAIN_MODEL=MBZUAI/LaMini-Flan-T5-783M
```

The first explanation request downloads the model from Hugging Face and may
take a while. The original model is large, so this mode requires substantially
more disk space and memory than the default Gemini explanation path.

If local model loading fails, the code attempts to fall back to Gemini.

## Project structure

```text
EduGenie/
├── main.py
├── gemini_client.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web interface |
| GET | `/health` | Health check |
| POST | `/qa` | Question answering |
| POST | `/explain` | Concept explanation |
| POST | `/quiz` | Quiz generation |
| POST | `/summarize` | Summarization |
| POST | `/learn/recommendations` | Learning path |

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains a valid key.

### Gemini model error

Change `GEMINI_MODEL` in `.env` to a model currently available to your
Gemini API account.

### Port 8000 is already in use

Run:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

### PowerShell execution policy

If activation is blocked, use Command Prompt instead, or activate the
environment with the appropriate execution-policy setting for your machine.

## Security

Never put your Gemini API key in frontend JavaScript. This project keeps the
key on the FastAPI server.

Do not commit `.env` to GitHub.
