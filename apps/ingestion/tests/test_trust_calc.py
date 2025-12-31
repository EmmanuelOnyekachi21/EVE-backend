import unittest
from datetime import datetime
from django.contrib.gis.geos import Point
from apps.ingestion.trust import TrustCalculator
from apps.sources.models import Source
from apps.signals.models import Signal
from apps.ingestion.types import NormalizedSignal
from apps.ingestion.trust import TrustCalculator


class TrustCalculatorTestCase(unittest.TestCase):
    """
    Test case for the TrustCalculator class.
    """
    def setUp(self):
        self.trust_verified = Source(verified=True)
        self.trust_not_verified = Source(verified=False)

        # Mock data
        self.signal_all_bonuses = NormalizedSignal(
            title="Test Signal",
            signal_type="robbery",
            description="They just took them out",
            location=Point(0, 0),
            timestamp=datetime.now(),
            source_platform="RSS",
            source_identifier="test_source",
            additional_data={
                "has_photo": True,
                "has_video": True,
            }
        )
        self.signal_no_bonuses = NormalizedSignal(
            title="Test Signal",
            signal_type="robbery",
            description="They just took them out",
            location=None,
            timestamp=datetime.now(),
            source_platform="RSS",
            source_identifier="test_source",
            additional_data={
                "has_photo": False,
                "has_video": False,
            }
        )
        self.signal_location_bonus = NormalizedSignal(
            title="Test Signal",
            signal_type="robbery",
            description="They just took them out",
            location=Point(0, 0),
            timestamp=datetime.now(),
            source_platform="RSS",
            source_identifier="test_source",
            additional_data={
                "has_photo": False,
                "has_video": False,
            }
        )

        self.calculator = TrustCalculator()
    
    def test_all_bonuses(self):
        """
        Test that all bonuses are applied.
        """
        score = self.calculator.calculate(self.signal_all_bonuses, self.trust_verified)
        breakdown = self.calculator.get_score_breakdown(
            self.signal_all_bonuses,
            self.trust_verified
        )
        self.assertEqual(score, 100)  # Clamped
        self.assertEqual(sum(breakdown.values()), 110)  # Raw score
        self.assertEqual(breakdown['verified_bonus'], 20)
        self.assertEqual(breakdown['photo_bonus'], 15)
        self.assertEqual(breakdown['video_bonus'], 15)
        self.assertEqual(breakdown['location_bonus'], 10)
        self.assertEqual(breakdown['cross_validation_bonus'], 0)
        self.assertEqual(breakdown['base'], 50)
    
    def test_only_verified_bonus(self):
        """
        Test that only verified bonus is applied.
        """
        score = self.calculator.calculate(self.signal_no_bonuses, self.trust_verified)
        breakdown = self.calculator.get_score_breakdown(
            self.signal_no_bonuses,
            self.trust_verified
        )
        self.assertEqual(score, 70)  # Clamped
        self.assertEqual(sum(breakdown.values()), 70)  # Raw score
        self.assertEqual(breakdown['verified_bonus'], 20)
        self.assertEqual(breakdown['photo_bonus'], 0)
        self.assertEqual(breakdown['video_bonus'], 0)
        self.assertEqual(breakdown['location_bonus'], 0)
        self.assertEqual(breakdown['cross_validation_bonus'], 0)
        self.assertEqual(breakdown['base'], 50)
    
    def test_no_bonuses(self):
        """
        Test that no bonuses are applied.
        """
        score = self.calculator.calculate(self.signal_no_bonuses, self.trust_not_verified)
        breakdown = self.calculator.get_score_breakdown(
            self.signal_no_bonuses,
            self.trust_not_verified
        )
        self.assertEqual(score, 50)  # Clamped
        self.assertEqual(sum(breakdown.values()), 50)  # Raw score
        self.assertEqual(breakdown['verified_bonus'], 0)
        self.assertEqual(breakdown['photo_bonus'], 0)
        self.assertEqual(breakdown['video_bonus'], 0)
        self.assertEqual(breakdown['location_bonus'], 0)
        self.assertEqual(breakdown['cross_validation_bonus'], 0)
        self.assertEqual(breakdown['base'], 50)
    
    def test_location_bonus(self):
        """
        Test that location bonus is applied.
        """
        score = self.calculator.calculate(self.signal_location_bonus, self.trust_verified)
        breakdown = self.calculator.get_score_breakdown(
            self.signal_location_bonus,
            self.trust_verified
        )
        self.assertEqual(score, 80)  # Clamped
        self.assertEqual(sum(breakdown.values()), 80)  # Raw score
        self.assertEqual(breakdown['verified_bonus'], 20)
        self.assertEqual(breakdown['photo_bonus'], 0)
        self.assertEqual(breakdown['video_bonus'], 0)
        self.assertEqual(breakdown['location_bonus'], 10)
        self.assertEqual(breakdown['cross_validation_bonus'], 0)
        self.assertEqual(breakdown['base'], 50)


if __name__ == "__main__":
    unittest.main()