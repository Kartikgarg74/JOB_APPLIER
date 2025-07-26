from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.database.config import SessionLocal
from packages.agents.agent_manager import AgentManager

# Import monetization modules (to be created)
# from monetization.billing.stripe_integration import StripeBilling
# from monetization.auth.api_key_manager import APIKeyManager

app = FastAPI(
    title="ATS Scoring MCP Service",
    description="Monetized ATS (Applicant Tracking System) scoring service for resume optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pricing configuration
PRICING_TIERS = {
    "basic": {"price": 25.00, "requests_per_month": 100},
    "professional": {"price": 50.00, "requests_per_month": 500},
    "enterprise": {"price": 100.00, "requests_per_month": -1}  # -1 means unlimited
}

class ATSScoreRequest(BaseModel):
    resume_text: str
    job_description: str
    industry: Optional[str] = None
    api_key: str
    tier: str = "basic"

class ATSScoreResponse(BaseModel):
    score: float
    recommendations: List[str]
    missing_keywords: List[str]
    success_probability: float
    cost: float
    request_id: str
    timestamp: datetime

class ResumeFileRequest(BaseModel):
    job_description: str
    industry: Optional[str] = None
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
    # TODO: Implement actual API key verification
    if not api_key or len(api_key) < 10:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return f"user_{api_key[:8]}"

def charge_user(user_id: str, service: str, amount: float) -> bool:
    """
    Charge user for service usage.
    In production, this would integrate with Stripe.
    """
    # TODO: Implement actual billing
    logger.info(f"Charging user {user_id} ${amount} for {service}")
    return True

@app.post("/score/text", response_model=ATSScoreResponse)
async def score_resume_text(
    request: ATSScoreRequest,
    db = Depends(get_db)
):
    """
    Score resume text against job description.
    Cost: $25-100 depending on tier.
    """
    try:
        # Verify API key
        user_id = verify_api_key(request.api_key)

        # Determine pricing based on tier
        tier_config = PRICING_TIERS.get(request.tier, PRICING_TIERS["basic"])
        cost = tier_config["price"]

        # Charge user
        charge_user(user_id, "ats_scoring", cost)

        # Initialize agents
        agent_manager = AgentManager(db)
        ats_scorer = agent_manager.get_ats_scorer_agent()
        resume_parser = agent_manager.get_resume_parser_agent()

        # Parse resume text
        parsed_resume = resume_parser.parse_resume(request.resume_text)

        # Score against job description
        result = ats_scorer.score_ats(parsed_resume, request.job_description, industry=request.industry)

        # Generate request ID
        request_id = f"ats_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"

        logger.info(f"ATS scoring completed for user {user_id}, score: {result.get('overall_ats_score', 0)}")

        return ATSScoreResponse(
            score=result.get("overall_ats_score", 0),
            recommendations=result.get("optimization_opportunities", []),
            missing_keywords=result.get("missing_keywords", []),
            success_probability=result.get("success_probability", 0),
            cost=cost,
            request_id=request_id,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error in ATS scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ATS scoring failed: {str(e)}")

@app.post("/score/file", response_model=ATSScoreResponse)
async def score_resume_file(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    industry: Optional[str] = Form(None),
    api_key: str = Form(...),
    tier: str = Form("basic"),
    db = Depends(get_db)
):
    """
    Score resume file against job description.
    Supports PDF, DOCX, and TXT files.
    Cost: $25-100 depending on tier.
    """
    try:
        # Verify API key
        user_id = verify_api_key(api_key)

        # Determine pricing based on tier
        tier_config = PRICING_TIERS.get(tier, PRICING_TIERS["basic"])
        cost = tier_config["price"]

        # Charge user
        charge_user(user_id, "ats_scoring_file", cost)

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.filename.split('.')[-1]}") as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Initialize agents
            agent_manager = AgentManager(db)
            ats_scorer = agent_manager.get_ats_scorer_agent()
            resume_parser = agent_manager.get_resume_parser_agent()

            # Parse resume file
            parsed_resume = resume_parser.parse_resume_file(tmp_file_path)

            # Score against job description
            result = ats_scorer.score_ats(parsed_resume, job_description, industry=industry)

            # Generate request ID
            request_id = f"ats_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"

            logger.info(f"ATS file scoring completed for user {user_id}, score: {result.get('overall_ats_score', 0)}")

            return ATSScoreResponse(
                score=result.get("overall_ats_score", 0),
                recommendations=result.get("optimization_opportunities", []),
                missing_keywords=result.get("missing_keywords", []),
                success_probability=result.get("success_probability", 0),
                cost=cost,
                request_id=request_id,
                timestamp=datetime.now()
            )

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except Exception as e:
        logger.error(f"Error in ATS file scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ATS file scoring failed: {str(e)}")

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
    return {"status": "healthy", "service": "ATS Scoring MCP", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
