"""Generate sessions and pageviews."""
import random
from datetime import timedelta, datetime
from typing import List, Dict, Any

from config.settings import *
from src.ids import gen
from src.utils import set_seed, random_datetime_in_range, iso_format, weighted_choice


def generate_sessions(customers: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Generate sessions with bots/noisy sessions."""
    sessions = []
    set_seed(SEED + 3)
    
    data_start_dt = datetime.strptime(DATA_START, "%Y-%m-%d")
    data_end_dt = datetime.strptime(DATA_END, "%Y-%m-%d")
    
    for i in range(n):
        customer = random.choice(customers)
        # Sparse users get fewer sessions conceptually, but we still generate
        if customer["is_sparse"] and random.random() < 0.7:
            continue  # skip some for sparse effect
        if len(sessions) >= n:
            break
            
        session_start = random_datetime_in_range(data_start_dt, data_end_dt - timedelta(hours=2))
        session_duration = random.randint(60, 3600)  # 1 min to 1 hour
        session_end = session_start + timedelta(seconds=session_duration)
        
        is_bot = customer["is_bot_flag_candidate"] or random.random() < 0.01
        is_test_candidate = random.random() < 0.05  # 5% candidates for test leakage
        
        session = {
            "session_id": gen.session("2026"),
            "customer_id": customer["customer_id"],
            "session_start": iso_format(session_start),
            "session_end": iso_format(session_end),
            "device_type": weighted_choice(DEVICE_TYPES, [0.4, 0.5, 0.1]) if not is_bot else random.choice(DEVICE_TYPES),
            "channel": weighted_choice(CHANNELS, [0.4, 0.2, 0.25, 0.1, 0.05]),
            "is_bot": is_bot,
            "is_test_candidate": is_test_candidate,
            "created_at": iso_format(session_start)
        }
        sessions.append(session)
    
    return sessions


def generate_pageviews(sessions: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate pageview events."""
    pageviews = []
    set_seed(SEED + 4)
    
    for session in sessions:
        session_start = datetime.strptime(session["session_start"].replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
        session_end = datetime.strptime(session["session_end"].replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
        
        # Number of pageviews per session
        num_views = random.randint(1, 15) if not session["is_bot"] else random.randint(5, 30)
        
        for idx in range(1, num_views + 1):
            view_time = random_datetime_in_range(session_start, session_end)
            page_type = weighted_choice(PAGE_TYPES, [0.2, 0.15, 0.4, 0.15, 0.07, 0.03])
            
            product_id = None
            if page_type in ["product", "category"] and random.random() < 0.8:
                product_id = random.choice(products)["product_id"]
            
            pv = {
                "event_id": gen.event(session["session_id"], idx),
                "session_id": session["session_id"],
                "customer_id": session["customer_id"],
                "product_id": product_id,
                "page_type": page_type,
                "view_time": iso_format(view_time),
                "referrer": weighted_choice(REFERRERS, [0.3, 0.2, 0.15, 0.1, 0.1, 0.15]),
                "created_at": iso_format(view_time)
            }
            pageviews.append(pv)
    
    return pageviews
