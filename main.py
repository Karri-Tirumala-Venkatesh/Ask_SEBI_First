from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List
import os
import google.generativeai as genai
import re
import json
import asyncio

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
auth_scheme = HTTPBearer()

INTERNAL_API_KEY = "d3ac456931faffea79a7c00f08a3e190998e84d9925709bb117e750078149d05"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

class RequestBody(BaseModel):
    documents: HttpUrl
    questions: List[str]

class ResponseBody(BaseModel):
    answers: List[str]

def verify_token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if creds.scheme.lower() != "bearer" or creds.credentials != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True

# Compile regex pattern once
JSON_PATTERN = re.compile(r'\{[\s\S]*\}')

@app.post("/hackrx/run", response_model=ResponseBody)
async def hackrx_run(body: RequestBody, authorized: bool = Depends(verify_token)):
    prompt = f"""Reference: {body.documents}
Answer the following questions in one detailed sentence each, in the exact JSON format:
{{"answers": ["answer1", "answer2"]}}
Questions:
""" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(body.questions)) + "\nReturn only the JSON object."
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        match = JSON_PATTERN.search(response.text)
        if not match:
            raise ValueError("No JSON object found in Gemini response")
        answers_json = json.loads(match.group())
        return ResponseBody(**answers_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")
