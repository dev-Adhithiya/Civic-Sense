import base64
from openai import OpenAI
from schemas import CivicIssueResult

client = OpenAI()

SYSTEM_PROMPT = """
You are an AI system designed to detect civic infrastructure issues from images.

Tasks:
1. Determine if a civic issue is present.
2. Classify the issue type from a fixed list.
3. Estimate severity based on public safety risk.
4. Provide concise visual reasoning.

Severity Guidelines:
- Low: Minor issue, no immediate risk.
- Medium: Noticeable issue, possible hazard.
- High: Severe issue, immediate safety risk.

Rules:
- Respond ONLY in valid JSON.
- No extra text.
- If image is unclear or unrelated, set:
  issue_detected=false,
  issue_type="None",
  severity="Low",
  confidence < 0.4
"""

def analyze_image(image_bytes: bytes) -> CivicIssueResult:
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        }
                    }
                ]
            }
        ],
        temperature=0.2
    )

    return CivicIssueResult.model_validate_json(
        response.choices[0].message.content
    )
