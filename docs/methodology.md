
- **Frontend**: Collects image and location; sends to backend via HTTP POST  
- **Backend API**: Handles uploads, calls AI model, validates results, returns JSON  
- **Vision Analyzer**: Either a Vision API (GPT-4.1/4o Vision) or YOLO object detection  
- **Dashboard/Storage**: Tracks complaints, severity, and authorities  

---

## 3. Method (Step-by-Step)

1. **Image Upload**
   - Users select an image from their device
   - Location can be entered manually or auto-detected

2. **Backend Submission**
   - Frontend sends image + location via POST `/analyze`

3. **AI Analysis**
   - **Vision API** approach:
     - Sends image + prompt to Vision LLM  
     - Receives structured JSON with issue type, severity, explanation, confidence
   - **YOLO approach (optional)**:
     - Detects bounding boxes of known civic issues  
     - Calculates severity heuristically based on box area

4. **Validation**
   - Structured output is verified:
     - JSON-only format
     - Enum values for issue types
     - Confidence threshold (e.g., > 0.6)
   - Low-confidence outputs flagged as “uncertain”

5. **Response**
   - Backend returns validated JSON
   - Frontend displays:
     - Issue type
     - Location
     - Authority
     - Severity
     - Complaint ID

6. **Dashboard (Optional)**
   - Stores complaints for authority tracking
   - Aggregates issues by type/severity
   - Displays status: Open, In Progress, Resolved

---

## 4. Safety & Reliability
- Vision model treated as **signal generator**, not decision-maker
- Schema validation ensures output consistency
- Confidence thresholds reduce false positives
- Human review can be added for critical issues

---

## 5. Advantages
- No large dataset required for Vision API
- Modular design allows swapping AI methods (Vision API ↔ YOLO)
- Structured, explainable results ready for authorities
- Frontend remains lightweight and intuitive
