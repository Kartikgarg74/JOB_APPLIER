import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class FeatureData:
    skills: List[str]
    job_type: str
    company: str
    location: str
    other: Dict[str, Any] = field(default_factory=dict)

class LearningAgent:
    """
    Analyzes application success patterns and adapts job matching criteria using simple ML techniques.
    Tracks features, analyzes success rates, and adjusts recommendations.
    """
    def __init__(self):
        self.application_data: List[Dict[str, Any]] = []  # Stores application features and outcomes
        self._ml_model = None
        self._ml_encoders = None
        logger.info("LearningAgent initialized.")

    def add_application_result(self, features: FeatureData, success: bool) -> None:
        """Add a new application result for learning."""
        self.application_data.append({"features": features, "success": success})
        logger.info(f"Added application result: success={success}, features={features}")

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in application data and return success rates by feature."""
        if not self.application_data:
            logger.warning("No application data to analyze.")
            return {}
        feature_success = {"skills": {}, "job_type": {}, "company": {}, "location": {}}
        feature_total = {"skills": {}, "job_type": {}, "company": {}, "location": {}}
        for entry in self.application_data:
            features: FeatureData = entry["features"]
            success: bool = entry["success"]
            # Skills
            for skill in features.skills:
                feature_total["skills"].setdefault(skill, 0)
                feature_success["skills"].setdefault(skill, 0)
                feature_total["skills"][skill] += 1
                if success:
                    feature_success["skills"][skill] += 1
            # Job type
            jt = features.job_type
            feature_total["job_type"].setdefault(jt, 0)
            feature_success["job_type"].setdefault(jt, 0)
            feature_total["job_type"][jt] += 1
            if success:
                feature_success["job_type"][jt] += 1
            # Company
            comp = features.company
            feature_total["company"].setdefault(comp, 0)
            feature_success["company"].setdefault(comp, 0)
            feature_total["company"][comp] += 1
            if success:
                feature_success["company"][comp] += 1
            # Location
            loc = features.location
            feature_total["location"].setdefault(loc, 0)
            feature_success["location"].setdefault(loc, 0)
            feature_total["location"][loc] += 1
            if success:
                feature_success["location"][loc] += 1
        # Calculate success rates
        success_rates = {cat: {} for cat in feature_success}
        for cat in feature_success:
            for feat, count in feature_total[cat].items():
                if count > 0:
                    success_rates[cat][feat] = feature_success[cat][feat] / count
        logger.info(f"Success rates by feature: {success_rates}")
        return success_rates

    def predict_success_probability(self, features: FeatureData) -> float:
        """
        Predict the probability of success for a given set of features.

        Args:
            features: FeatureData object containing application features.

        Returns:
            Probability of success (0.0 to 1.0).
        """
        if not self.application_data:
            logger.warning("No application data available for prediction.")
            return 0.5  # Default to 50% if no data

        # Try ML model first if available
        if self._ml_model is not None and self._ml_encoders is not None:
            try:
                return self._predict_with_ml_model(features)
            except Exception as e:
                logger.warning(f"ML model prediction failed: {e}")

        # Fallback to success rate analysis
        return self._predict_with_success_rates(features)

    def _predict_with_ml_model(self, features: FeatureData) -> float:
        """Predict using trained ML model."""
        try:
            from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
            import numpy as np

            # Encode features using trained encoders
            skills_encoded = self._ml_encoders["mlb"].transform([features.skills])
            job_type_encoded = self._ml_encoders["le_job_type"].transform([features.job_type]).reshape(1, -1)
            company_encoded = self._ml_encoders["le_company"].transform([features.company]).reshape(1, -1)
            location_encoded = self._ml_encoders["le_location"].transform([features.location]).reshape(1, -1)

            # Concatenate features
            X = np.hstack([skills_encoded, job_type_encoded, company_encoded, location_encoded])

            # Predict probability
            prob = self._ml_model.predict_proba(X)[0][1]  # Probability of success
            return float(prob)
        except Exception as e:
            logger.error(f"Error in ML model prediction: {e}")
            return 0.5

    def _predict_with_success_rates(self, features: FeatureData) -> float:
        """Predict using success rate analysis."""
        rates = self.analyze_patterns()

        # Calculate average success rate for the given features
        feature_scores = []

        # Skills score
        skill_scores = [rates.get("skills", {}).get(skill, 0.5) for skill in features.skills]
        if skill_scores:
            feature_scores.append(sum(skill_scores) / len(skill_scores))

        # Job type score
        job_type_score = rates.get("job_type", {}).get(features.job_type, 0.5)
        feature_scores.append(job_type_score)

        # Company score
        company_score = rates.get("company", {}).get(features.company, 0.5)
        feature_scores.append(company_score)

        # Location score
        location_score = rates.get("location", {}).get(features.location, 0.5)
        feature_scores.append(location_score)

        # Return average score
        return sum(feature_scores) / len(feature_scores) if feature_scores else 0.5

    def adjust_recommendations(self) -> Dict[str, Any]:
        """Adjust job matching criteria based on learned patterns or model predictions."""
        # Try to use ML model if available
        if self._ml_model is not None and self._ml_encoders is not None:
            try:
                # Recommend top skills/job types/companies/locations with highest model coefficients
                model = self._ml_model
                enc = self._ml_encoders
                coef = model.coef_[0]
                # Get top skills
                skill_coefs = coef[:len(enc['mlb'].classes_)]
                top_skill_indices = skill_coefs.argsort()[-3:][::-1]
                top_skills = [enc['mlb'].classes_[i] for i in top_skill_indices]
                # Get top job type
                jt_start = len(enc['mlb'].classes_)
                jt_end = jt_start + len(enc['le_job_type'].classes_)
                jt_coefs = coef[jt_start:jt_end]
                top_jt = enc['le_job_type'].classes_[jt_coefs.argmax()]
                # Get top company
                comp_start = jt_end
                comp_end = comp_start + len(enc['le_company'].classes_)
                comp_coefs = coef[comp_start:comp_end]
                top_comp = enc['le_company'].classes_[comp_coefs.argmax()]
                # Get top location
                loc_start = comp_end
                loc_end = loc_start + len(enc['le_location'].classes_)
                loc_coefs = coef[loc_start:loc_end]
                top_loc = enc['le_location'].classes_[loc_coefs.argmax()]
                recommendations = {
                    "top_skills": top_skills,
                    "top_job_type": top_jt,
                    "top_company": top_comp,
                    "top_location": top_loc
                }
                logger.info(f"Adjusted recommendations (ML): {recommendations}")
                return recommendations
            except Exception as e:
                logger.warning(f"ML model recommendation failed: {e}")

        # Fallback: use success rates
        rates = self.analyze_patterns()
        recommendations = {
            "top_skills": sorted(rates.get("skills", {}), key=lambda k: rates["skills"][k], reverse=True)[:3],
            "top_job_type": max(rates.get("job_type", {}), key=lambda k: rates["job_type"][k], default=None),
            "top_company": max(rates.get("company", {}), key=lambda k: rates["company"][k], default=None),
            "top_location": max(rates.get("location", {}), key=lambda k: rates["location"][k], default=None)
        }
        logger.info(f"Adjusted recommendations (success rates): {recommendations}")
        return recommendations

    def fit_predictive_model(self) -> Optional[Any]:
        """Fit a simple logistic regression model to predict success. Returns the model or None if not enough data or sklearn not available."""
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
            import numpy as np
        except ImportError:
            logger.warning("scikit-learn or numpy not installed. Skipping ML model.")
            return None
        if len(self.application_data) < 5:
            logger.warning("Not enough data to fit a model.")
            return None
        # Prepare features and labels
        X_skills = [entry["features"].skills for entry in self.application_data]
        X_job_type = [entry["features"].job_type for entry in self.application_data]
        X_company = [entry["features"].company for entry in self.application_data]
        X_location = [entry["features"].location for entry in self.application_data]
        y = [1 if entry["success"] else 0 for entry in self.application_data]
        # Encode features
        mlb = MultiLabelBinarizer()
        skills_encoded = mlb.fit_transform(X_skills)
        le_job_type = LabelEncoder()
        job_type_encoded = le_job_type.fit_transform(X_job_type).reshape(-1, 1)
        le_company = LabelEncoder()
        company_encoded = le_company.fit_transform(X_company).reshape(-1, 1)
        le_location = LabelEncoder()
        location_encoded = le_location.fit_transform(X_location).reshape(-1, 1)
        # Concatenate all features
        X = np.hstack([skills_encoded, job_type_encoded, company_encoded, location_encoded])
        # Fit model
        model = LogisticRegression(max_iter=100, solver='liblinear')
        model.fit(X, y)
        logger.info("Fitted logistic regression model for application success prediction.")
        self._ml_model = model
        self._ml_encoders = {
            "mlb": mlb,
            "le_job_type": le_job_type,
            "le_company": le_company,
            "le_location": le_location
        }
        return model

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning agent's data and performance."""
        if not self.application_data:
            return {"total_applications": 0, "success_rate": 0.0, "model_trained": False}

        total_applications = len(self.application_data)
        successful_applications = sum(1 for entry in self.application_data if entry["success"])
        success_rate = successful_applications / total_applications

        return {
            "total_applications": total_applications,
            "successful_applications": successful_applications,
            "success_rate": success_rate,
            "model_trained": self._ml_model is not None,
            "unique_skills": len(set(skill for entry in self.application_data for skill in entry["features"].skills)),
            "unique_companies": len(set(entry["features"].company for entry in self.application_data)),
            "unique_locations": len(set(entry["features"].location for entry in self.application_data))
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = LearningAgent()
    # Example data
    agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)
    agent.add_application_result(FeatureData(["Java", "AWS"], "Full-Time", "Amazon", "Seattle"), False)
    agent.add_application_result(FeatureData(["Python", "ML"], "Internship", "Google", "NYC"), True)
    agent.add_application_result(FeatureData(["JavaScript", "React"], "Contract", "Meta", "Remote"), False)
    agent.add_application_result(FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC"), True)

    # Analyze patterns
    patterns = agent.analyze_patterns()
    print(f"Patterns: {patterns}")

    # Fit model
    agent.fit_predictive_model()

    # Test prediction
    test_features = FeatureData(["Python", "SQL"], "Full-Time", "Google", "NYC")
    probability = agent.predict_success_probability(test_features)
    print(f"Success probability for test features: {probability:.2f}")

    # Adjust recommendations
    recs = agent.adjust_recommendations()
    print(f"Recommended features: {recs}")

    # Get stats
    stats = agent.get_learning_stats()
    print(f"Learning stats: {stats}")
