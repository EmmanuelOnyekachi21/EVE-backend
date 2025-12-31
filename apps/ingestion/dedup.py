from apps.signals.models import Signal
from apps.ingestion.types import NormalizedSignal
from apps.sources.models import Source


class DeduplicationService:
    """
    Deduplication service.

    Responsible for deciding whether an incoming signal
    already exists in the system.
    """

    @staticmethod
    def compute_hash(signal: NormalizedSignal, source: Source) -> str:
        """
        Delegate hash computation to Signal model.
        """
        return Signal.compute_dedup_hash(
            source.id,
            signal.signal_type.value,
            signal.location,
            signal.timestamp
        )
        

    def is_duplicate(self, hash: str) -> bool:
        """
        Check if a signal is a duplicate, i.e checks if signals exist.
        """
        return Signal.objects.filter(dedup_hash=hash).exists()
