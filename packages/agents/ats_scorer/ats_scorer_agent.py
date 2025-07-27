import logging
from typing import Dict, Any
from packages.common_types.common_types import ResumeData
from packages.agents.ats_scorer.ats_utils import (
    extract_keywords,
    calculate_keyword_score_and_density,
    identify_optimization_opportunities,
    predict_success_probability,
    check_ats_unfriendly_formatting,
    get_industry_weights,
    benchmark_score,
)


class ATSScorerAgent:
    """
    [CONTEXT] Scores the compatibility of a resume with a job description, simulating an ATS.
    [PURPOSE] Provides a quantitative measure of how well a resume matches a job's requirements,
              identifies optimization opportunities, and predicts application success.
    """

    def __init__(self, db=None):
        self.db = db # Keep db for consistency, though not directly used in this simplified version
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("ATSScorerAgent initialized.")

    def score_ats(
        self, resume_data: ResumeData, job_description: str, industry: str = None
    ) -> Dict[str, Any]:
        """
        [CONTEXT] Analyzes the resume and job description to calculate an ATS compatibility score,
                  identify optimization opportunities, and predict success probability.
        [PURPOSE] Returns a comprehensive report including score, opportunities, and prediction.
        """
        self.logger.info("Starting ATS scoring process.")

        # 1. Extract keywords from job description
        job_keywords = extract_keywords(job_description)

        # 2. Simulate keyword density and matching
        # Enhanced: Use structured data and get density and underrepresented keywords
        keyword_score, missing_keywords, keyword_density, underrepresented_keywords = calculate_keyword_score_and_density(
            resume_data, job_keywords
        )

        # 3. Simulate formatting and structure score
        # Formatting checks
        formatting_result = check_ats_unfriendly_formatting(resume_data.get('raw_text', ''))
        formatting_score = formatting_result['formatting_score']

        # Combine scores (weights can be adjusted)
        # Keyword matching is typically the most important factor for ATS
        # Industry weights
        weights = get_industry_weights(industry)
        # Weighted overall score
        overall_score = (
            keyword_score * weights.get('keywords', 0.7)
            + formatting_score * weights.get('formatting', 0.3)
            + sum([
                (sum([resume_data.get('skills', []).count(k) for k in job_keywords]) / max(1, len(job_keywords))) * weights.get('skills', 0)
                if 'skills' in weights else 0,
                (sum([str(exp.get('description', '')).lower().count(k.lower()) for exp in resume_data.get('experience', []) if isinstance(exp, dict) for k in job_keywords]) / max(1, len(job_keywords))) * weights.get('experience', 0)
                if 'experience' in weights else 0,
                (sum([resume_data.get('summary', '').lower().count(k.lower()) for k in job_keywords]) / max(1, len(job_keywords))) * weights.get('summary', 0)
                if 'summary' in weights else 0,
                (len(resume_data.get('certifications', [])) / 3.0) * weights.get('certifications', 0)
                if 'certifications' in weights else 0,
            ])
        )
        overall_score = min(round(overall_score * 100, 2), 100.0)

        # Identify ATS optimization opportunities
        optimization_opportunities = identify_optimization_opportunities(
            missing_keywords, resume_data
        )

        # Predict application success probability
        success_probability = predict_success_probability(overall_score)
        percentile = benchmark_score(overall_score, industry)

        self.logger.info(f"ATS scoring completed. Overall Score: {overall_score:.2f}")

        return {
            "overall_ats_score": overall_score,
            "keyword_score": round(keyword_score * 100, 2),
            "keyword_density": keyword_density,
            "underrepresented_keywords": underrepresented_keywords,
            "formatting_score": round(formatting_score * 100, 2),
            "formatting_issues": formatting_result['issues'],
            "missing_keywords": missing_keywords,
            "optimization_opportunities": optimization_opportunities,
            "predicted_success_probability": success_probability,
            "benchmark_percentile": percentile,
        }


if __name__ == "__main__":
    # TODO: Replace any sample or dummy data with real data integration
    pass
