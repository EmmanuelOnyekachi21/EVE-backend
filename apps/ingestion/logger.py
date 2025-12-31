"""
This module provides logging functionality for the ingestion process.
"""

import json
import logging
import datetime

logger = logging.getLogger('ingestion')

def log_ingestion_start(run_id, source_count):
    """
    Log Ingestion Start
    """
    logger.info(json.dumps({
        'event': 'ingestion_start',
        'run_id': run_id,
        'source_count': source_count,
        'timestamp': datetime.datetime.now().isoformat()
    }))

def log_signal_stored(run_id, signal_id, trust_score):
    """
    Log Signal Stored
    """
    logger.info(json.dumps({
        'event': 'signal_stored',
        'run_id': run_id,
        'signal_id': signal_id,
        'trust_score': trust_score,
        'timestamp': datetime.datetime.now().isoformat()
    }))
