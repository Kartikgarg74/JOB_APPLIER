# File Operations and Management Utilities

## Purpose
This module, `file_operations.py`, provides a robust set of functions and a class for performing common file system operations within the Job Applier application. It aims to centralize file handling, ensuring consistency, error handling, and proper management of file paths, especially for user-specific data.

## Dependencies
- `os`: For interacting with the operating system, primarily for path manipulation and directory creation.
- `json`: For encoding and decoding JSON data.
- `shutil`: For high-level file operations, specifically for deleting entire directory trees.
- `logging`: For logging errors and informational messages.
- `packages.utilities.encryption_utils`: Used for encrypting and decrypting sensitive data when reading/writing specific JSON files (e.g., `user_resume.json`, `user_profile.json`).

## Key Functions
- `read_file(file_path: str) -> Optional[str]`:
  - **Purpose**: Reads the entire content of a text file.
  - **Error Handling**: Logs `FileNotFoundError`, `IOError`, or `OSError` and returns `None`.
- `write_file(file_path: str, content: str) -> bool`:
  - **Purpose**: Writes string content to a text file. Creates parent directories if they don't exist.
  - **Error Handling**: Logs `IOError` or `OSError` and returns `False` on failure.
- `read_json_file(file_path: str) -> Optional[Dict[str, Any]]`:
  - **Purpose**: Reads and parses a JSON file into a Python dictionary.
  - **Error Handling**: Logs `json.JSONDecodeError` if the file content is not valid JSON, or other file-related errors, returning `None`.
- `write_json_file(file_path: str, data: Dict[str, Any]) -> bool`:
  - **Purpose**: Writes a Python dictionary to a file as formatted JSON (with 4-space indentation).
  - **Error Handling**: Logs `IOError` or `OSError` and returns `False` on failure.
- `create_directory(dir_path: str) -> bool`:
  - **Purpose**: Creates a directory, including any necessary parent directories. Does nothing if the directory already exists.
  - **Error Handling**: Logs `IOError` or `OSError` and returns `False` on failure.
- `delete_file(file_path: str) -> bool`:
  - **Purpose**: Deletes a specified file. Logs a warning if the file does not exist.
  - **Error Handling**: Logs `IOError` or `OSError` and returns `False` on failure.
- `delete_directory(dir_path: str) -> bool`:
  - **Purpose**: Deletes a directory and all its contents recursively. Logs a warning if the path is not an existing directory.
  - **Error Handling**: Logs `IOError` or `OSError` and returns `False` on failure.
- `list_directory_contents(dir_path: str) -> Optional[List[str]]`:
  - **Purpose**: Lists the names of all files and subdirectories within a given directory.
  - **Error Handling**: Logs a warning if the path is not a directory, or other `IOError`/`OSError`, returning `None`.

## `FileManagement` Class

### Purpose
Encapsulates file and directory operations, providing a centralized interface that operates relative to a defined `base_output_dir`. This ensures all managed files are stored in a consistent and controlled location, and includes special handling for encrypted user data.

### Initialization
`FileManagement(base_output_dir: str)`
- Initializes the instance with a `base_output_dir` and ensures this directory exists.

### Key Methods
- `get_output_path(*paths: str) -> str`:
  - **Purpose**: Constructs an absolute file path by joining the `base_output_dir` with provided relative path components.
- `read_file(relative_path: str) -> Optional[str]`:
  - **Purpose**: Reads a file located within the `base_output_dir`.
- `write_file(relative_path: str, content: str) -> bool`:
  - **Purpose**: Writes content to a file within the `base_output_dir`.
- `read_json(relative_path: str) -> Optional[Dict[str, Any]]`:
  - **Purpose**: Reads and parses a JSON file from the `base_output_dir`. Special handling is included for `user_resume.json` and `user_profile.json`, where the content is expected to be encrypted and is automatically decrypted using `encryption_utils.decrypt_data`.
- `write_json(relative_path: str, data: Dict[str, Any]) -> bool`:
  - **Purpose**: Writes a dictionary to a JSON file within the `base_output_dir`. (Note: The provided snippet for this method is incomplete, but it's expected to handle JSON serialization and potentially encryption for specific files.)

## Usage Example (FileManagement Class)
```python
import os
from packages.utilities.file_management.file_operations import FileManagement

# Initialize FileManagement with a base directory
output_dir = "./data/user_files"
file_manager = FileManagement(output_dir)

# Example: Writing a text file
text_content = "This is some sample text."
file_manager.write_file("documents/sample.txt", text_content)
print(f"Wrote text to {file_manager.get_output_path('documents/sample.txt')}")

# Example: Reading a text file
read_text = file_manager.read_file("documents/sample.txt")
print(f"Read text: {read_text}")

# Example: Writing a JSON file
json_data = {"name": "John Doe", "age": 30}
file_manager.write_json("profiles/user_data.json", json_data)
print(f"Wrote JSON to {file_manager.get_output_path('profiles/user_data.json')}")

# Example: Reading a JSON file (without encryption)
read_json = file_manager.read_json("profiles/user_data.json")
print(f"Read JSON: {read_json}")

# Example: Simulating encrypted user profile data read
# (Requires actual encrypted content to work, this is illustrative)
# Assuming 'encrypted_user_profile.json' contains {"encrypted_content": "<encrypted_string>"}
# user_profile = file_manager.read_json("user_profile.json")
# if user_profile:
#     print(f"Decrypted User Profile: {user_profile}")

# Clean up (optional)
# file_manager.delete_directory(output_dir)
# print(f"Cleaned up directory: {output_dir}")
```

## Best Practices
- Always use the `FileManagement` class for operations within a specific project output path to maintain consistency.
- Leverage the provided utility functions for basic file operations to ensure proper error handling and logging.
- Be mindful of the encryption/decryption logic when handling sensitive user data, ensuring the correct file names (`user_resume.json`, `user_profile.json`) are used for automatic decryption.