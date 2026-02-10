from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from vision_analyzer import analyze_image
from schemas import AnalysisResponse, ComplaintStatus
import os
from datetime import datetime
from typing import List, Optional
import json

# Create FastAPI app
app = FastAPI(
    title="Civic Issue Reporter API",
    description="AI-powered civic infrastructure issue detection",
    version="1.0.0"
)

# Configure CORS - CRITICAL FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory complaint storage (replace with database in production)
complaints_db = []


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Civic Issue Reporter API is running",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_civic_issue(
    file: UploadFile = File(..., description="Image file to analyze"),
    location: str = Form(..., description="Location where the image was taken")
):
    """
    Analyze an uploaded image for civic infrastructure issues
    
    Args:
        file: Image file (JPG, PNG, etc.)
        location: Geographic location of the issue
        
    Returns:
        AnalysisResponse with detected issues and assigned authorities
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate image size (optional, but recommended)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 10MB"
            )
        
        # Analyze the image
        result = analyze_image(image_bytes, location)
        
        # Check if there was an error in analysis
        if "error" in result:
            # Still return the result but log the error
            print(f"Analysis completed with error: {result['error']}")
        
        # Store complaint in database
        complaint_record = {
            "complaint_id": result["complaint_id"],
            "issue_detected": result["issue_detected"],
            "civic_issues": result["civic_issues"],
            "severity": result["severity"],
            "severity_score": result["severity_score"],
            "assigned_authorities": result["assigned_authorities"],
            "location": location,
            "status": "Pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "detections": [d.dict() for d in result["detections"]]
        }
        complaints_db.append(complaint_record)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_civic_issue endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
    }


# ============= ADMIN ENDPOINTS =============

@app.get("/admin/complaints")
async def get_all_complaints(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, le=500, description="Maximum number of results")
):
    """
    Get all complaints with optional filters
    
    Query Parameters:
    - status: Filter by status (Pending, In Progress, Resolved)
    - severity: Filter by severity (Low, Medium, High)
    - limit: Maximum number of results
    """
    filtered_complaints = complaints_db.copy()
    
    # Apply filters
    if status:
        filtered_complaints = [c for c in filtered_complaints if c["status"] == status]
    
    if severity:
        filtered_complaints = [c for c in filtered_complaints if c["severity"] == severity]
    
    # Sort by created_at (newest first)
    filtered_complaints.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    filtered_complaints = filtered_complaints[:limit]
    
    return {
        "total": len(filtered_complaints),
        "complaints": filtered_complaints
    }


@app.get("/admin/complaints/{complaint_id}")
async def get_complaint_by_id(complaint_id: str):
    """Get a specific complaint by ID"""
    complaint = next((c for c in complaints_db if c["complaint_id"] == complaint_id), None)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@app.put("/admin/complaints/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    status: str = Query(..., description="New status: Pending, In Progress, Resolved")
):
    """Update the status of a complaint"""
    if status not in ["Pending", "In Progress", "Resolved"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: Pending, In Progress, or Resolved"
        )
    
    complaint = next((c for c in complaints_db if c["complaint_id"] == complaint_id), None)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint["status"] = status
    complaint["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": "Status updated successfully",
        "complaint_id": complaint_id,
        "new_status": status,
        "updated_at": complaint["updated_at"]
    }


@app.delete("/admin/complaints/{complaint_id}")
async def delete_complaint(complaint_id: str):
    """Delete a complaint (admin only)"""
    global complaints_db
    
    initial_length = len(complaints_db)
    complaints_db = [c for c in complaints_db if c["complaint_id"] != complaint_id]
    
    if len(complaints_db) == initial_length:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return {
        "message": "Complaint deleted successfully",
        "complaint_id": complaint_id
    }


@app.get("/admin/statistics")
async def get_statistics():
    """Get dashboard statistics"""
    total = len(complaints_db)
    pending = len([c for c in complaints_db if c["status"] == "Pending"])
    in_progress = len([c for c in complaints_db if c["status"] == "In Progress"])
    resolved = len([c for c in complaints_db if c["status"] == "Resolved"])
    
    # Count by severity
    high_severity = len([c for c in complaints_db if c["severity"] == "High"])
    medium_severity = len([c for c in complaints_db if c["severity"] == "Medium"])
    low_severity = len([c for c in complaints_db if c["severity"] == "Low"])
    
    # Count by issue type
    issue_counts = {}
    for complaint in complaints_db:
        for issue in complaint["civic_issues"]:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    
    # Resolution rate
    resolution_rate = (resolved / total * 100) if total > 0 else 0
    
    return {
        "total_complaints": total,
        "by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved
        },
        "by_severity": {
            "high": high_severity,
            "medium": medium_severity,
            "low": low_severity
        },
        "by_issue_type": issue_counts,
        "resolution_rate": round(resolution_rate, 2),
        "average_severity_score": round(
            sum(c["severity_score"] for c in complaints_db) / total, 2
        ) if total > 0 else 0
    }


@app.get("/admin/export")
async def export_complaints():
    """Export all complaints as JSON"""
    return {
        "export_date": datetime.utcnow().isoformat(),
        "total_complaints": len(complaints_db),
        "complaints": complaints_db
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
