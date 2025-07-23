from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    image = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # New fields for user profile
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    personal_website = Column(String, nullable=True)
    linkedin_profile = Column(String, nullable=True)
    github_profile = Column(String, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    skills = Column(
        Text, nullable=True
    )  # Stored as comma-separated string or JSON string

    # Relationships to new tables
    education = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    experience = relationship(
        "Experience", back_populates="user", cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    job_preferences = relationship(
        "JobPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', google_id='{self.google_id}')>"


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    degree = Column(String, nullable=False)
    university = Column(String, nullable=False)
    field_of_study = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="education")

    def __repr__(self):
        return (
            f"<Education(id={self.id}, user_id={self.user_id}, degree='{self.degree}')>"
        )


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="experience")

    def __repr__(self):
        return f"<Experience(id={self.id}, user_id={self.user_id}, title='{self.title}', company='{self.company}')>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(
        Text, nullable=True
    )  # Stored as comma-separated string or JSON string
    url = Column(String, nullable=True)

    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_size = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    job_titles = Column(
        Text, nullable=True
    )  # Stored as comma-separated string or JSON string
    locations = Column(
        Text, nullable=True
    )  # Stored as comma-separated string or JSON string
    remote = Column(Boolean, default=False)

    user = relationship("User", back_populates="job_preferences")

    def __repr__(self):
        return f"<JobPreference(id={self.id}, user_id={self.user_id})>"


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    proficiency = Column(String, nullable=True)

    user = relationship("User", back_populates="skills")

    def __repr__(self):
        return f"<Skill(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class InAppNotification(Base):
    __tablename__ = "in_app_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    details = Column(Text, nullable=True)  # Store JSON string for additional details
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

    def __repr__(self):
        return f"<InAppNotification(id={self.id}, user_id={self.user_id}, message='{self.message[:20]}...')>"
