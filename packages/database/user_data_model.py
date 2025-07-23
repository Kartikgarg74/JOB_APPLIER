# packages/database/user_data_model.py

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from packages.database.models import (
    Base,
    User,
    Education,
    Experience,
    Project,
    Skill,
    Certification,
    Language,
    Award,
    Publication,
    Patent,
    VolunteerExperience,
    Reference,
    CustomSection,
    JobPreference,
)
from packages.database.config import SessionLocal


class UserDatabase:
    def __init__(self):
        pass

    def add_user(self, session: Session, username: str, email: str, hashed_password: str) -> User:
        try:
            new_user = User(username=username, email=email, password=hashed_password)
            session.add(new_user)
            session.commit()
            return new_user
        except IntegrityError as e:
            session.rollback()
            raise ValueError(
                f"User with username {username} or email {email} already exists."
            ) from e
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Database error occurred while adding user: {e}") from e
        finally:
            pass


    def add_user_google(self, session: Session, username: str, email: str, google_id: str, image_url: Optional[str] = None) -> User:
        try:
            new_user = User(
                username=username, email=email, google_id=google_id, image=image_url
            )
            session.add(new_user)
            session.commit()
            return new_user
        except IntegrityError as e:
            session.rollback()
            raise ValueError(
                f"User with email {email} or Google ID {google_id} already exists."
            ) from e
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while adding Google user: {e}"
            ) from e
        finally:
            pass


    def get_user_by_username(self, session: Session, username: str) -> Optional[User]:
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            pass


    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        try:
            return session.query(User).filter_by(email=email).first()
        finally:
            pass


    def get_user_by_id(self, session: Session, user_id: int) -> Optional[User]:
        try:
            return session.query(User).filter_by(id=user_id).first()
        finally:
            pass


    def get_user_by_google_id(self, session: Session, google_id: str) -> Optional[User]:
        try:
            return session.query(User).filter_by(google_id=google_id).first()
        finally:
            pass


    def update_user_profile(self, session: Session, user_id: int, profile_data: dict) -> Optional[User]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            for key, value in profile_data.items():
                setattr(user, key, value)

            session.commit()
            return user
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while updating user profile: {e}"
            ) from e
        finally:
            pass


    def add_education(self, session: Session, user_id: int, education_data: dict) -> Optional[Education]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            education = Education(**education_data)
            user.education.append(education)
            session.commit()
            return education
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while adding education: {e}"
            ) from e
        finally:
            pass


    def get_education(self, session: Session, user_id: int) -> List[Education]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.education
            return []
        finally:
            pass


    def update_education(self, session: Session, education_id: int, education_data: dict) -> Optional[Education]:
        try:
            education = session.query(Education).filter_by(id=education_id).first()
            if not education:
                return None
            for key, value in education_data.items():
                setattr(education, key, value)
            session.commit()
            return education
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while updating education: {e}"
            ) from e
        finally:
            pass


    def delete_education(self, session: Session, education_id: int) -> bool:
        try:
            education = session.query(Education).filter_by(id=education_id).first()
            if education:
                session.delete(education)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while deleting education: {e}"
            ) from e
        finally:
            pass


    def add_experience(self, session: Session, user_id: int, experience_data: dict) -> Optional[Experience]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            experience = Experience(**experience_data)
            user.experience.append(experience)
            session.commit()
            return experience
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while adding experience: {e}"
            ) from e
        finally:
            pass


    def get_experience(self, session: Session, user_id: int) -> List[Experience]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.experience
            return []
        finally:
            pass


    def update_experience(self, session: Session, experience_id: int, experience_data: dict) -> Optional[Experience]:
        try:
            experience = session.query(Experience).filter_by(id=experience_id).first()
            if not experience:
                return None
            for key, value in experience_data.items():
                setattr(experience, key, value)
            session.commit()
            return experience
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while updating experience: {e}"
            ) from e
        finally:
            pass


    def delete_experience(self, session: Session, experience_id: int) -> bool:
        try:
            experience = session.query(Experience).filter_by(id=experience_id).first()
            if experience:
                session.delete(experience)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while deleting experience: {e}"
            ) from e
        finally:
            pass


    def add_project(self, session: Session, user_id: int, project_data: dict) -> Optional[Project]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            project = Project(**project_data)
            user.projects.append(project)
            session.commit()
            return project
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while adding project: {e}"
            ) from e
        finally:
            pass


    def get_projects(self, session: Session, user_id: int) -> List[Project]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.projects
            return []
        finally:
            pass


    def update_project(self, session: Session, project_id: int, project_data: dict) -> Optional[Project]:
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return None
            for key, value in project_data.items():
                setattr(project, key, value)
            session.commit()
            return project
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while updating project: {e}"
            ) from e
        finally:
            pass


    def delete_project(self, session: Session, project_id: int) -> bool:
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                session.delete(project)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while deleting project: {e}"
            ) from e
        finally:
            pass


    def update_job_preferences(self, session: Session, user_id: int, preferences_data: dict) -> Optional[JobPreference]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            if user.job_preferences:
                # Update existing preferences
                for key, value in preferences_data.items():
                    setattr(user.job_preferences, key, value)
            else:
                # Create new preferences
                preferences = JobPreference(**preferences_data)
                user.job_preferences = preferences

            session.commit()
            return user.job_preferences
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(
                f"Database error occurred while updating job preferences: {e}"
            ) from e
        finally:
            pass

    def get_job_preferences(self, session: Session, user_id: int) -> Optional[JobPreference]:
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.job_preferences
            return None
        finally:
             session.close()
