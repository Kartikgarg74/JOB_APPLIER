import os
import json
import logging
import os
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


def generate_key():
    """
    [CONTEXT] Generates a new Fernet encryption key.
    [PURPOSE] Provides a secure key for encrypting and decrypting data.
    """
    return Fernet.generate_key().decode()


def load_key(key_path: str = "./encryption.key") -> bytes:
    """
    [CONTEXT] Loads the encryption key from a specified path or generates a new one if not found.
    [PURPOSE] Ensures a persistent and secure key is used for encryption/decryption.
    """
    if os.path.exists(key_path):
        with open(key_path, "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    return key


# Load the key once when the module is imported
ENCRYPTION_KEY = load_key()
fernet = Fernet(ENCRYPTION_KEY)


def encrypt_data(data: str) -> str:
    """
    [CONTEXT] Encrypts a given string using Fernet symmetric encryption.
    [PURPOSE] To secure sensitive data like personal information and resumes.
    """
    try:
        encrypted_data = fernet.encrypt(data.encode("utf-8"))
        return encrypted_data.decode("utf-8")
    except ValueError as e:
        logger.error(f"Error encrypting data due to invalid input: {e}")
        raise


def decrypt_data(encrypted_data: str) -> str:
    """
    [CONTEXT] Decrypts a given string using Fernet symmetric encryption.
    [PURPOSE] To retrieve sensitive data securely.
    """
    try:
        decrypted_data = fernet.decrypt(encrypted_data.encode("utf-8"))
        return decrypted_data.decode("utf-8")
    except InvalidToken as e:
        logger.error(f"Error decrypting data due to invalid token: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error decrypting data due to invalid input: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example Usage
    original_data = json.dumps({"name": "John Doe", "email": "john.doe@example.com"})
    print(f"Original: {original_data}")

    encrypted = encrypt_data(original_data)
    print(f"Encrypted: {encrypted}")

    decrypted = decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")

    assert json.loads(original_data) == json.loads(decrypted)
    print("Encryption/Decryption successful!")
