# Config Package

## Purpose
This package centralizes configuration management for the JobApplierAgent monorepo. It handles loading application-wide settings and user-specific profiles, ensuring that configurations are consistently accessed and managed across different modules and agents.

## Dependencies
This package has no internal dependencies within the monorepo. It primarily relies on Python's built-in `json` and `os` modules.

## Key Components
- `settings.py`: Manages application-wide settings, providing a `Settings` class and a `load_settings` function to load configurations from `settings.json`.
- `settings.json`: Stores default application settings in JSON format.
- `user_profile.py`: Handles loading and managing user-specific data.
- `user_profile.json`: Stores example user data for testing and customization.

## Usage Examples
Configuration settings and user profiles can be loaded by any part of the application that requires them.

Example of loading settings and user profile in `main.py`:
```python
from packages.config.settings import load_settings
from packages.config.user_profile import load_user_profile

app_settings = load_settings()
user_config = load_user_profile()

print(f"Log Level: {app_settings['LOG_LEVEL']}")
print(f"Preferred Role: {user_config['preferred_job_roles'][0]}")
```

## API Reference
Refer to `settings.py` and `user_profile.py` for detailed function signatures and documentation.

## Development Setup
No specific setup is required for this package beyond the general monorepo setup. Ensure that `user_profile.json` is correctly configured for local development.

## Testing
Tests for configuration loading should ensure that settings are loaded correctly from various sources (e.g., environment variables, JSON files) and that default values are applied when necessary.

## Contributing
Refer to the main `README.md` in the monorepo root for general contribution guidelines.