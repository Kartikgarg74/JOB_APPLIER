from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    google_id: Optional[str] = None
    image: Optional[str] = None


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    google_id: Optional[str] = None
    image: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    portfolio_url: Optional[str] = None
    personal_website: Optional[str] = None
    linkedin_profile: Optional[str] = None
    github_profile: Optional[str] = None
    years_of_experience: Optional[int] = None
    skills: Optional[list[str]] = None

    class Config:
        from_attributes = True


class GoogleAuthCallback(BaseModel):
    id_token: str
