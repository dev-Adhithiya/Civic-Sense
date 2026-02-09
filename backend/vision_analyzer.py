import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables first
load_dotenv()

# Check if API key exists before importing
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file! Please add it.")

# Now import google generativeai
try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

from schemas import Detection

# Configure with API key
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    raise


def generate_complaint_id():
    return f"CIVIC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def assign_authority(issue_type: str):
    authority_map = {
        "Pothole": "Public Works Department",
        "Garbage Overflow": "Sanitation Department",
        "Water Leakage": "Water Board",
        "Open Drain": "Public Works Department",
        "Streetlight Issue": "Electrical Department"
    }
    return authority_map.get(issue_type, "Municipal Corporation")


def calculate_severity(issue_type: str, description: str):
    """Calculate severity (1-10) based on issue type and description"""
    desc_lower = description.lower()
    
    if issue_type == "Pothole":
        if any(word in desc_lower for word in ["large", "deep", "major", "severe", "dangerous"]):
            return 8
        elif any(word in desc_lower for word in ["medium", "moderate"]):
            return 5
        else:
            return 3
    
    elif issue_type == "Garbage Overflow":
        if any(word in desc_lower for word in ["huge", "massive", "pile", "accumulated", "overflow"]):
            return 7
        elif any(word in desc_lower for word in ["scattered", "moderate"]):
            return 5
        else:
            return 3
    
    elif issue_type == "Water Leakage":
        if any(word in desc_lower for word in ["burst", "flooding", "major", "gushing"]):
            return 9
        elif any(word in desc_lower for word in ["leak", "flowing"]):
            return 6
        else:
            return 4
    
    elif issue_type == "Open Drain":
        if any(word in desc_lower for word in ["large", "uncovered", "dangerous", "open"]):
            return 8
        else:
            return 5
    
    elif issue_type == "Streetlight Issue":
        if any(word in desc_lower for word in ["broken", "damaged", "hanging"]):
            return 6
        else:
            return 3
    
    return 5


def analyze_image(image_bytes: bytes, location: str):
    """Analyze image for civic issues using Gemini Vision API"""
    
    try:
        print(f"Analyzing image for location: {location}")
        print(f"Image size: {len(image_bytes)} bytes")
        
        prompt = """
        Analyze this image and identify civic infrastructure issues. Detect:
        1. Potholes (road damage, cracks, holes)
        2. Garbage Overflow (litter, trash, waste)
        3. Water Leakage (pipe burst, flooding, seepage)
        4. Open Drain (uncovered drains, sewage)
        5. Streetlight Issue (broken lights, damaged poles)
        
        For each issue found, describe its severity (small/medium/large/severe).
        
        Respond in JSON format:
        {
            "issues": [
                {
                    "type": "Pothole|Garbage Overflow|Water Leakage|Open Drain|Streetlight Issue",
                    "description": "detailed description with size/severity indicators",
                    "confidence": 0.0-1.0
                }
            ]
        }
        
        If no issues found, return: {"issues": []}
        """

        # Generate content with error handling
        try:
            response = model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    }
                ]
            )
            
            print(f"Gemini API Response received")
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Return default response if API fails
            return {
                "complaint_id": generate_complaint_id(),
                "issue_detected": False,
                "civic_issues": [],
                "severity": "Low",
                "severity_score": 1,
                "assigned_authorities": ["Municipal Corporation"],
                "location": location,
                "detections": [],
                "error": f"API Error: {str(e)}"
            }

        text_output = response.text or ""
        print(f"Response text: {text_output[:200]}...")  # Print first 200 chars
        
        # Parse JSON from response
        try:
            if "```json" in text_output:
                json_text = text_output.split("```json")[1].split("```")[0].strip()
            elif "```" in text_output:
                json_text = text_output.split("```")[1].split("```")[0].strip()
            else:
                json_text = text_output.strip()
            
            data = json.loads(json_text)
            issues_data = data.get("issues", [])
            print(f"Parsed {len(issues_data)} issues from response")
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw response: {text_output}")
            issues_data = []
        
        # Process detected issues
        detections = []
        civic_issues = []
        authorities = set()
        max_severity = 0
        
        for issue in issues_data:
            issue_type = issue.get("type", "")
            description = issue.get("description", "")
            confidence = issue.get("confidence", 0.85)
            
            if issue_type:
                civic_issues.append(issue_type)
                severity_score = calculate_severity(issue_type, description)
                max_severity = max(max_severity, severity_score)
                
                detections.append(Detection(
                    label=issue_type,
                    confidence=confidence
                ))
                
                authorities.add(assign_authority(issue_type))
        
        # Determine overall severity level
        if max_severity >= 8:
            severity_level = "High"
        elif max_severity >= 5:
            severity_level = "Medium"
        else:
            severity_level = "Low"
        
        # Default severity if no issues
        if max_severity == 0:
            max_severity = 1
            severity_level = "Low"
        
        result = {
            "complaint_id": generate_complaint_id(),
            "issue_detected": len(civic_issues) > 0,
            "civic_issues": civic_issues,
            "severity": severity_level,
            "severity_score": max_severity,
            "assigned_authorities": list(authorities) if authorities else ["Municipal Corporation"],
            "location": location,
            "detections": detections
        }
        
        print(f"Analysis complete: {result['complaint_id']}")
        return result
        
    except Exception as e:
        print(f"Unexpected error in analyze_image: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            "complaint_id": generate_complaint_id(),
            "issue_detected": False,
            "civic_issues": [],
            "severity": "Low",
            "severity_score": 1,
            "assigned_authorities": ["Municipal Corporation"],
            "location": location,
            "detections": [],
            "error": str(e)
        }
