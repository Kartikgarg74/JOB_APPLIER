from sqlalchemy.orm import Session

from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent
from packages.agents.cover_letter_generator.cover_letter_generator_agent import CoverLetterGeneratorAgent
from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.agents.unicorn_agent.unicorn_agent import UnicornAgent

class AgentManager:
    """A centralized manager for instantiating and providing access to various agents."""

    def __init__(self, db: Session):
        self.db = db

    def get_ats_scorer_agent(self) -> ATSScorerAgent:
        """Returns an instance of ATSScorerAgent."""
        return ATSScorerAgent(self.db)

    def get_application_automation_agent(self) -> ApplicationAutomationAgent:
        """Returns an instance of ApplicationAutomationAgent."""
        return ApplicationAutomationAgent(self.db)

    def get_cover_letter_generator_agent(self) -> CoverLetterGeneratorAgent:
        """Returns an instance of CoverLetterGeneratorAgent."""
        return CoverLetterGeneratorAgent(self.db)

    def get_job_matcher_agent(self) -> JobMatcherAgent:
        """Returns an instance of JobMatcherAgent."""
        return JobMatcherAgent(self.db)

    def get_resume_parser_agent(self) -> ResumeParserAgent:
        """Returns an instance of ResumeParserAgent."""
        return ResumeParserAgent(self.db)

    def get_unicorn_agent(self) -> UnicornAgent:
        """Returns an instance of UnicornAgent with its dependencies."""
        return UnicornAgent(
            db=self.db,
            resume_parser_agent=self.get_resume_parser_agent(),
            ats_scorer_agent=self.get_ats_scorer_agent(),
            job_matcher_agent=self.get_job_matcher_agent(),
            application_automation_agent=self.get_application_automation_agent()
        )