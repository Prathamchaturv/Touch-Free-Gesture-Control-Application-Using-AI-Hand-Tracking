"""
Module: logger.py
Description: Performance logging utility — creates a file-based logger that
             records gesture recognition events to logs/mmgi_performance.log.
Author: Pratham Chaturvedi
"""

import logging
from pathlib import Path

_perf_logger: logging.Logger | None = None


def get_performance_logger() -> logging.Logger:
    """Return the singleton performance logger, initialising on first call."""
    global _perf_logger
    if _perf_logger is not None:
        return _perf_logger

    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'mmgi_performance.log'

    _perf_logger = logging.getLogger('mmgi.performance')
    _perf_logger.setLevel(logging.INFO)
    _perf_logger.propagate = False

    if not _perf_logger.handlers:
        fh = logging.FileHandler(str(log_file), encoding='utf-8')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ))
        _perf_logger.addHandler(fh)

    return _perf_logger
