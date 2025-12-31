from .base import SourceAdapter
from apps.ingestion.types import RawSignal, NormalizedSignal
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from django.contrib.gis.geos import Point
from decouple import config
from typing import List
from math import cos, radians


class MockAdapter(SourceAdapter):
    """
    Mock adapter for testing purposes.
    """
    SOURCE_PLATFORM = 'mock'
    def __init__(self):
        self.faker = Faker()
        self.CENTER_LAT = float(config('CENTER_LAT'))
        self.CENTER_LONG = float(config('CENTER_LONG'))
        self.radius_km = float(config('RADIUS_KM', default=10.0))
        self.max_signal = int(config('MAX_SIGNAL', default=20))
        self.min_signal = int(config('MIN_SIGNAL', default=1))

        self.signal_types = [
            'robbery', 'assault', 'burglary', 'vehicle_theft', 'harassment', 'other'
        ]
    
    def fetch_signals(self) -> List[RawSignal]:
        signals = []
        count = random.randint(self.min_signal, self.max_signal)
        for _ in range(count):
            signals.append(self._generate_signal())
        return signals
    
    def normalize_signal(self, raw_signal: RawSignal) -> NormalizedSignal:
        """
        Converts RawSignal to NormalizedSignal.
        Assumes raw.location is a GeoDjango Point.
        """
        return NormalizedSignal(
            title=raw_signal.title,
            description=raw_signal.description,
            signal_type=raw_signal.signal_type,
            source_identifier=raw_signal.source_name,
            timestamp=raw_signal.published,
            source_platform=self.SOURCE_PLATFORM,
            location=raw_signal.location,
            additional_data={
                'has_photo': raw_signal.has_photo,
                'has_video': raw_signal.has_video,
                'original_link': raw_signal.link,
            }
        )
    
    def _generate_signal(self):
        """
        Generate a single RawSignal.
        """
        signal_type = random.choice(self.signal_types)
        minutes_ago = random.randint(0, 1440)
        occured_at = timezone.now() - timedelta(minutes=minutes_ago)
        title = self.faker.sentence(nb_words=5)
        description = self.faker.text(max_nb_chars=1000)
        link = self.faker.url()

        # location
        lat = self.CENTER_LAT + random.uniform(-self.radius_km, self.radius_km) / 111320
        lon = self.CENTER_LONG + random.uniform(-self.radius_km, self.radius_km) / (111320 * cos(radians(self.CENTER_LAT)))
        location = Point(lon, lat, srid=4326)

        source_name = random.choice([
            "mock:citizen_reporter_1",
            "mock:traffic_monitor",
            "mock:neighborhood_watch"
        ])

        return RawSignal(
            title=f'{signal_type.replace("_", ' ').title()} Reported',
            description=description,
            signal_type=signal_type,
            link=link,
            published=occured_at,
            source_name=source_name,
            location=location,
            has_photo=random.choice([True, False]),
            has_video=random.choice([True, False])
        )



