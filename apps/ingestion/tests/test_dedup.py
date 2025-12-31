from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Point
from apps.ingestion.dedup import DeduplicationService
from apps.ingestion.types import NormalizedSignal, SignalType
from apps.signals.models import Signal
from apps.sources.models import Source


class DeduplicationServiceTestCase(TestCase):
    """
    Test case for the DeduplicationService class.
    """
    def setUp(self):
        self.source = Source.objects.create(
            platform="test_platform",
            external_identifier="test_id",
            verified=True
        )
        self.now = timezone.now()
        self.location = Point(12.34567, 7.89012)
        
        self.signal_data = NormalizedSignal(
            title="Test Signal",
            signal_type=SignalType.ROBBERY,
            description="Test Description",
            timestamp=self.now,
            location=self.location,
            source_platform="RSS",
            source_identifier="test_source"
        )
        self.service = DeduplicationService()

    def test_compute_hash(self):
        """
        Test that compute_hash returns a valid SHA256 hash.
        """
        hash_val = self.service.compute_hash(self.signal_data, self.source)
        self.assertTrue(isinstance(hash_val, str))
        self.assertEqual(len(hash_val), 64)  # SHA256 length

    def test_is_duplicate_false(self):
        """
        Test that is_duplicate returns False when no signal exists.
        """
        hash_val = self.service.compute_hash(self.signal_data, self.source)
        self.assertFalse(self.service.is_duplicate(hash_val))

    def test_is_duplicate_true(self):
        """
        Test that is_duplicate returns True when a signal with the same hash exists.
        """
        hash_val = self.service.compute_hash(self.signal_data, self.source)
        
        # Create a signal in the database
        Signal.objects.create(
            content="Test Signal",
            signal_type=SignalType.ROBBERY.value,
            location=self.location,
            occurred_at=self.now,
            source=self.source,
            dedup_hash=hash_val
        )
        
        self.assertTrue(self.service.is_duplicate(hash_val))

    def test_hash_consistency(self):
        """
        Test that same input produces same hash.
        """
        hash1 = self.service.compute_hash(self.signal_data, self.source)
        hash2 = self.service.compute_hash(self.signal_data, self.source)
        self.assertEqual(hash1, hash2)
