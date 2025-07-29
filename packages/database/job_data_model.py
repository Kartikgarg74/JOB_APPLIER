# packages/database/job_data_model.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import uuid
from .models import JobListing


class JobDatabase:
    def __init__(self):
         self.logger = logging.getLogger(__name__)

    def add_job_listing(self, session: Session, job_data: dict):
        try:
            # Check if job already exists by URL
            existing_job = (
                session.query(JobListing).filter_by(url=job_data["url"]).first()
            )
            if existing_job:
                self.logger.info(
                    f"Job with URL {job_data['url']} already exists. Skipping."
                )
                return existing_job

            job = JobListing(
                id=job_data.get("id", str(uuid.uuid4())),
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"],
                requirements=job_data.get("requirements"),
                salary=job_data.get("salary"),
                posting_date=job_data.get("posting_date"),
                url=job_data["url"],
                source=job_data.get("source"),
                date_discovered=datetime.utcnow(),
            )
            session.add(job)
            session.commit()
            self.logger.info(f"Added job: {job.title} at {job.company}")
            return job
        except IntegrityError as e:
            session.rollback()
            self.logger.error(f"Integrity error adding job listing: {e}")
            raise RuntimeError(f"Job listing with this URL already exists: {e}") from e
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error adding job listing: {e}")
            raise RuntimeError(f"Database error adding job listing: {e}") from e


    def get_job_listing(self, session: Session, job_id: str):
        return session.query(JobListing).filter_by(id=job_id).first()


    def get_all_job_listings(self, session: Session):
        return session.query(JobListing).all()


    def update_job_listing(self, session: Session, job_id: str, updated_data: dict):
        try:
            job = session.query(JobListing).filter_by(id=job_id).first()
            if job:
                for key, value in updated_data.items():
                    setattr(job, key, value)
                session.commit()
                self.logger.info(f"Updated job {job.title}")
                return True
            return False

        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error updating job status: {e}")
            raise RuntimeError(f"Database error updating job status: {e}") from e


    def search_job_listings(
        self,
        session: Session,
        query: str = None,
        location: str = None,
        salary_min: float = None,
        posting_date_after: datetime = None,
    ):
        try:
            jobs = session.query(JobListing)
            if query:
                jobs = jobs.filter(
                    JobListing.title.contains(query)
                    | JobListing.description.contains(query)
                )
            if location:
                jobs = jobs.filter(JobListing.location.contains(location))
            if salary_min:
                # This assumes salary is stored as a number or can be parsed.
                # For string salaries, more complex parsing would be needed.
                jobs = jobs.filter(
                    JobListing.salary.contains(str(salary_min))
                )  # Placeholder for actual salary parsing
            if posting_date_after:
                jobs = jobs.filter(JobListing.posting_date >= posting_date_after)
            return jobs.all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error searching job listings: {e}")
            raise RuntimeError(f"Database error searching job listings: {e}") from e


    def delete_job_listing(self, session: Session, job_id: str):
        try:
            job = session.query(JobListing).filter_by(id=job_id).first()
            if job:
                session.delete(job)
                session.commit()
                self.logger.info(f"Deleted job: {job.title}")
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error deleting job listing: {e}")
            raise RuntimeError(f"Database error deleting job listing: {e}") from e
