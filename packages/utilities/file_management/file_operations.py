import os
import json
import shutil
import logging
from typing import Any, Dict, List, Optional
from packages.utilities.encryption_utils import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


def read_file(file_path: str) -> Optional[str]:
    """
    [CONTEXT] Reads the content of a text file.
    [PURPOSE] Provides a utility to safely read file contents, handling potential errors.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except (IOError, OSError) as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def write_file(file_path: str, content: str) -> bool:
    """
    [CONTEXT] Writes content to a text file.
    [PURPOSE] Provides a utility to safely write content to a file, creating directories if necessary.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except (IOError, OSError) as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False


def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    [CONTEXT] Reads and parses a JSON file.
    [PURPOSE] Provides a utility to safely load JSON data from a file.
    """
    content = read_file(file_path)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {e}")
            return None
    return None


def write_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    [CONTEXT] Writes a dictionary to a JSON file.
    [PURPOSE] Provides a utility to safely save dictionary data as JSON to a file.
    """
    try:
        json_content = json.dumps(data, indent=4)
        return write_file(file_path, json_content)
    except (IOError, OSError) as e:
        logger.error(f"Error encoding JSON for {file_path}: {e}")
        return False


def create_directory(dir_path: str) -> bool:
    """
    [CONTEXT] Creates a directory if it does not already exist.
    [PURPOSE] Ensures that necessary directories are in place before file operations.
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except (IOError, OSError) as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return False


def delete_file(file_path: str) -> bool:
    """
    [CONTEXT] Deletes a specified file.
    [PURPOSE] Provides a utility to remove files safely.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            logger.warning(f"Attempted to delete non-existent file: {file_path}")
            return False
    except (IOError, OSError) as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def delete_directory(dir_path: str) -> bool:
    """
    [CONTEXT] Deletes a directory and all its contents.
    [PURPOSE] Provides a utility to remove directories safely.
    """
    try:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            return True
        else:
            logger.warning(
                f"Attempted to delete non-existent or non-directory path: {dir_path}"
            )
            return False
    except (IOError, OSError) as e:
        logger.error(f"Error deleting directory {dir_path}: {e}")
        return False


def list_directory_contents(dir_path: str) -> Optional[List[str]]:
    """
    [CONTEXT] Lists the contents (files and directories) of a given directory.
    [PURPOSE] Provides a utility to inspect directory contents.
    """
    try:
        if os.path.isdir(dir_path):
            return os.listdir(dir_path)
        else:
            logger.warning(f"Path is not a directory: {dir_path}")
            return None
    except (IOError, OSError) as e:
        logger.error(f"Error listing directory contents for {dir_path}: {e}")
        return None


