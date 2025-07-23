# Types Package

## Purpose
This package defines common data structures and type hints used across the JobApplierAgent monorepo. Centralizing type definitions ensures consistency, improves code readability, and enables better static analysis and IDE support.

## Dependencies
This package has no internal dependencies within the monorepo. It primarily relies on Python's built-in `typing` module.

## Key Components
- `common_types.py`: Contains `TypedDict` definitions and other type aliases for frequently used data structures such as:
  - `ResumeData`: Structured representation of parsed resume information.
  - `JobListing`: Structured representation of a job posting.
  - `UserProfile`: Configuration details for the user.
  - `ATSResult`: Result of an ATS compatibility score calculation.
  - `ApplicationStatus`: Status of a submitted job application.

## Usage Examples
Types defined here can be imported and used in function signatures, class attributes, and variable annotations throughout the monorepo to improve type safety and clarity.

Example of importing and using a type:
```python
from packages.common_types.common_types import JobListing, ResumeData

def process_job_and_resume(job: JobListing, resume: ResumeData):
    # Function logic here
    pass
```

## API Reference
Refer to `common_types.py` for a complete list and detailed definitions of all available types.

## Development Setup
No specific setup is required for this package beyond the general monorepo setup.

## Testing
Type definitions typically do not require dedicated unit tests, as their correctness is validated through static analysis tools (like MyPy) and their usage in other modules' tests.

## Contributing
Refer to the main `README.md` in the monorepo root for general contribution guidelines.