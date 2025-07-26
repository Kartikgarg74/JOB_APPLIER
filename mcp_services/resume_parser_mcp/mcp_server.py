from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.database.config import SessionLocal
from packages.agents.agent_manager import AgentManager

app = FastAPI(
    title="Resume Parser MCP Service",
    description="Monetized resume parsing service for extracting structured data from resumes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pricing configuration
PRICING_TIERS = {
    "basic": {"price": 15.00, "resumes_per_month": 50},
    "professional": {"price": 25.00, "resumes_per_month": 200},
    "enterprise": {"price": 40.00, "resumes_per_month": -1}  # -1 means unlimited
}

class ResumeParseResponse(BaseModel):
    personal_info: Dict[str, Any]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    summary: str
    contact_info: Dict[str, Any]
    cost: float
    request_id: str
    timestamp: datetime

class ResumeTextRequest(BaseModel):
    resume_text: str
    api_key: str
    tier: str = "basic"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(api_key: str) -> str:
    """
    Verify API key and return user ID.
    In production, this would check against a database.
    """
    if not api_key or len(api_key) < 10:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return f"user_{api_key[:8]}"

def charge_user(user_id: str, service: str, amount: float) -> bool:
    """
    Charge user for service usage.
    In production, this would integrate with Stripe.
    """
    logger.info(f"Charging user {user_id} ${amount} for {service}")
    return True

@app.post("/parse/file", response_model=ResumeParseResponse)
async def parse_resume_file(
    resume_file: UploadFile = File(...),
    api_key: str = Form(...),
    tier: str = Form("basic"),
    db = Depends(get_db)
):
    """
    Parse resume file and extract structured data.
    Supports PDF, DOCX, and TXT files.
    Cost: $15-40 depending on tier.
    """
    try:
        # Verify API key
        user_id = verify_api_key(api_key)

        # Determine pricing based on tier
        tier_config = PRICING_TIERS.get(tier, PRICING_TIERS["basic"])
        cost = tier_config["price"]

        # Charge user
        charge_user(user_id, "resume_parsing_file", cost)

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.filename.split('.')[-1]}") as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Initialize parser agent
            agent_manager = AgentManager(db)
            resume_parser = agent_manager.get_resume_parser_agent()

            # Parse resume file
            result = resume_parser.parse_resume_file(tmp_file_path)

            # Generate request ID
            request_id = f"parse_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"

            logger.info(f"Resume file parsing completed for user {user_id}")

            return ResumeParseResponse(
                personal_info=result.get("personal_info", {}),
                skills=result.get("skills", []),
                experience=result.get("experience", []),
                education=result.get("education", []),
                summary=result.get("summary", ""),
                contact_info=result.get("contact_info", {}),
                cost=cost,
                request_id=request_id,
                timestamp=datetime.now()
            )

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except Exception as e:
        logger.error(f"Error in resume file parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume file parsing failed: {str(e)}")

@app.post("/parse/text", response_model=ResumeParseResponse)
async def parse_resume_text(
    request: ResumeTextRequest,
    db = Depends(get_db)
):
    """
    Parse resume text and extract structured data.
    Cost: $15-40 depending on tier.
    """
    try:
        # Verify API key
        user_id = verify_api_key(request.api_key)

        # Determine pricing based on tier
        tier_config = PRICING_TIERS.get(request.tier, PRICING_TIERS["basic"])
        cost = tier_config["price"]

        # Charge user
        charge_user(user_id, "resume_parsing_text", cost)

        # Initialize parser agent
        agent_manager = AgentManager(db)
        resume_parser = agent_manager.get_resume_parser_agent()

        # Parse resume text
        result = resume_parser.parse_resume(request.resume_text)

        # Generate request ID
        request_id = f"parse_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"

        logger.info(f"Resume text parsing completed for user {user_id}")

        return ResumeParseResponse(
            personal_info=result.get("personal_info", {}),
            skills=result.get("skills", []),
            experience=result.get("experience", []),
            education=result.get("education", []),
            summary=result.get("summary", ""),
            contact_info=result.get("contact_info", {}),
            cost=cost,
            request_id=request_id,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error in resume text parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume text parsing failed: {str(e)}")

@app.get("/pricing")
async def get_pricing():
    """
    Get pricing information for different tiers.
    """
    return {
        "tiers": PRICING_TIERS,
        "currency": "USD",
        "billing_cycle": "monthly"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "Resume Parser MCP", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
