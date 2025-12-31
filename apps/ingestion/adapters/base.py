from abc import ABC, abstractmethod
from typing import List
from apps.ingestion.types import RawSignal, NormalizedSignal

class SourceAdapter(ABC):

    @abstractmethod
    def fetch_signals(self) -> List[RawSignal]:
        """
        Fetch raw signals from source.
        """
        pass

    @abstractmethod
    def normalize_signal(self, raw: RawSignal) -> NormalizedSignal:
        """
        Normalize raw signal to a common format.
        """
        pass
