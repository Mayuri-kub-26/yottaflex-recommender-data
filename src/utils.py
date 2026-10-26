"""Utility functions for data generation."""
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Any


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)


def random_date_between(start_date: str, end_date: str) -> datetime:
    """Generate random datetime between start and end dates."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)


def random_datetime_in_range(start_dt: datetime, end_dt: datetime) -> datetime:
    """Generate random datetime between two datetimes."""
    delta_seconds = int((end_dt - start_dt).total_seconds())
    if delta_seconds < 0:
        return start_dt
    random_seconds = random.randint(0, delta_seconds)
    return start_dt + timedelta(seconds=random_seconds)


def iso_format(dt: datetime) -> str:
    """Format datetime as ISO8601 string."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def date_format(dt: datetime) -> str:
    """Format date as YYYY-MM-DD."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)


def weighted_choice(items: List[Any], weights: List[float]) -> Any:
    """Choose item based on weights."""
    return random.choices(items, weights=weights, k=1)[0]


def compute_checksum(data_str: str) -> str:
    """Compute SHA256 checksum."""
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()


def round_money(amount: float) -> float:
    """Round to 2 decimal places for money."""
    return round(float(amount), 2)
