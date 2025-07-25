from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, CheckConstraint
from datetime import datetime
from sqlalchemy.orm import relationship
from .config import Base
from sqlalchemy.ext.hybrid import hybrid_property
from packages.utilities.encryption_utils import encrypt_data, decrypt_data


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    _email = Column("email", String(255), unique=True, index=True, nullable=False)  # PII, confidential
    hashed_password = Column(String(100), nullable=True)  # confidential
    google_id = Column(String(100), unique=True, index=True, nullable=True)  # confidential
    image = Column(String(255), nullable=True)  # public (if user chooses)
    is_active = Column(Boolean, default=True)  # public
    created_at = Column(DateTime, default=datetime.utcnow)  # public

    # 2FA fields
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String(32), nullable=True)  # TOTP secret (base32)
    two_fa_method = Column(String(16), nullable=True)  # e.g., 'totp', 'email', 'sms'

    # Password reset fields
    password_reset_token = Column(String(128), nullable=True)
    password_reset_token_expiry = Column(DateTime, nullable=True)

    # PII fields (encrypted at rest)
    _phone = Column("phone", String(20), nullable=True)  # PII, confidential
    _address = Column("address", String(255), nullable=True)  # PII, confidential
    _portfolio_url = Column("portfolio_url", String(255), nullable=True)  # PII, confidential
    _personal_website = Column("personal_website", String(255), nullable=True)  # public (if user chooses)
    _linkedin_profile = Column("linkedin_profile", String(255), nullable=True)  # public (if user chooses)
    _github_profile = Column("github_profile", String(255), nullable=True)  # public (if user chooses)
    years_of_experience = Column(Integer, CheckConstraint('years_of_experience >= 0 AND years_of_experience <= 100'), nullable=True)  # public
    skills = Column(
        Text, nullable=True
    )  # public
    profile_visibility = Column(String(20), default="public")  # public, private, connections-only
    show_email = Column(Boolean, default=False)  # user privacy control for email visibility

    # Onboarding state
    onboarding_complete = Column(Boolean, default=False)
    onboarding_step = Column(String(50), nullable=True)

    # Hybrid properties for transparent encryption/decryption
    @hybrid_property
    def email(self):
        return decrypt_data(self._email) if self._email else None

    @email.setter
    def email(self, value):
        self._email = encrypt_data(value) if value else None

    @hybrid_property
    def phone(self):
        return decrypt_data(self._phone) if self._phone else None

    @phone.setter
    def phone(self, value):
        self._phone = encrypt_data(value) if value else None

    @hybrid_property
    def address(self):
        return decrypt_data(self._address) if self._address else None

    @address.setter
    def address(self, value):
        self._address = encrypt_data(value) if value else None

    @hybrid_property
    def portfolio_url(self):
        return decrypt_data(self._portfolio_url) if self._portfolio_url else None

    @portfolio_url.setter
    def portfolio_url(self, value):
        self._portfolio_url = encrypt_data(value) if value else None

    @hybrid_property
    def personal_website(self):
        return decrypt_data(self._personal_website) if self._personal_website else None

    @personal_website.setter
    def personal_website(self, value):
        self._personal_website = encrypt_data(value) if value else None

    @hybrid_property
    def linkedin_profile(self):
        return decrypt_data(self._linkedin_profile) if self._linkedin_profile else None

    @linkedin_profile.setter
    def linkedin_profile(self, value):
        self._linkedin_profile = encrypt_data(value) if value else None

    @hybrid_property
    def github_profile(self):
        return decrypt_data(self._github_profile) if self._github_profile else None

    @github_profile.setter
    def github_profile(self, value):
        self._github_profile = encrypt_data(value) if value else None

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

    __table_args__ = (
        CheckConstraint("char_length(username) >= 3", name="ck_user_username_minlen"),
        CheckConstraint("char_length(email) > 3", name="ck_user_email_minlen"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', google_id='{self.google_id}')>"


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # confidential
    degree = Column(String(100), nullable=False)  # PII, confidential
    university = Column(String(100), nullable=False)  # PII, confidential
    field_of_study = Column(String(100), nullable=False)  # PII, confidential
    start_date = Column(DateTime, nullable=False)  # PII, confidential
    end_date = Column(DateTime, nullable=True)  # PII, confidential
    description = Column(Text, nullable=True)  # public

    user = relationship("User", back_populates="education")

    def __repr__(self):
        return (
            f"<Education(id={self.id}, user_id={self.user_id}, degree='{self.degree}')>"
        )


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # confidential
    title = Column(String(100), nullable=False)  # PII, confidential
    company = Column(String(100), nullable=False)  # PII, confidential
    location = Column(String(100), nullable=True)  # PII, confidential
    start_date = Column(DateTime, nullable=False)  # PII, confidential
    end_date = Column(DateTime, nullable=True)  # PII, confidential
    description = Column(Text, nullable=True)  # public

    user = relationship("User", back_populates="experience")

    def __repr__(self):
        return f"<Experience(id={self.id}, user_id={self.user_id}, title='{self.title}', company='{self.company}')>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # confidential
    name = Column(String(100), nullable=False)  # PII, confidential (if not public)
    description = Column(Text, nullable=True)  # public
    technologies = Column(
        Text, nullable=True
    )  # public
    url = Column(String(255), nullable=True)  # PII, confidential (if not public)

    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)  # confidential
    company_size = Column(String(50), nullable=True)  # public
    industry = Column(String(100), nullable=True)  # public
    job_titles = Column(
        Text, nullable=True
    )  # PII, confidential (if user entered)
    locations = Column(
        Text, nullable=True
    )  # PII, confidential
    remote = Column(Boolean, default=False)  # public
    job_type = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    notifications = Column(Boolean, default=True)

    user = relationship("User", back_populates="job_preferences")

    def __repr__(self):
        return f"<JobPreference(id={self.id}, user_id={self.user_id})>"


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # confidential
    name = Column(String(100), nullable=False)  # PII, confidential (if rare/unique)
    proficiency = Column(String(50), nullable=True)  # public

    user = relationship("User", back_populates="skills")

    def __repr__(self):
        return f"<Skill(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class InAppNotification(Base):
    __tablename__ = "in_app_notifications"

    id = Column(Integer, primary_key=True)  # public
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # confidential
    message = Column(String(255), nullable=False)  # PII, confidential (if message contains user data)
    details = Column(Text, nullable=True)  # PII, confidential (if details contain user data)
    is_read = Column(Boolean, default=False)  # public
    created_at = Column(DateTime, default=datetime.utcnow)  # public

    user = relationship("User")

    def __repr__(self):
        return f"<InAppNotification(id={self.id}, user_id={self.user_id}, message='{self.message[:20]}...')>"


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    action = Column(String, nullable=False)
    table_name = Column(String, index=True)
    row_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON)


class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    filename = Column(String(255), index=True, nullable=False)
    storage_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_encrypted = Column(Boolean, default=False)
    is_compressed = Column(Boolean, default=False)
    file_metadata = Column(JSON, nullable=True)
