# =========================
# Imports
# =========================
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List
import os
import google.generativeai as genai
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredURLLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import tempfile
import httpx
import re

# =========================
# Environment Setup
# =========================
load_dotenv()

# =========================
# FastAPI App Initialization
# =========================
app = FastAPI()
auth_scheme = HTTPBearer()

# =========================
# API Keys and Model Setup
# =========================
INTERNAL_API_KEY = "d3ac456931faffea79a7c00f08a3e190998e84d9925709bb117e750078149d05"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# =========================
# Request Body Schema
# =========================
class RequestBody(BaseModel):
    documents: HttpUrl
    questions: List[str]

# =========================
# Authentication Dependency
# =========================
def verify_token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Verifies the Bearer token for API access.
    """
    if creds.scheme.lower() != "bearer" or creds.credentials != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True

# Instantiate embedding model once
embedding_fn = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

MAX_RECURSION_DEPTH = 2  # Prevent infinite loops

def extract_urls(text):
    url_pattern = r'https?://[^\s)]+'
    return re.findall(url_pattern, text)

async def fetch_and_extract(url, client):
    try:
        data = await load_document_from_url(url, client)
        return "\n".join([doc.page_content for doc in data])
    except Exception:
        pass
    return ""

async def load_document_from_url(url, client):
    """
    Determines content type, downloads, and loads the document using the correct loader.
    Returns a list of loaded documents.
    """
    try:
        head_resp = await client.head(url, follow_redirects=True)
        content_type = head_resp.headers.get('content-type', '').lower()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch headers: {str(e)}")

    if 'application/pdf' in content_type:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to download PDF file.")
            tmp.write(response.content)
            tmp_path = tmp.name
        try:
            loader = UnstructuredPDFLoader(tmp_path)
            data = await asyncio.to_thread(loader.load)
        finally:
            os.remove(tmp_path)
    elif (
        'application/msword' in content_type or
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or
        'wordprocessingml.document' in content_type
    ):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to download Word file.")
            tmp.write(response.content)
            tmp_path = tmp.name
        try:
            loader = UnstructuredWordDocumentLoader(tmp_path)
            data = await asyncio.to_thread(loader.load)
        finally:
            os.remove(tmp_path)
    elif content_type.startswith("text/html"):
        loader = UnstructuredURLLoader(urls=[url])
        data = await asyncio.to_thread(loader.load)
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type.")

    if not data:
        raise HTTPException(status_code=404, detail="No data found at the provided URL.")
    return data

ACTION_MARKER = "REQUIRES_EXTERNAL_ACTION:"

async def process_question_recursive(question, vectorstore, client, recursion_depth=0):
    try:
        docs_and_scores = await asyncio.to_thread(vectorstore.similarity_search_with_score, question, 3)
        if not docs_and_scores or not docs_and_scores[0]:
            return "No relevant context found for this question."
        relevant_chunks = "\n\n".join([doc.page_content for doc, _ in docs_and_scores if doc])
    except Exception as e:
        return f"Error during similarity search: {str(e)}"

    prompt = (
        f"Use the following context to answer the question in 1 detailed sentence. "
        f"If the answer is not present or requires following a link or external reference, "
        f"reply exactly with '{ACTION_MARKER} <action or URL or instruction>'.\n\n"
        f"Context:\n{relevant_chunks}\n\n"
        f"Question: {question}\nAnswer:"
    )
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        answer = (response.text or "").strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"

    # If LLM says external action is required, extract and recurse
    if recursion_depth < MAX_RECURSION_DEPTH and answer.startswith(ACTION_MARKER):
        action_text = answer[len(ACTION_MARKER):].strip()
        urls = extract_urls(action_text)
        if urls:
            fetched_content = await fetch_and_extract(urls[0], client)
            if fetched_content:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
                docs = text_splitter.split_documents([type('Doc', (), {'page_content': fetched_content})()])
                doc_texts = [doc.page_content for doc in docs]
                try:
                    new_vectorstore = await asyncio.to_thread(FAISS.from_texts, doc_texts, embedding_fn)
                except Exception as e:
                    return f"Failed to create vector store for referenced content: {str(e)}"
                return await process_question_recursive(question, new_vectorstore, client, recursion_depth + 1)
        return f"External action required but no valid URL found: {action_text}"

    return answer

# =========================
# Main Endpoint
# =========================
@app.post("/hackrx/run")
async def hackrx_run(body: RequestBody, authorized: bool = Depends(verify_token)):
    """
    Answers user questions based on the content of a web document or file.
    Recursively follows LLM instructions to fetch referenced content if needed.
    """

    try:
        url = str(body.documents)
        async with httpx.AsyncClient() as client:
            data = await load_document_from_url(url, client)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
            docs = text_splitter.split_documents(data)
            if not docs:
                raise HTTPException(status_code=404, detail="Document could not be split into chunks.")

            doc_texts = [doc.page_content for doc in docs]

            try:
                vectorstore = await asyncio.to_thread(FAISS.from_texts, doc_texts, embedding_fn)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create vector store: {str(e)}")

            answers = await asyncio.gather(
                *(process_question_recursive(q, vectorstore, client) for q in body.questions)
            )
            return {"answers": answers}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
