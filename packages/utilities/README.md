# Utilities Package

## Purpose
This package provides a collection of reusable utility modules that support the functionality of the JobApplierAgent and its various sub-agents. These utilities are designed to be generic and can be used across different parts of the monorepo.

## Dependencies
Utilities generally have minimal dependencies within the monorepo, primarily relying on standard Python libraries or external third-party packages as specified in the main application's `requirements.txt`.

## Key Components
- `parsers/`: Contains modules for parsing different types of data, such as resumes and job descriptions.
  - `resume_parser.py`: Functions to extract text and structured data from resume files (e.g., PDF, DOCX).
  - `job_description_parser.py`: Functions to parse and extract key information from raw job description text.
- `file_management/`: Provides utilities for common file system operations.
  - `file_operations.py`: Provides utility functions for reading and writing files (text and JSON), creating and deleting directories, and listing directory contents. It also includes the `FileManagement` class for managing file operations relative to a base output directory.
- `vector_matching/`: Modules for generating and comparing text embeddings.
  - `embedding_generator.py`: Functions to create numerical representations (embeddings) of text.
  - `vector_matcher.py`: Functions to calculate similarity between vectors and perform matching.
- `browser_automation/`: Contains tools for controlling web browsers.
  - `browser_controller.py`: Abstraction layer for browser interactions (e.g., navigation, form filling, scraping) using tools like Selenium or Playwright.
- `ats_benchmarks/`: Data and logic for benchmarking ATS scoring and related functionalities.
  - `benchmark_data.py`: Sample data for testing and benchmarking the ATS scoring and resume enhancement agents.
- `logging_utils.py`: Configures and manages logging for the application.
- `retry_utils.py`: Provides a decorator for retrying failed operations with exponential backoff.

## Usage Examples
Utilities can be imported and used directly by any agent or application within the monorepo.

Example of using a file operation utility:
```python
from packages.utilities.file_management.file_operations import read_file

content = read_file("path/to/some/file.txt")
if content:
    print(content)
```

Example of using an embedding generator:
```python
from packages.utilities.vector_matching.embedding_generator import EmbeddingGenerator

embedder = EmbeddingGenerator()
text_embedding = embedder.generate_embedding("This is a sample text.")
```

## API Reference
Refer to the individual utility files for detailed function and class signatures and documentation.

## Development Setup
No specific setup is required for this package beyond the general monorepo setup. Ensure all Python dependencies are installed as per the main application's `requirements.txt`.

## Testing
Unit tests for utility functions should be placed in `apps/job-applier-agent/tests/utilities/`.

## Contributing
Refer to the main `README.md` in the monorepo root for general contribution guidelines.