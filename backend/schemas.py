# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional


class Detection(BaseModel):
    """Schema for individual issue detection"""
    label: str = Field(..., description="Type of civic issue detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class AnalysisRequest(BaseModel):
    """Schema for image analysis request"""
    location: str = Field(..., description="Location where the image was taken")
    image: Optional[str] = Field(None, description="Base64 encoded image string")


class AnalysisResponse(BaseModel):
    """Schema for image analysis response"""
    complaint_id: str = Field(..., description="Unique complaint identifier")
    issue_detected: bool = Field(..., description="Whether any issues were detected")
    civic_issues: List[str] = Field(default_factory=list, description="List of detected civic issues")
    severity: str = Field(..., description="Overall severity level: Low, Medium, High")
    severity_score: int = Field(..., ge=1, le=10, description="Numerical severity score from 1-10")
    assigned_authorities: List[str] = Field(..., description="List of responsible authorities")
    location: str = Field(..., description="Location of the issue")
    detections: List[Detection] = Field(default_factory=list, description="Detailed detection results")


class ComplaintStatus(BaseModel):
    """Schema for complaint status"""
    complaint_id: str
    status: str = Field(..., description="Status: Pending, In Progress, Resolved")
    created_at: str
    updated_at: Optional[str] = None