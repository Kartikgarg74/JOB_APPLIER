# File Management Utilities

## Purpose
This directory contains utilities for handling file operations within the application, such as reading, writing, and managing files and directories. It provides both standalone functions for basic file system interactions and a class-based interface for managing files within a specific base directory, including support for encrypted JSON data.

## Dependencies
- `json`: For JSON serialization and deserialization.
- `shutil`: For high-level file operations, specifically deleting directories.
- `logging`: For logging errors and warnings.
- `os`: For path manipulation and directory creation/listing.
- `packages.utilities.encryption_utils`: For encrypting and decrypting sensitive data stored in JSON files.

## Key Components

### `file_operations.py`
This module contains a collection of standalone functions for common file system operations:

- **`read_file(file_path: str) -> Optional[str]`**
  - Reads the content of a text file. Handles `FileNotFoundError`, `IOError`, and `OSError`.

- **`write_file(file_path: str, content: str) -> bool`**
  - Writes content to a text file. Creates parent directories if they don't exist. Handles `IOError` and `OSError`.

- **`read_json_file(file_path: str) -> Optional[Dict[str, Any]]`**
  - Reads and parses a JSON file. Returns `None` on `json.JSONDecodeError` or if the file cannot be read.

- **`write_json_file(file_path: str, data: Dict[str, Any]) -> bool`**
  - Writes a dictionary to a JSON file with an indent of 4. Returns `False` on `IOError`, `OSError`, or JSON encoding issues.

- **`create_directory(dir_path: str) -> bool`**
  - Creates a directory if it does not already exist. Handles `IOError` and `OSError`.

- **`delete_file(file_path: str) -> bool`**
  - Deletes a specified file. Logs a warning if the file does not exist. Handles `IOError` and `OSError`.

- **`delete_directory(dir_path: str) -> bool`**
  - Deletes a directory and all its contents recursively. Logs a warning if the path is not an existing directory. Handles `IOError` and `OSError`.

- **`list_directory_contents(dir_path: str) -> Optional[List[str]]`**
  - Lists the contents (files and directories) of a given directory. Returns `None` if the path is not a directory or on error.

### `FileManagement` Class (within `file_operations.py`)
This class provides a centralized interface for file and directory operations relative to a specified base directory. It's particularly useful for managing application-specific data storage.

- **`__init__(self, base_output_dir: str)`**
  - Initializes the `FileManagement` instance with a `base_output_dir`, ensuring this directory exists.

- **`get_output_path(self, *paths: str) -> str`**
  - Constructs an absolute path within the `base_output_dir`.

- **`read_file(self, relative_path: str) -> Optional[str]`**
  - Reads a file from the base output directory using `file_operations.read_file`.

- **`write_file(self, relative_path: str, content: str) -> bool`**
  - Writes content to a file within the base output directory using `file_operations.write_file`.

- **`read_json(self, relative_path: str) -> Optional[Dict[str, Any]]`**
  - Reads and parses a JSON file from the base output directory. **Crucially, it includes logic to decrypt content if the file is `user_resume.json` or `user_profile.json` and contains an `encrypted_content` field or is an encrypted string itself.**

- **`write_json(self, relative_path: str, data: Dict[str, Any]) -> bool`**
  - Writes a dictionary to a JSON file within the base output directory using `file_operations.write_json_file`.

### `file_handler.py`
This file is currently empty and serves as a placeholder for future, more advanced file handling logic if required.

## Usage Examples

```python
import os
from packages.utilities.file_management.file_operations import (
    read_file,
    write_file,
    read_json_file,
    write_json_file,
    create_directory,
    delete_file,
    delete_directory,
    list_directory_contents,
    FileManagement,
)

# --- Standalone Functions Examples ---

# Example: Write and Read a text file
text_file_path = "./temp_data/my_text_file.txt"
write_file(text_file_path, "Hello, this is a test.\nNew line.")
content = read_file(text_file_path)
print(f"Read from text file: {content}")

# Example: Write and Read a JSON file
json_file_path = "./temp_data/my_data.json"
data = {"name": "Alice", "age": 30, "isStudent": False}
write_json_file(json_file_path, data)
read_data = read_json_file(json_file_path)
print(f"Read from JSON file: {read_data}")

# Example: Create and List a directory
new_dir_path = "./temp_data/sub_dir"
create_directory(new_dir_path)
contents = list_directory_contents("./temp_data")
print(f"Contents of temp_data: {contents}")

# Example: Delete a file
delete_file(text_file_path)

# Example: Delete a directory
delete_directory("./temp_data")

# --- FileManagement Class Examples ---

# Initialize FileManagement with a base directory
fm = FileManagement("./app_data")

# Write a file using FileManagement
fm.write_file("logs/app.log", "Application started.\n")

# Write JSON data (e.g., user profile)
user_profile_data = {"username": "testuser", "email": "test@example.com"}
fm.write_json("users/profile.json", user_profile_data)

# Read JSON data
profile = fm.read_json("users/profile.json")
print(f"User profile from FileManagement: {profile}")

# Clean up FileManagement base directory
delete_directory("./app_data")
```

## Error Handling
Both the standalone functions and the `FileManagement` class incorporate robust error handling for common file system operations. Errors such as `FileNotFoundError`, `IOError`, `OSError`, and `json.JSONDecodeError` are caught and logged using the `logging` module, preventing application crashes and providing clear diagnostic messages. Warnings are logged for operations on non-existent files or directories (e.g., attempting to delete a file that doesn't exist).

## Security Considerations
When using `read_json` with `user_resume.json` or `user_profile.json`, the module attempts to decrypt the content using `encryption_utils`. This implies that sensitive user data is expected to be stored encrypted. Ensure that encryption keys are managed securely (e.g., via environment variables, not hardcoded) and that access to these keys is strictly controlled to maintain data confidentiality.