# packages/utilities/ats_benchmarks/benchmark_data.py

# This file is now ready for real benchmarking data. All sample data has been removed.

SAMPLE_RESUMES = []
SAMPLE_JOB_DESCRIPTIONS = []

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
