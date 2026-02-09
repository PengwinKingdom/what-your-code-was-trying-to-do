import os
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.prompts import PROMPT_TEMPLATE
from app.gemini_client import call_gemini
from app.fallback_analyzer import fallback_analyze
from fastapi.exceptions import HTTPException as FastAPIHTTPException


app=FastAPI(title="What Your Code Was Trying to Do")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("UNHANDLED ERROR:", repr(exc))
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": exc.__class__.__name__}
    )
    

class AnalyzeRequest(BaseModel):
    code:str
    language:str|None=None

@app.get("/")
def root():
    return {"ok":True,"message":"The API is running"}

@app.post("/analyze")
def analyze(req:AnalyzeRequest):
    #lines=req.code.splitlines()
    if len(req.code.splitlines())>150:
        raise HTTPException(status_code=400,detail="Code exceeds 150 lines limit")
    
    prompt = PROMPT_TEMPLATE.replace("<<LANG>>", req.language or "unknown") \
                        .replace("<<CODE>>", req.code)

    
    try:
        result=call_gemini(prompt)
        result["ai_used"] = True
        return result
    
    except Exception as e:
        msg=str(e)
        
        quota_error = "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower()
        if quota_error:
            return fallback_analyze(req.code,req.language)
        
        raise HTTPException(status_code=500,detail=msg)
 
 
 