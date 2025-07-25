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
    # Dummy data for testing
    from packages.common_types.common_types import ResumeData
    # Test Case 1: High Match Scenario
    high_match_resume = ResumeData(
        raw_text="John Doe\nSoftware Engineer\nSkills: Python, SQL, AWS, Machine Learning, Data Analysis, Project Management\nExperience: 5 years",
        personal_details={
            "name": "Jane Doe",
            "email": "jane.doe@example.com"
        },
        summary="Highly motivated software engineer with 5 years of experience in Python development and cloud technologies.",
        skills=[
            "Python",
            "SQL",
            "AWS",
            "Machine Learning",
            "Data Analysis",
            "Project Management",
        ],
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "years": "2020-Present",
                "description": "Developed and deployed scalable machine learning models on AWS. Led a team of 5 engineers in agile environment. Optimized SQL queries for performance.",
            },
            {
                "title": "Software Engineer",
                "company": "Data Innovations",
                "years": "2018-2020",
                "description": "Built data pipelines using Python and SQL. Performed data analysis to identify key trends.",
            },
        ],
        education=[
            {
                "degree": "M.S. in Computer Science",
                "university": "State University",
                "years": "2018",
            }
        ],
    )

    high_match_job_description = (
        "We are seeking a Senior Python Engineer with strong experience in AWS, Machine Learning, and SQL. "
        "The ideal candidate will have a background in data analysis and project management, working in an agile development environment."
    )

    ats_scorer = ATSScorerAgent(None)

    print("\n--- ATS Scoring Test Results (High Match) ---")
    results_high = ats_scorer.score_ats(
        high_match_resume, high_match_job_description
    )
    print(f"Overall ATS Score: {results_high['overall_ats_score']:.2f}")
    print(f"Keyword Score: {results_high['keyword_score']:.2f}")
    print(f"Formatting Score: {results_high['formatting_score']:.2f}")
    print(f"Missing Keywords: {results_high['missing_keywords']}")
    print(f"Optimization Opportunities: {results_high['optimization_opportunities']}")
    print(
        f"Predicted Success Probability: {results_high['predicted_success_probability']}"
    )

    # Test Case 2: Low Match Scenario
    low_match_resume = {
        "name": "John Smith",
        "email": "john.s@example.com",
        "summary": "Entry-level graphic designer with experience in visual arts and digital media.",
        "skills": ["Photoshop", "Illustrator", "UI/UX Design", "Typography"],
        "experience": [
            {
                "title": "Junior Graphic Designer",
                "company": "Creative Studio",
                "years": "2021-Present",
                "description": "Designed marketing materials and digital assets for various clients.",
            }
        ],
        "education": [
            {
                "degree": "B.A. in Graphic Design",
                "university": "Art Institute",
                "years": "2021",
            }
        ],
    }

    low_match_job_description = (
        "Seeking a Lead Data Scientist with expertise in Python, R, statistical modeling, and big data technologies. "
        "Experience with machine learning algorithms and cloud platforms like Azure is a must."
    )

    print("\n--- ATS Scoring Test Results (Low Match) ---")
    results_low = ats_scorer.score_ats(low_match_resume, low_match_job_description)
    print(f"Overall ATS Score: {results_low['overall_ats_score']:.2f}")
    print(f"Keyword Score: {results_low['keyword_score']:.2f}")
    print(f"Formatting Score: {results_low['formatting_score']:.2f}")
    print(f"Missing Keywords: {results_low['missing_keywords']}")
    print(f"Optimization Opportunities: {results_low['optimization_opportunities']}")
    print(
        f"Predicted Success Probability: {results_low['predicted_success_probability']}"
    )

    # Test with a low match scenario
    dummy_resume_data_low_match = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "summary": "Experienced Java developer with a focus on enterprise applications.",
        "skills": ["Java", "Spring Boot", "Hibernate", "C++"],
        "experience": [
            {
                "title": "Java Developer",
                "company": "Enterprise Solutions",
                "years": "2017-Present",
                "description": "Developed and maintained large-scale Java applications.",
            }
        ],
        "education": [
            {
                "degree": "B.S. in Software Engineering",
                "university": "City College",
                "years": "2017",
            }
        ],
    }
    dummy_job_description_low_match = "Seeking a Python developer with expertise in data science, cloud platforms (AWS/Azure), and machine learning. Strong SQL skills required."

    results_low_match = ats_scorer.score_ats(
        dummy_resume_data_low_match, dummy_job_description_low_match
    )
    print("\n--- ATS Scoring Test Results (Low Match - Dummy Data) ---")
    print(f"Overall ATS Score: {results_low_match['overall_ats_score']:.2f}")
    print(f"Keyword Score: {results_low_match['keyword_score']:.2f}")
    print(f"Formatting Score: {results_low_match['formatting_score']:.2f}")
    print(f"Missing Keywords: {results_low_match['missing_keywords']}")
    print(f"Optimization Opportunities: {results_low_match['optimization_opportunities']}")
    print(
        f"Predicted Success Probability: {results_low_match['predicted_success_probability']}"
    )
    score1 = scorer.score_resume(dummy_resume_data, dummy_job_description_1)
    print(f"ATS Score for Job 1: {score1:.2f}")

    # Dummy job description 2 (low match)
    dummy_job_description_2 = (
        "Seeking a Front-end Developer with expertise in JavaScript, React, and CSS. "
        "Familiarity with UI/UX design principles is a plus."
    )

    print("\n--- Scoring Resume against Job 2 (Low Match) ---")
    score2 = scorer.score_resume(dummy_resume_data, dummy_job_description_2)
    print(f"ATS Score for Job 2: {score2:.2f}")

    # Dummy job description 3 (partial match)
    dummy_job_description_3 = (
        "Looking for a Cloud Engineer with AWS experience. Python scripting is a plus. "
        "Knowledge of machine learning concepts is a bonus."
    )

    print("\n--- Scoring Resume against Job 3 (Partial Match) ---")
    score3 = scorer.score_resume(dummy_resume_data, dummy_job_description_3)
    print(f"ATS Score for Job 3: {score3:.2f}")
