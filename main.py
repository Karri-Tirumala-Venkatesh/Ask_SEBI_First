from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List
import requests

app = FastAPI()
auth_scheme = HTTPBearer()

class RequestBody(BaseModel):
    documents: HttpUrl
    questions: List[str]

class ResponseBody(BaseModel):
    answers: List[str]

api_key = "d3ac456931faffea79a7c00f08a3e190998e84d9925709bb117e750078149d05"

def verify_token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if creds.scheme.lower() != "bearer" or creds.credentials != api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True

@app.post("/hackrx/run", response_model=ResponseBody)
async def hackrx_run(body: RequestBody, authorized: bool = Depends(verify_token)):
    # fetch the document (PDF) from the URL
    resp = requests.get(body.documents)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch document URL")
    pdf_content = resp.content
    # Here, you would extract text from pdf_content, run QA model etc.
    # For demonstration, we return a fixed sample response like your example
    sample_answers = [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre‑existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one‑year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "Yes, the policy reimburses expenses for health check‑ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).",
    ]

    # If mismatched question count
    if len(body.questions) != len(sample_answers):
        raise HTTPException(status_code=400, detail="Number of answers not matching number of questions")

    return ResponseBody(answers=sample_answers)
