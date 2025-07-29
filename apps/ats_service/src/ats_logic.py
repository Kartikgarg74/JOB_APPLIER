from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def extract_keywords(text: str) -> List[str]:
    # Simple keyword extraction by splitting words and converting to lowercase
    return [word.lower() for word in re.findall(r'\b\w+\b', text)]

def calculate_ats_score(resume_content: str, job_description: str) -> Dict:
    resume_keywords = extract_keywords(resume_content)
    job_keywords = extract_keywords(job_description)

    # Combine keywords for TF-IDF vectorization
    corpus = [" ".join(resume_keywords), " ".join(job_keywords)]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity for job match score
    job_match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    # Identify matched and missing keywords
    matched_keywords = list(set(resume_keywords) & set(job_keywords))
    missing_keywords = list(set(job_keywords) - set(resume_keywords))

    # Placeholder for ATS score calculation (e.g., keyword density, section completeness)
    # For now, a simple calculation based on keyword match percentage
    total_job_keywords = len(job_keywords)
    ats_score = 0.0
    if total_job_keywords > 0:
        ats_score = (len(matched_keywords) / total_job_keywords) * 100

    return {
        "job_match_score": job_match_score,
        "ats_score": ats_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    }