class FileManagement:
    """
    [CONTEXT] Provides a centralized interface for file and directory operations within a specified base directory.
    [PURPOSE] Encapsulates common file system interactions, ensuring operations are relative to a defined output path.
    """

    def __init__(self, base_output_dir: str):
        self.base_output_dir = base_output_dir
        create_directory(self.base_output_dir)
        logger.info(
            f"FileManagement initialized with base output directory: {self.base_output_dir}"
        )

    def get_output_path(self, *paths: str) -> str:
        """
        [CONTEXT] Constructs an absolute path within the base output directory.
        [PURPOSE] Ensures all generated files are stored in a consistent and managed location.
        """
        return os.path.join(self.base_output_dir, *paths)

    def read_file(self, relative_path: str) -> Optional[str]:
        """
        [CONTEXT] Reads a file from the base output directory.
        [PURPOSE] Simplifies reading files that are managed by this FileManagement instance.
        """
        file_path = self.get_output_path(relative_path)
        return read_file(file_path)

    def write_file(self, relative_path: str, content: str) -> bool:
        """
        [CONTEXT] Writes content to a file within the base output directory.
        [PURPOSE] Simplifies writing files that are managed by this FileManagement instance.
        """
        file_path = self.get_output_path(relative_path)
        return write_file(file_path, content)

    def read_json(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """
        [CONTEXT] Reads and parses a JSON file from the base output directory.
        [PURPOSE] Simplifies reading JSON files that are managed by this FileManagement instance.
        """
        file_path = self.get_output_path(relative_path)
        try:
            data = read_json_file(file_path)
            if data and (
                relative_path == "user_resume.json" or relative_path == "user_profile.json"
            ):
                # Assuming the content of the JSON file is a string that was encrypted
                # If the JSON itself contains encrypted fields, this logic needs adjustment
                if isinstance(data, dict) and "encrypted_content" in data:
                    decrypted_content = decrypt_data(data["encrypted_content"])
                    return json.loads(decrypted_content)
                elif isinstance(data, str):
                    decrypted_content = decrypt_data(data)
                    return json.loads(decrypted_content)
            return data
        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error(f"Error reading or decrypting JSON from {file_path}: {e}")
            return None

    def write_json(self, relative_path: str, data: Dict[str, Any]) -> bool:
        """
        [CONTEXT] Writes a dictionary to a JSON file within the base output directory.
        [PURPOSE] Simplifies writing JSON files that are managed by this FileManagement instance.
        """
        file_path = self.get_output_path(relative_path)
        try:
            if relative_path == "user_resume.json" or relative_path == "user_profile.json":
                encrypted_content = encrypt_data(json.dumps(data))
                # Store as a JSON object with an encrypted_content field
                return write_json_file(
                    file_path, {"encrypted_content": encrypted_content}
                )
            return write_json_file(file_path, data)
        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error(f"Error writing or encrypting JSON for {file_path}: {e}")
            return False

    def create_dir(self, relative_path: str) -> bool:
        """
        [CONTEXT] Creates a directory within the base output directory.
        [PURPOSE] Simplifies creating directories that are managed by this FileManagement instance.
        """
        dir_path = self.get_output_path(relative_path)
        return create_directory(dir_path)

    def delete_file(self, relative_path: str) -> bool:
        """
        [CONTEXT] Deletes a file within the base output directory.
        [PURPOSE] Simplifies deleting files that are managed by this FileManagement instance.
        """
        file_path = self.get_output_path(relative_path)
        return delete_file(file_path)

    def delete_dir(self, relative_path: str) -> bool:
        """
        [CONTEXT] Deletes a directory and its contents within the base output directory.
        [PURPOSE] Simplifies deleting directories that are managed by this FileManagement instance.
        """
        dir_path = self.get_output_path(relative_path)
        return delete_directory(dir_path)

    def list_contents(self, relative_path: str = ".") -> Optional[List[str]]:
        """
        [CONTEXT] Lists the contents of a directory within the base output directory.
        [PURPOSE] Simplifies listing directory contents that are managed by this FileManagement instance.
        """
        dir_path = self.get_output_path(relative_path)
        return list_directory_contents(dir_path)


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging
    from packages.config.settings import load_settings

    setup_logging()
    settings = load_settings()

    # Initialize FileManagement with the configured output directory
    fm = FileManagement(settings.OUTPUT_DIR)

    # Example Usage:
    test_dir = "test_files"
    test_file_txt = os.path.join(test_dir, "example.txt")
    test_file_json = os.path.join(test_dir, "data.json")

    print(f"\n--- Testing FileManagement in {fm.base_output_dir} ---")

    # 1. Create a directory
    print(f"Creating directory '{test_dir}': {fm.create_dir(test_dir)}")

    # 2. Write a text file
    print(
        f"Writing text file '{test_file_txt}': {fm.write_file(test_file_txt, 'Hello, FileManagement!')}"
    )

    # 3. Read the text file
    content = fm.read_file(test_file_txt)
    print(f"Reading text file '{test_file_txt}': {content}")

    # 4. Write a JSON file
    json_data = {"name": "Test", "value": 123}
    print(
        f"Writing JSON file '{test_file_json}': {fm.write_json(test_file_json, json_data)}"
    )

    # 5. Read the JSON file
    read_data = fm.read_json(test_file_json)
    print(f"Reading JSON file '{test_file_json}': {read_data}")

    # 6. List directory contents
    print(f"Listing contents of '{test_dir}': {fm.list_contents(test_dir)}")

    # 7. Delete a file
    print(f"Deleting file '{test_file_txt}': {fm.delete_file(test_file_txt)}")

    # 8. Delete a directory
    print(f"Deleting directory '{test_dir}': {fm.delete_dir(test_dir)}")

    print("--- FileManagement testing complete ---")

    # Test error cases
    print("\n--- Testing Error Cases ---")
    print(f"Reading non-existent file: {fm.read_file('non_existent.txt')}")
    print(f"Deleting non-existent file: {fm.delete_file('non_existent.txt')}")
    print(f"Deleting non-existent directory: {fm.delete_dir('non_existent_dir')}")
    print("--- Error Cases testing complete ---")
