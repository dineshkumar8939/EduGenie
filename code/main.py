from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

load_dotenv()

app = FastAPI(
    title="EduGenie",
    description="Google Gemini powered learning assistant",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=30000)


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=10000)
    count: int = Field(default=3, ge=1, le=10)


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=5000)
    level: str = Field(default="Beginner", max_length=50)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "EduGenie"}


@app.post("/qa")
async def qa(payload: TextRequest):
    return {"result": answer_question(payload.text)}


@app.post("/explain")
async def explain(payload: TextRequest):
    return {"result": explain_concept(payload.text)}


@app.post("/quiz")
async def quiz(payload: QuizRequest):
    return {"quiz": generate_quiz(payload.topic, payload.count)}


@app.post("/summarize")
async def summarize(payload: TextRequest):
    return {"result": summarize_text(payload.text)}


@app.post("/learn/recommendations")
async def recommendations(payload: LearningPathRequest):
    return {
        "result": get_learning_recommendations(
            payload.topic, payload.level
        )
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
