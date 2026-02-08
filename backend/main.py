from fastapi import FastAPI, UploadFile, Form
from vision_analyzer import analyze_image
import uuid

app = FastAPI()

@app.post("/detect")
async def detect_issue(
    image: UploadFile,
    location: str = Form(...)
):
    image_bytes = await image.read()

    ai_result = analyze_image(image_bytes)

    complaint_id = f"CIV-{uuid.uuid4().hex[:6]}"

    return {
        "complaint_id": complaint_id,
        "location": location,
        "analysis": ai_result
    }
