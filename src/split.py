"""Chronological train/test split to prevent leakage."""
import random
from datetime import datetime
from typing import List, Dict, Any

from config.settings import *


def chronological_split(sessions: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> tuple:
    """Split data chronologically by session time to prevent leakage."""
    # Sort sessions by start time (ISO strings sort chronologically)
    sorted_sessions = sorted(sessions, key=lambda x: x["session_start"])
    
    # 80/20 split chronologically
    split_idx = int(len(sorted_sessions) * 0.8)
    train_session_ids = set(s["session_id"] for s in sorted_sessions[:split_idx])
    test_session_ids = set(s["session_id"] for s in sorted_sessions[split_idx:])
    
    # Assign split to sessions
    for s in sessions:
        if s["session_id"] in train_session_ids:
            s["split"] = "train"
        else:
            s["split"] = "test"
    
    # Assign split to recommendations based on their session
    for rec in recommendations:
        if rec["session_id"] in train_session_ids:
            rec["split"] = "train"
        elif rec["session_id"] in test_session_ids:
            rec["split"] = "test"
        else:
            # Default
            rec["split"] = random.choice(["train", "test"])
    
    return train_session_ids, test_session_ids
