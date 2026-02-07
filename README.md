# CivicSense AI

## Overview
CivicSense is a vision-based system that detects civic infrastructure issues from user-uploaded images using a Vision API.

## Architecture
- Frontend: Image upload and result visualization
- Backend: API and validation
- Vision Layer: Prompt-driven multimodal reasoning

## API Contract
POST /analyze  
Response:
{
  "issue_detected": boolean,
  "issue_type": string,
  "severity": "Low | Medium | High",
  "confidence": number,
  "explanation": string
}

## Team Roles
- LLM Engineer: Vision reasoning and prompt design
- Backend: API and server logic
- Frontend: UI and visualization
