# Encryption Utilities

## Purpose
This module provides utilities for symmetric encryption and decryption of sensitive data within the Job Applier application. It uses the Fernet recipe from the `cryptography` library, ensuring that data such as personal information, API keys, or other confidential strings are securely stored and transmitted.

## Dependencies
- `cryptography`: For robust cryptographic primitives, specifically the Fernet symmetric encryption.

## Key Components
- `generate_key() -> str`: Generates a new Fernet encryption key. This key is crucial for both encryption and decryption.
- `load_key(key_path: str = "./encryption.key") -> bytes`: Loads the encryption key from a specified file path. If the key file does not exist, a new key is generated and saved to that path, ensuring persistence.
- `ENCRYPTION_KEY`: A global variable that stores the loaded encryption key, initialized when the module is imported.
- `fernet`: A `Fernet` instance initialized with `ENCRYPTION_KEY`, used for performing encryption and decryption operations.
- `encrypt_data(data: str) -> str`: Encrypts a given string. The input string is UTF-8 encoded before encryption, and the encrypted bytes are then UTF-8 decoded for storage/transmission.
- `decrypt_data(encrypted_data: str) -> str`: Decrypts an encrypted string. It expects a UTF-8 encoded string, which is then decoded to bytes before decryption. Includes error handling for invalid tokens.

## Workflow
1. **Key Management**: Upon module import, `load_key()` is called to either load an existing `encryption.key` file or generate a new one. This ensures a consistent key is used across the application.
2. **Encryption**: Data is passed to `encrypt_data()`, which uses the loaded Fernet key to encrypt the string.
3. **Decryption**: Encrypted data is passed to `decrypt_data()`, which uses the same Fernet key to decrypt the string.

## Usage Example
```python
import json
from packages.utilities.encryption_utils import encrypt_data, decrypt_data

# Example sensitive data (e.g., user profile data)
original_data = json.dumps({"username": "testuser", "password": "supersecret"})
print(f"Original Data: {original_data}")

# Encrypt the data
encrypted_string = encrypt_data(original_data)
print(f"Encrypted Data: {encrypted_string}")

# Decrypt the data
decrypted_string = decrypt_data(encrypted_string)
print(f"Decrypted Data: {decrypted_string}")

# Verify that the decrypted data matches the original
assert json.loads(original_data) == json.loads(decrypted_string)
print("Encryption and decryption successful!")
```

## Error Handling
- `encrypt_data`: Raises `ValueError` for issues related to invalid input during encryption.
- `decrypt_data`: Raises `cryptography.fernet.InvalidToken` if the provided encrypted data cannot be decrypted (e.g., wrong key, corrupted data, or tampered data). Also raises `ValueError` for other input-related issues.

## Security Considerations
- **Key Storage**: The `encryption.key` file should be protected with appropriate file system permissions to prevent unauthorized access.
- **Key Rotation**: For high-security applications, consider implementing a key rotation strategy.
- **Environment Variables**: For production environments, it's recommended to load the encryption key from a secure environment variable or a secrets management service rather than a file.

## Contributing
When contributing to this module:
- Ensure any changes maintain the integrity and security of the encryption process.
- Avoid introducing new dependencies unless absolutely necessary and well-vetted.
- Follow best practices for cryptographic operations.