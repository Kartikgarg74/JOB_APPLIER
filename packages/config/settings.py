import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging




class Settings(BaseSettings):
    """
    [CONTEXT] Manages application settings using Pydantic Settings.
    [PURPOSE] Provides a centralized, type-safe, and flexible way to load application settings
              from various sources (environment variables, .env files, JSON).
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "settings.json"),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields not defined in the model
    )

    LOG_LEVEL: str = "INFO"
    OUTPUT_DIR: str = Field(
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output"
        ),
        description="Directory for application output files",
    )
    CONFIG_DIR: str = Field(
        default=os.path.dirname(__file__),
        description="Directory for configuration files",
    )
    USER_PROFILE_PATH: str = Field(
        default=os.path.join(os.path.dirname(__file__), "user_profile.json"),
        description="Path to the user profile JSON file",
    )

    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="API key for OpenAI services"
    )
    JOB_BOARD_API_KEY: Optional[str] = Field(
        default=None, description="API key for job board services"
    )

    GEMINI_API_KEY: Optional[str] = Field(
        default=None, description="API key for Gemini services"
    )

    DATABASE_URL: str = Field(
        default="sqlite:///./applications.db", description="Database connection URL"
    )

    CELERY_BROKER_URL: str = Field(
        default=get_redis_url(), description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default=get_redis_url(), description="Celery result backend URL"
    )

    UPSTASH_REDIS_REST_URL: Optional[str] = Field(
        default=None, description="Upstash Redis REST URL"
    )
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = Field(
        default=None, description="Upstash Redis REST Token"
    )

    MAILGUN_API_KEY: Optional[str] = Field(
        default=None, description="API key for Mailgun email service"
    )
    MAILGUN_DOMAIN: Optional[str] = Field(
        default=None, description="Domain for Mailgun email service"
    )

    TWILIO_ACCOUNT_SID: Optional[str] = Field(
        default=None, description="Account SID for Twilio SMS service"
    )
    TWILIO_AUTH_TOKEN: Optional[str] = Field(
        default=None, description="Auth Token for Twilio SMS service"
    )
    TWILIO_PHONE_NUMBER: Optional[str] = Field(
        default=None, description="Twilio phone number for SMS service"
    )

    SECRET_KEY: str = Field(
        default="your-super-secret-key", description="Secret key for JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT encryption")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )


# Instantiate settings to be imported throughout the application
settings = Settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_redis_url():
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    if url and url.startswith("redis://"):
        return url
    logging.warning("UPSTASH_REDIS_REST_URL not set or invalid, using default localhost Redis.")
    return "redis://localhost:6379/0"
