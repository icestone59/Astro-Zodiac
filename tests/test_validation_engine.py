import unittest

from pattern_schema import PatternCandidate, PatternScore
from validation_engine import create_validation_session, validate_pattern
from validation_schema import BehavioralEvidence, QuestionResponse


def candidate(pattern_id="P01", total=5.0):
    return PatternCandidate(
        pattern_id=pattern_id,
        name="Test Pattern",
        life_question="Test?",
        score=PatternScore(
            western=total, uranian=0, context=0, specificity=0,
            signal_count=1, total=total,
        ),
        validation_route=pattern_id,
    )


class ValidationEngineTests(unittest.TestCase):
    def test_high_self_report_can_reach_strong_fit(self):
        responses = [QuestionResponse(question_id=f"P01-Q{i}", value=5) for i in range(1, 6)]
        evidence = [BehavioralEvidence(evidence_id="E1", strength=1.0, source="behavioral_example")]
        result = validate_pattern(candidate(total=8.5), responses, evidence)
        self.assertEqual(result.fit, "strong")
        self.assertEqual(result.status, "validated")
        self.assertGreaterEqual(result.scores.pattern_fit_score, 70)

    def test_disagreement_does_not_force_validation(self):
        responses = [QuestionResponse(question_id=f"P01-Q{i}", value=1) for i in range(1, 6)]
        result = validate_pattern(candidate(total=0), responses, ())
        self.assertEqual(result.fit, "low")
        self.assertEqual(result.status, "not_confirmed")

    def test_reverse_scoring_for_self_efficacy(self):
        responses = [
            QuestionResponse(question_id="P05-Q1", value=1),
            QuestionResponse(question_id="P05-Q2", value=1),
            QuestionResponse(question_id="P05-Q3", value=5),
            QuestionResponse(question_id="P05-Q4", value=5),
            QuestionResponse(question_id="P05-Q5", value=1),
        ]
        result = validate_pattern(candidate(pattern_id="P05", total=7), responses)
        self.assertGreater(result.scores.self_report_score, 25)

    def test_partial_session_is_explored_not_validated(self):
        responses = [QuestionResponse(question_id="P01-Q1", value=5)]
        session = create_validation_session(candidate(total=8), responses=responses)
        self.assertEqual(session.result.status, "explored")
        self.assertEqual(session.result.next_route, "continue_questions")


if __name__ == "__main__":
    unittest.main()
