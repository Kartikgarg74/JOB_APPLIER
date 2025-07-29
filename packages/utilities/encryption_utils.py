import os
import json
import logging
import os
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

# Initialize logger after load_dotenv to ensure proper configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Ensure INFO messages are captured


def generate_key():
    """
    [CONTEXT] Generates a new Fernet encryption key.
    [PURPOSE] Provides a secure key for encrypting and decrypting data.
    """
    return Fernet.generate_key().decode()


def load_key() -> bytes:
    """
    Loads the encryption key from the FERNET_KEY environment variable.
    """
    fernet_key = os.getenv("FERNET_KEY")
    if not fernet_key:
        logger.error("FERNET_KEY environment variable not set.")
        raise ValueError("FERNET_KEY environment variable not set.")
    logger.info(f"Loaded FERNET_KEY: {fernet_key[:5]}... Full key: {fernet_key}") # Log first 5 chars for security
    return fernet_key.encode("utf-8")


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


def mask_email(email: str) -> str:
    if not email or '@' not in email:
        return email
    name, domain = email.split('@', 1)
    if len(name) <= 1:
        return '*' * len(name) + '@' + domain
    return name[0] + '***' + '@' + domain

def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 4:
        return '*' * len(phone)
    return '*' * (len(phone) - 4) + phone[-4:]

# Add more masking functions as needed (address, etc.)


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
