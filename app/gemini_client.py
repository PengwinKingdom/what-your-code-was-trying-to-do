import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

def call_gemini(prompt:str,model:str="gemini-2.0-flash") -> dict:
    api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise RuntimeError("Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in your environment variables.")
    
    client=genai.Client(api_key=api_key)
    
    resp=client.model.generate_content(
        model=model,
        contents=prompt
    )
    
    text=(resp.text or "").strip()
    if not text:
        raise RuntimeError("No response from Gemini API")
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start=text.find("{")
        end=text.rfind("}")
        if start!=-1 and end!=-1 and end>start:
            return json.loads(text[start:end+1])
        raise

