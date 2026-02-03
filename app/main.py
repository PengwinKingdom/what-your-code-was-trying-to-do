from fastapi import FastAPI
from pydantic import BaseModel
from app.prompts import PROMPT_TEMPLATE
from app.gemini_client import call_gemini

app=FastAPI(title="What Your Code Was Trying to Do")

class AnalyzeRequest(BaseModel):
    code:str
    language:str|None=None

@app.get("/")
def root():
    return {"ok":True,"message":"The API is running"}

@app.post("/analyze")
def analyze(req:AnalyzeRequest):
    lines=req.code.splitlines()
    if len(lines)>150:
        raise HTTPException(status_code=400,detail="Code exceeds 150 lines limit")
    
    prompt=PROMPT_TEMPLATE.format(
        language=req.language or "unknown",
        code=req.code
    )
    
    try:
        result=call_gemini(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    