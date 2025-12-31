from django.core.management.base import BaseCommand
from apps.ingestion.coordinator import IngestionCoordinator
from apps.ingestion.logger import log_ingestion_start, log_signal_stored


class Command(BaseCommand):
    """
    Ingest signals from various sources.
    """
    help = 'Run Signal Ingestion.'

    def handle(self, *args, **kwargs):
        # log_ingestion_start(run_id, source_count)
        coordinator = IngestionCoordinator()
        coordinator.run()
        # log_ingestion_end(run_id)
