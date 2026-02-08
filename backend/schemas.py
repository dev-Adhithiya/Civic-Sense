from pydantic import BaseModel
from typing import Literal

class CivicIssueResult(BaseModel):
    issue_detected: bool
    issue_type: Literal[
        "Pothole",
        "Broken Road",
        "Garbage Overflow",
        "Streetlight Issue",
        "Water Leakage",
        "None"
    ]
    severity: Literal["Low", "Medium", "High"]
    confidence: float
    explanation: str
    location: str
