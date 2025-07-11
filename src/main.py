from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.medicalAgent import ask
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/medicalAssistant")
async def ask_question(request: QuestionRequest):
    try:
        result = await ask(request.question)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
