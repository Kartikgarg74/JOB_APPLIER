import pytest
from packages.agents.learning_agent.learning_agent import LearningAgent, FeatureData

def test_add_application_result():
    agent = LearningAgent()
    features = FeatureData(["Python"], "Full-Time", "TestCo", "Remote")
    agent.add_application_result(features, True)
    assert len(agent.application_data) == 1

def test_analyze_patterns_empty():
    agent = LearningAgent()
    result = agent.analyze_patterns()
    assert result == {}
