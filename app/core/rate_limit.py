import time
from collections import deque
from typing import Deque


class SimpleRateLimiter:
    """In-memory rate limiter by client identifier."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: dict[str, Deque[float]] = {}

    def is_request_allowed(self, client_id: str) -> tuple[bool, int | None]:
        now = time.time()
        timestamps = self.clients.setdefault(client_id, deque())

        while timestamps and timestamps[0] <= now - self.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - timestamps[0]))
            return False, max(retry_after, 1)

        timestamps.append(now)
        return True, None

    def reset(self) -> None:
        self.clients.clear()
