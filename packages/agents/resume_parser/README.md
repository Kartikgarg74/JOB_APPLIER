# Resume Parser Agent

## Purpose
The Resume Parser Agent extracts structured information from raw resume text, converting it into a standardized `ResumeData` object that can be used by other components of the system. It handles parsing of personal details, skills, experience, education, and other relevant sections from resumes in various formats.

## Dependencies
- `packages/common_types/common_types` for the `ResumeData` type definition
- `packages/agents/resume_parser/resume_utils` for utility functions

## Key Components
- `ResumeParserAgent`: The main class that orchestrates the parsing process
  - `__init__(self, db)`: Initializes the agent (database connection is optional)
  - `parse_resume(self, resume_text: str) -> Optional[ResumeData]`: Main method that takes raw resume text and returns structured data
  - `_structure_resume_data(self, raw_text: str) -> ResumeData`: Internal method that structures the parsed data

## Workflow
1. **Input Validation**: Checks if the input resume text is valid
2. **Personal Details Extraction**: Uses utility functions to extract name, email, phone, etc.
3. **Skills Extraction**: Identifies and extracts technical and soft skills
4. **Experience Parsing**: Extracts work history (currently placeholder)
5. **Education Parsing**: Extracts educational background (currently placeholder)
6. **Data Structuring**: Packages all extracted data into a standardized `ResumeData` object

## Usage Example
```python
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.utilities.logging_utils import setup_logging

# Initialize logging
setup_logging()

# Example resume text
resume_text = """
John Doe
Software Engineer
john.doe@example.com

SKILLS
Python, Java, AWS, SQL

EXPERIENCE
Senior Software Engineer at Tech Corp (2018-Present)
- Developed scalable applications using Python
- Led team of 5 engineers
"""

# Initialize parser
parser = ResumeParserAgent(None)  # Pass None for db in this example

# Parse resume
parsed_data = parser.parse_resume(resume_text)

if parsed_data:
    print(f"Extracted Skills: {parsed_data.skills}")
    print(f"Personal Details: {parsed_data.personal_details}")
else:
    print("Failed to parse resume")
```

## Error Handling
The agent includes comprehensive logging and gracefully handles:
- Empty or invalid input text
- Parsing failures for specific sections
- Unexpected formatting issues

## Testing
To test the `ResumeParserAgent`, run `resume_parser_agent.py` directly. It contains an `if __name__ == "__main__":` block with example usage and dummy data.

## Contributing
When enhancing the parser:
1. Add new extraction methods in `resume_utils.py`
2. Improve existing parsing logic for experience/education sections
3. Consider integrating NLP libraries for better entity recognition
4. Maintain the `ResumeData` structure for backward compatibility