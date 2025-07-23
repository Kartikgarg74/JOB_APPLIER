# packages/utilities/ats_benchmarks/benchmark_data.py

# This file would contain sample resume and job description data for benchmarking
# the ATS scoring and resume enhancement agents.

SAMPLE_RESUMES = [
    {
        "id": "resume_1",
        "content": "Experienced Software Engineer with 5 years in Python and Machine Learning...",
        "keywords": ["Python", "Machine Learning", "Software Development"],
        "skills": ["Python", "TensorFlow", "AWS"],
    },
    {
        "id": "resume_2",
        "content": "Data Scientist with strong statistical modeling and R/Python skills...",
        "keywords": ["Data Science", "Statistical Modeling", "R", "Python"],
        "skills": ["R", "Python", "SQL", "Pandas"],
    },
]

SAMPLE_JOB_DESCRIPTIONS = [
    {
        "id": "job_1",
        "title": "Senior Python Developer",
        "company": "InnovateX",
        "description": "Seeking a Senior Python Developer with expertise in backend systems and cloud technologies. Experience with AWS and large-scale data processing is a plus.",
        "requirements": "5+ years of Python development, experience with RESTful APIs, SQL, and cloud platforms.",
        "keywords": ["Python", "Backend", "Cloud", "AWS", "RESTful APIs"],
        "skills": ["Python", "SQL", "AWS"],
    },
    {
        "id": "job_2",
        "title": "Junior Data Scientist",
        "company": "Data Insights Inc.",
        "description": "Entry-level Data Scientist position. Responsibilities include data analysis, model building, and reporting. Familiarity with R or Python is required.",
        "requirements": "Bachelor's in Statistics or Computer Science. Proficiency in R or Python, and basic understanding of machine learning concepts.",
        "keywords": [
            "Data Scientist",
            "Data Analysis",
            "Machine Learning",
            "R",
            "Python",
        ],
        "skills": ["R", "Python", "Statistics"],
    },
]

# Expected ATS scores for benchmarks (manual assessment)
EXPECTED_ATS_SCORES = {
    ("resume_1", "job_1"): {
        "score": 85,
        "reason": "High match on Python, experience, and AWS.",
    },
    ("resume_1", "job_2"): {
        "score": 40,
        "reason": "Some Python match, but not data science focused.",
    },
    ("resume_2", "job_1"): {
        "score": 30,
        "reason": "Data science focus, less on backend development.",
    },
    ("resume_2", "job_2"): {
        "score": 90,
        "reason": "Excellent match on data science, R/Python, and skills.",
    },
}
