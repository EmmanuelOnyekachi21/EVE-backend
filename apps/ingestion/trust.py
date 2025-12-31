from apps.sources.models import Source
from apps.ingestion.types import NormalizedSignal
from datetime import timedelta
from django.contrib.gis.measure import D



class TrustCalculator:
    """
    Trust calculator.
    """
    BASE_SCORE = 50
    def calculate(self, signal: NormalizedSignal, source: Source) -> int:
        """
        Apply trust scoring rules.
        """
        breakdown = self.get_score_breakdown(signal, source)
        raw_score = sum(breakdown.values())
        return self.clamp(raw_score)
    
    def get_score_breakdown(self, signal: NormalizedSignal, source: Source) -> dict:
        """
        For logging/explainability
        """
        return {
            "base": self.BASE_SCORE,
            "verified_bonus": self._verified_bonus(source),
            "photo_bonus": self._photo_bonus(signal),
            "video_bonus": self._video_bonus(signal),
            "location_bonus": self._location_bonus(signal),
            "cross_validation_bonus": self._cross_validation_bonus(signal, source),
        }

    def _verified_bonus(self, source: Source) -> int:
        """
        Bonus for verified sources.
        """
        if source.verified:
            return 20
        return 0
    
    def _photo_bonus(self, signal: NormalizedSignal) -> int:
        """
        Bonus for photo upload in signal.
        """
        if signal.additional_data.get('has_photo', False):
            return 15
        return 0
    
    def _video_bonus(self, signal: NormalizedSignal) -> int:
        """
        Bonus for video upload in signal.
        """
        if signal.additional_data.get('has_video', False):
            return 15
        return 0
    
    def _location_bonus(self, signal: NormalizedSignal) -> int:
        """
        Bonus for location in signal.
        """
        if signal.location is not None:
            return 10
        return 0
    
    def _cross_validation_bonus(self, signal: NormalizedSignal, source: Source) -> int:
        """
        Bonus for cross validation.
        """
        if not signal.location or not signal.timestamp:
            return 0

        # Importing it here to prevent circular dependency        
        from apps.signals.models import Signal

        if Signal.objects.filter(
            signal_type=signal.signal_type,
            location__distance_lte=(signal.location, D(m=500)),
            occurred_at__range=(
                signal.timestamp - timedelta(minutes=10),
                signal.timestamp + timedelta(minutes=10)
            )
        ).exclude(source=source).exists():
            return 25
        return 0
    
    @staticmethod
    def clamp(score: int, min: int =0, max: int =100) -> int:
        """
        Clamp a value between a minimum and maximum.
        """
        if score < min:
            score = min
        elif score > max:
            score = max
        return score
