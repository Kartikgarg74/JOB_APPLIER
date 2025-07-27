import unittest
import os
import sys
import logging

# Add the parent directory to the sys.path to allow imports of modules at the same level
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from packages.agents.learning_agent.learning_agent import LearningAgent, FeatureData

class TestLearningAgent(unittest.TestCase):

    def setUp(self):
        self.agent = LearningAgent()

    def test_initialization(self):
        """Test that the learning agent initializes correctly."""
        self.assertEqual(len(self.agent.application_data), 0)
        self.assertIsNone(self.agent._ml_model)
        self.assertIsNone(self.agent._ml_encoders)

    def test_add_application_result(self):
        """Test adding application results."""
        features = FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC")
        self.agent.add_application_result(features, True)

        self.assertEqual(len(self.agent.application_data), 1)
        self.assertEqual(self.agent.application_data[0]["features"], features)
        self.assertTrue(self.agent.application_data[0]["success"])

    def test_analyze_patterns_empty_data(self):
        """Test pattern analysis with no data."""
        patterns = self.agent.analyze_patterns()
        self.assertEqual(patterns, {})

    def test_analyze_patterns_with_data(self):
        """Test pattern analysis with sample data."""
        # Add test data
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
        self.agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)

        patterns = self.agent.analyze_patterns()

        # Check that patterns are returned
        self.assertIn("skills", patterns)
        self.assertIn("job_type", patterns)
        self.assertIn("company", patterns)
        self.assertIn("location", patterns)

        # Check specific patterns
        self.assertEqual(patterns["skills"]["Python"], 1.0)  # 2/2 successful
        self.assertEqual(patterns["skills"]["Java"], 0.0)    # 0/1 successful
        self.assertEqual(patterns["company"]["Google"], 1.0)  # 2/2 successful
        self.assertEqual(patterns["company"]["Amazon"], 0.0)  # 0/1 successful

    def test_predict_success_probability_no_data(self):
        """Test prediction with no training data."""
        features = FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC")
        probability = self.agent.predict_success_probability(features)
        self.assertEqual(probability, 0.5)  # Default value

    def test_predict_success_probability_with_data(self):
        """Test prediction with training data."""
        # Add training data
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
        self.agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)

        # Test prediction for similar features (should have high probability)
        test_features = FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC")
        probability = self.agent.predict_success_probability(test_features)

        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_adjust_recommendations_no_data(self):
        """Test recommendations with no data."""
        recommendations = self.agent.adjust_recommendations()

        # Should return empty recommendations
        self.assertIn("top_skills", recommendations)
        self.assertIn("top_job_type", recommendations)
        self.assertIn("top_company", recommendations)
        self.assertIn("top_location", recommendations)

    def test_adjust_recommendations_with_data(self):
        """Test recommendations with training data."""
        # Add training data
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
        self.agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)

        recommendations = self.agent.adjust_recommendations()

        self.assertIn("top_skills", recommendations)
        self.assertIn("top_job_type", recommendations)
        self.assertIn("top_company", recommendations)
        self.assertIn("top_location", recommendations)

        # Python should be in top skills (100% success rate)
        self.assertIn("Python", recommendations["top_skills"])

    def test_fit_predictive_model_insufficient_data(self):
        """Test model fitting with insufficient data."""
        # Add only 2 data points (need at least 5)
        self.agent.add_application_result(FeatureData(["Python"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java"], "Full-Time", "Amazon", "Seattle"), False)

        model = self.agent.fit_predictive_model()
        self.assertIsNone(model)

    def test_get_learning_stats_empty(self):
        """Test learning stats with no data."""
        stats = self.agent.get_learning_stats()

        self.assertEqual(stats["total_applications"], 0)
        self.assertEqual(stats["success_rate"], 0.0)
        self.assertFalse(stats["model_trained"])

    def test_get_learning_stats_with_data(self):
        """Test learning stats with data."""
        # Add training data
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
        self.agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)

        stats = self.agent.get_learning_stats()

        self.assertEqual(stats["total_applications"], 3)
        self.assertEqual(stats["successful_applications"], 2)
        self.assertAlmostEqual(stats["success_rate"], 2/3, places=2)
        self.assertFalse(stats["model_trained"])
        self.assertEqual(stats["unique_skills"], 5)  # Python, SQL, Java, AWS, ML
        self.assertEqual(stats["unique_companies"], 2)  # Google, Amazon
        self.assertEqual(stats["unique_locations"], 2)  # NYC, Seattle

    def test_feature_data_creation(self):
        """Test FeatureData dataclass creation."""
        features = FeatureData(
            skills=["Python", "SQL"],
            job_type="Full-Time",
            company="Google",
            location="NYC",
            other={"remote": True}
        )

        self.assertEqual(features.skills, ["Python", "SQL"])
        self.assertEqual(features.job_type, "Full-Time")
        self.assertEqual(features.company, "Google")
        self.assertEqual(features.location, "NYC")
        self.assertEqual(features.other, {"remote": True})

    def test_comprehensive_workflow(self):
        """Test a complete workflow of the learning agent."""
        # Add diverse training data
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
        self.agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)
        self.agent.add_application_result(FeatureData(["JavaScript", "React"], "Contract", "Meta", "Remote"), False)
        self.agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)

        # Analyze patterns
        patterns = self.agent.analyze_patterns()
        self.assertIn("skills", patterns)

        # Fit model (if sklearn is available)
        model = self.agent.fit_predictive_model()
        # Model might be None if sklearn is not available, which is okay

        # Get recommendations
        recommendations = self.agent.adjust_recommendations()
        self.assertIn("top_skills", recommendations)

        # Test prediction
        test_features = FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC")
        probability = self.agent.predict_success_probability(test_features)
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

        # Get stats
        stats = self.agent.get_learning_stats()
        self.assertEqual(stats["total_applications"], 5)
        self.assertEqual(stats["successful_applications"], 3)

if __name__ == '__main__':
    unittest.main()
