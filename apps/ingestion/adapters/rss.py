from .base import SourceAdapter
import feedparser
from typing import List
import random
from datetime import datetime
from apps.ingestion.types import RawSignal, NormalizedSignal
import logging

logger = logging.getLogger(__name__)

class RssAdapter(SourceAdapter):
    """
    RSS adapter for fetching signals from RSS feeds.
    """
    pass
    # def __init__(self, feed_urls: List[str]):
    #     """
    #     Instantiates the RssAdapter with a list of RSS feed URLs.
    #     """
    #     self.feed_urls = feed_urls
    
    # def fetch_signals(self) -> RawSignal:
    #     """
    #     Fetch raw RSS entries and convert to RawSignal.
    #     """
    #     raw_signals = []

    #     for urls in self.feed_urls:
    #         logger.info(f"Fetching RSS feed: {urls}")
    #         feed = feedparser.parse(urls)

    #         # Track how many we get from this specific URL
    #         count_before = len(raw_signals)

    #         # Check if feedparser encountered a structural problem.
    #         if feed.bozo:
    #             logger.warning(f"Feed at {urls} might be malformed: {feed.bozo_exception}")

    #         for entry in feed.entries:
    #             try:
    #                 published = getattr(entry, 'published_parsed', None)
    #                 if published:
    #                     # The '*' unpacks the tuple
    #                     published_dt = datetime(*published[:6])
    #                 else:
    #                     published_dt = None
    #                 raw = RawSignal(
    #                     title=getattr(entry, "title", ""),
    #                     description=getattr(entry, "description", ""),
    #                     link=getattr(entry, "link", ""),
    #                     published=published_dt,
    #                     source_name=urls
    #                 )
    #                 raw_signals.append(raw)
    #             except Exception as e:
    #                 # Get a friendly name for the entry that failed.
    #                 entry_label = getattr(
    #                     entry, 'title',
    #                     getattr(entry, 'link', 'Unknown Title')
    #                 )
    #                 logger.error(
    #                     f"Failed to parse RSS entry: {entry_label} from {urls}",
    #                     exc_info=True
    #                 )
    #                 continue
            
    #         # Track how many we get from this specific URL
    #         count_after = len(raw_signals)
    #         logger.info(f"Fetched {count_after - count_before} signals from {urls}")
    #     return raw_signals
    
    # def normalize_signal(self, raw_signal: RawSignal) -> NormalizedSignal:
    #     """
    #     Normalize a raw RSS entry to a NormalizedSignal.
    #     """
    #     return NormalizedSignal(
    #         signal_type=raw_signal.signal_type if raw_signal.signal_type else 'other',
    #         description=raw_signal.description,
    #         timestamp=raw_signal.published,
    #         location_lat=raw_signal.location_lat if raw_signal.location_lat else None,
    #         location_lon=raw_signal.location_lon if raw_signal.location_lon else None,
    #         source_platform=raw_signal.source_platform,
    #         source_identifier=raw_signal.source_identifier,
    #         additional_data=raw_signal.additional_data
    #     )

# if __name__ == '__main__':
#     feed_urls = [
#     "https://www.vanguardngr.com/feed/",
#     "https://www.punchng.com/feed/",
#     ]
#     adapter = RssAdapter(feed_urls)
#     signals = adapter.fetch_signals()
#     print(f"Fetched {len(signals)} signals")
#     print(signals[0])


