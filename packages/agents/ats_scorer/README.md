# ATS Scorer Agent

## Purpose
The ATS Scorer Agent evaluates how well a resume matches a job description by simulating an Applicant Tracking System (ATS). It provides:
- Quantitative compatibility score (0-100)
- Keyword matching analysis
- Formatting/structure evaluation
- Optimization recommendations
- Success probability prediction

## Dependencies
- `packages/common_types/common_types` for ResumeData type
- `packages/agents/ats_scorer/ats_utils` for scoring utilities

## Key Components
- `ATSScorerAgent`: Main class that orchestrates the scoring process
  - `score_ats()`: Primary method that analyzes resume vs job description

## Workflow
1. Extracts keywords from job description
2. Calculates keyword matching score
3. Evaluates resume formatting/structure
4. Combines scores (70% keyword, 30% formatting)
5. Identifies optimization opportunities
6. Predicts application success probability

## Usage Example
```python
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.common_types.common_types import ResumeData

# Initialize agent
ats_scorer = ATSScorerAgent()

# Prepare resume data
resume_data = ResumeData(
    raw_text="...",
    personal_details={...},
    summary="...",
    skills=[...],
    experience=[...],
    education=[...]
)

# Score against job description
job_desc = "Seeking Python developer with AWS experience..."
results = ats_scorer.score_ats(resume_data, job_desc)

print(f"ATS Score: {results['overall_ats_score']}")
print(f"Missing Keywords: {results['missing_keywords']}")
```

## Error Handling
The agent includes comprehensive logging but doesn't raise exceptions - it returns partial results even if some scoring components fail.

## Testing
Run the agent directly to execute built-in test cases:
```bash
python packages/agents/ats_scorer/ats_scorer_agent.py
```

## Contributing
When modifying scoring algorithms:
1. Update weights in `score_ats()` method
2. Add new utility functions in `ats_utils.py`
3. Maintain the same return structure for backward compatibility