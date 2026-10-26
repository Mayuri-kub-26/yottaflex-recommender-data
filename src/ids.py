"""ID generators following exact conventions specified."""
from typing import Iterator


class IDGenerator:
    def __init__(self):
        self._counters = {}
    
    def _next(self, prefix: str, width: int, year: str = None) -> str:
        key = (prefix, width, year)
        if key not in self._counters:
            self._counters[key] = 0
        self._counters[key] += 1
        num = str(self._counters[key]).zfill(width)
        if year:
            return f"{prefix}-{year}-{num}"
        return f"{prefix}-{num}"
    
    def customer(self) -> str:
        return self._next("CUS", 6)
    
    def category(self) -> str:
        return self._next("CAT", 4)
    
    def product(self) -> str:
        return self._next("SKU", 6)
    
    def session(self, year: str = "2026") -> str:
        return self._next("SES", 6, year)
    
    def event(self, session_id: str, idx: int) -> str:
        return f"EVT-{session_id}-{str(idx).zfill(3)}"
    
    def cart(self, year: str = "2026") -> str:
        return self._next("CART", 6, year)
    
    def cart_line(self) -> str:
        return self._next("CL", 9)
    
    def order(self, year: str = "2026") -> str:
        return self._next("ORD", 6, year)
    
    def order_line(self) -> str:
        return self._next("OL", 9)
    
    def product_relation(self) -> str:
        return self._next("PR", 9)
    
    def recommendation(self) -> str:
        return self._next("REC", 9)
    
    def ground_truth(self) -> str:
        return self._next("GT", 6)
    
    def reset(self):
        self._counters = {}


# Global instance
gen = IDGenerator()
