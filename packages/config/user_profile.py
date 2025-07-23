# packages/config/user_profile.py

import json
import os
from typing import Dict, Any
from packages.utilities.encryption_utils import encrypt_data, decrypt_data
from cryptography.fernet import InvalidToken
from packages.config.settings import settings

# Define sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    "full_name",
    "email",
    "phone_number",
    "address",
    "linkedin_profile",
    "github_profile",
    "personal_website",
]


def load_user_profile(file_path: str = settings.USER_PROFILE_PATH) -> Dict[str, Any]:
    """
    [CONTEXT] Loads the user profile configuration from a JSON file and decrypts sensitive fields.
    [PURPOSE] Ensures that sensitive user data is decrypted upon loading for application use.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"User profile file not found at: {file_path}")
    with open(file_path, "r") as f:
        user_profile = json.load(f)

    # Decrypt sensitive fields
    for field in SENSITIVE_FIELDS:
        if field in user_profile and user_profile[field]:
            try:
                user_profile[field] = decrypt_data(user_profile[field])
            except InvalidToken as e:
                print(
                    f"Warning: Could not decrypt field {field} due to invalid token: {e}. Data might be unencrypted or corrupted."
                )
            except ValueError as e:
                print(
                    f"Warning: Could not decrypt field {field} due to invalid input: {e}. Data might be unencrypted or corrupted."
                )
    return user_profile


def save_user_profile(
    user_profile: Dict[str, Any], file_path: str = settings.USER_PROFILE_PATH
):
    """
    [CONTEXT] Encrypts sensitive fields and saves the user profile configuration to a JSON file.
    [PURPOSE] Ensures that sensitive user data is encrypted before being stored on disk.
    """
    # Create a copy to avoid modifying the original in-memory profile
    profile_to_save = user_profile.copy()

    # Encrypt sensitive fields
    for field in SENSITIVE_FIELDS:
        if field in profile_to_save and profile_to_save[field]:
            profile_to_save[field] = encrypt_data(profile_to_save[field])

    try:
        with open(file_path, "w") as f:
            json.dump(profile_to_save, f, indent=4)
    except (IOError, OSError) as e:
        print(f"Error saving user profile to {file_path}: {e}")
        raise RuntimeError(f"Failed to save user profile: {e}") from e
