from fastapi import FastAPI, UploadFile, Form
import requests
import uuid
import os

app = FastAPI()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

@app.get("/")
def root():
    return {"status": "Civic Sense backend running"}

def analyze_image_hf(image_bytes: bytes):
    response = requests.post(
        HF_MODEL_URL,
        headers=headers,
        data=image_bytes
    )

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()

@app.post("/detect")
async def detect_issue(
    image: UploadFile,
    location: str = Form(...)
):
    image_bytes = await image.read()

    ai_result = analyze_image_hf(image_bytes)

    complaint_id = f"CIV-{uuid.uuid4().hex[:6]}"

    return {
        "complaint_id": complaint_id,
        "location": location,
        "analysis": ai_result
    }
