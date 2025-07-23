# Resume Parser Utilities

## Purpose
This module, `resume_parser.py`, is designed to provide helper functions for parsing various resume formats (PDF, DOCX, TXT) and extracting their raw text content. It serves as a foundational component for processing user resumes within the Job Applier application, enabling further analysis such as ATS scoring or information extraction.

## Dependencies
- Standard Python libraries (`os` for file path handling, implicitly).

## Key Functions
- `parse_pdf_resume(file_path: str) -> str`:
  - **Purpose**: Parses a PDF resume file and returns its text content.
  - **Note**: Currently contains placeholder logic. In a full implementation, this would integrate with libraries like `PyPDF2` or `pdfminer.six`.
  - **Parameters**:
    - `file_path` (str): The absolute or relative path to the PDF resume file.
  - **Returns**: A string containing the extracted text content from the PDF.

- `parse_docx_resume(file_path: str) -> str`:
  - **Purpose**: Parses a DOCX resume file and returns its text content.
  - **Note**: Currently contains placeholder logic. In a full implementation, this would integrate with libraries like `python-docx`.
  - **Parameters**:
    - `file_path` (str): The absolute or relative path to the DOCX resume file.
  - **Returns**: A string containing the extracted text content from the DOCX.

- `extract_text_from_resume(file_path: str) -> str`:
  - **Purpose**: A dispatcher function that determines the resume file type based on its extension and calls the appropriate parsing function. If the file is neither PDF nor DOCX, it attempts to read it as a plain text file.
  - **Parameters**:
    - `file_path` (str): The absolute or relative path to the resume file.
  - **Returns**: A string containing the extracted text content from the resume.
  - **Error Handling**: Prints an error message to the console if the file is not found or if there's an `IOError` during plain text file reading, returning an empty string in such cases.

## Workflow
1. A resume file's path is provided to `extract_text_from_resume`.
2. The function checks the file extension (`.pdf`, `.docx`, `.doc`).
3. Based on the extension, it calls `parse_pdf_resume`, `parse_docx_resume`, or attempts to read the file as plain text.
4. The extracted text content is returned.

## Usage Example
```python
from packages.utilities.parsers.resume_parser import extract_text_from_resume

# Example 1: Parsing a PDF resume (placeholder output)
pdf_resume_path = "./path/to/your/resume.pdf"
text_content_pdf = extract_text_from_resume(pdf_resume_path)
print(f"Text from PDF: {text_content_pdf}")

# Example 2: Parsing a DOCX resume (placeholder output)
docx_resume_path = "./path/to/your/resume.docx"
text_content_docx = extract_text_from_resume(docx_resume_path)
print(f"Text from DOCX: {text_content_docx}")

# Example 3: Reading a plain text resume
# Create a dummy text file for demonstration
with open("./path/to/your/resume.txt", "w", encoding="utf-8") as f:
    f.write("This is a plain text resume.\nIt has multiple lines.")

text_resume_path = "./path/to/your/resume.txt"
text_content_txt = extract_text_from_resume(text_resume_path)
print(f"Text from TXT: {text_content_txt}")

# Example 4: Handling a non-existent file
non_existent_path = "./path/to/non_existent_resume.pdf"
text_content_non_existent = extract_text_from_resume(non_existent_path)
print(f"Text from non-existent file: '{text_content_non_existent}' (should be empty)")
```

## Future Enhancements
- Integration with actual PDF and DOCX parsing libraries (e.g., `PyPDF2`, `pdfminer.six`, `python-docx`).
- More robust error handling and logging instead of `print` statements.
- Support for other resume formats (e.g., RTF, ODT).
- Extraction of structured data (e.g., sections like education, experience, skills) rather than just raw text.