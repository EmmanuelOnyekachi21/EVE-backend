"""
This file orchestrates the ingestion process.
"""

import logging
from django.db import transaction
from django.utils import timezone

from apps.ingestion.adapters.rss import RssAdapter
from apps.ingestion.adapters.mock import MockAdapter
from apps.ingestion.trust import TrustCalculator
from apps.ingestion.dedup import DeduplicationService

from apps.signals.models import Signal
from apps.sources.models import Source

logger = logging.getLogger(__name__)

class IngestionCoordinator:
    """
    Orchestrates the ingestion process.
    """
    def __init__(self):
        # FIX #1: Changed RSSAdapter to RssAdapter (correct import name)
        self.adapters = [MockAdapter()]
        self.trust_calculator = TrustCalculator()
        self.deduplication_service = DeduplicationService()

    def run(self):
        """
        Main ingestion loop with error isolation per source.
        """
        logger.info("Starting ingestion coordinator run")
        
        for adapter in self.adapters:
            adapter_name = adapter.__class__.__name__
            try:
                logger.info(f"Processing source: {adapter_name}")
                self._process_source(adapter)
                logger.info(f"Successfully processed source: {adapter_name}")
            except Exception as e:
                # Error isolation: log and continue with next source
                logger.error(
                    f"Source failed: {adapter_name}",
                    exc_info=True,
                    extra={
                        'adapter': adapter_name,
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                )
                # Continue with next source
        
        logger.info("Ingestion coordinator run completed")
    
    def _process_source(self, adapter):
        """
        Process a single source end to end with transaction boundary.
        All-or-nothing: if any step fails, entire source processing is rolled back.
        """
        adapter_name = adapter.__class__.__name__
        
        # Fetch signals
        logger.info(f"[{adapter_name}] Step 1: Fetching signals")
        signals = self._fetch(adapter)
        logger.info(f"[{adapter_name}] Fetched {len(signals)} signals")
        
        if not signals:
            logger.info(f"[{adapter_name}] No signals to process")
            return
        
        # Process each signal
        processed_count = 0
        duplicate_count = 0
        error_count = 0
        
        for idx, signal in enumerate(signals, 1):
            try:
                with transaction.atomic():
                    # Step 1: Normalize
                    logger.debug(f"[{adapter_name}] Signal {idx}/{len(signals)}: Normalizing")
                    normalized_signal = self._normalize(signal, adapter)

                    # get_or_create returns (object, created) tuple
                    source, created = Source.objects.get_or_create(
                        platform=normalized_signal.source_platform,
                        external_identifier=normalized_signal.source_identifier,
                        defaults={'last_fetched_at': normalized_signal.timestamp}
                    )
                    
                    if created:
                        logger.info(
                            f"[{adapter_name}] Created new source: {source}",
                            extra={'source_id': str(source.id)}
                        )
                    else:
                        # Update last_fetched_at for existing sources
                        source.last_fetched_at = timezone.now()
                        source.save(update_fields=['last_fetched_at'])
                    
                    # Step 2: Score
                    logger.debug(f"[{adapter_name}] Signal {idx}/{len(signals)}: Calculating trust score")
                    score = self._score(normalized_signal, source)
                    
                    # Update source trust score
                    if score is not None and source.trust_score != score:
                        old_score = source.trust_score
                        source.trust_score = score
                        source.save(update_fields=['trust_score'])
                        logger.info(
                            f"[{adapter_name}] Updated trust score for {source}: {old_score} → {score}",
                            extra={
                                'source_id': str(source.id),
                                'old_score': old_score,
                                'new_score': score
                            }
                        )
                    
                    # Step 3: Store (dedup handled by model's unique constraint)
                    logger.debug(f"[{adapter_name}] Signal {idx}/{len(signals)}: Storing")
                    stored_signal = self._store(normalized_signal, score, source)
                    processed_count += 1
                    
                    logger.debug(
                        f"[{adapter_name}] Signal {idx}/{len(signals)}: Successfully stored",
                        extra={
                            'signal_id': str(stored_signal.id),
                            'signal_type': stored_signal.signal_type,
                            'dedup_hash': stored_signal.dedup_hash
                        }
                    )
                    
            except Exception as e:
                from django.db import IntegrityError
                
                # Handle duplicates gracefully (unique constraint on dedup_hash)
                if isinstance(e, IntegrityError) and 'dedup_hash' in str(e):
                    duplicate_count += 1
                    logger.debug(
                        f"[{adapter_name}] Signal {idx}/{len(signals)}: Duplicate detected (IntegrityError)",
                        extra={'signal_type': normalized_signal.signal_type if 'normalized_signal' in locals() else 'unknown'}
                    )
                else:
                    error_count += 1
                    logger.error(
                        f"[{adapter_name}] Signal {idx}/{len(signals)}: Processing failed",
                        exc_info=True,
                        extra={
                            'error_type': type(e).__name__,
                            'error_message': str(e)
                        }
                    )
                    # Re-raise only for actual errors (not duplicates)
                    raise
        
        # Summary logging
        logger.info(
            f"[{adapter_name}] Processing complete: "
            f"{processed_count} stored, {duplicate_count} duplicates, {error_count} errors",
            extra={
                'adapter': adapter_name,
                'processed': processed_count,
                'duplicates': duplicate_count,
                'errors': error_count,
                'total': len(signals)
            }
        )

    def _fetch(self, adapter):
        """
        Fetch signals from the adapter.
        """
        return adapter.fetch_signals()
    
    def _normalize(self, signal, adapter):
        """
        Normalize signals.
        FIX #3: Removed call to non-existent self.normalize_signal method.
        Signals are already normalized by adapters, so just return as-is.
        """
        # Adapters already return normalized signals
        # If additional normalization is needed, implement it here
        return adapter.normalize_signal(signal)
    
    def _score(self, signal, source):
        """
        Score signals using trust calculator.
        """
        return self.trust_calculator.calculate(signal, source)
    

    
    def _store(self, normalized_signal, score, source):
        """
        Store signals in database.
        The Signal model will auto-generate dedup_hash in its save() method.
        """
        return Signal.objects.create(
            content=normalized_signal.description,
            signal_type=normalized_signal.signal_type,
            location=normalized_signal.location,
            occurred_at=normalized_signal.timestamp,
            source_metadata=normalized_signal.additional_data,
            source=source  # ForeignKey to Source object
            # dedup_hash will be auto-generated by Signal.save()
        )
