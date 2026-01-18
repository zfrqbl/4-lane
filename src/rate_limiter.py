
# src/rate_limiter.py
import time
from threading import Lock

class GlobalRateLimiter:
    def __init__(self, cooldown_period: int):
        self.cooldown_period = cooldown_period
        self.last_call_time = 0
        self.lock = Lock()

    def wait_if_needed(self):
        with self.lock:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.cooldown_period:
                sleep_time = self.cooldown_period - elapsed
                print(f"Rate limiter active: sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            self.last_call_time = time.time()

# Example usage:
# rate_limiter = GlobalRateLimiter(cooldown_period=CONFIG.system.global_cooldown)