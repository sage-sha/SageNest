from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock

HISTORY_LIMIT = 10

LIVE = "live"
SUPERSEDED = "superseded"
FAILED = "failed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Deployment:
    commit: str
    branch: str
    image_tag: str
    container_id: str
    url: str
    status: str = LIVE
    detail: str = ""
    at: str = field(default_factory=_now)


class AppState:
    """The one live deployment, plus a short tail of what came before it."""

    def __init__(self, history_limit: int = HISTORY_LIMIT) -> None:
        self._lock = Lock()
        self._deployment: Deployment | None = None
        self._history: list[Deployment] = []
        self._history_limit = history_limit

    def current(self) -> Deployment | None:
        with self._lock:
            return self._deployment

    def history(self) -> list[Deployment]:
        with self._lock:
            return list(self._history)

    def swap(self, next: Deployment) -> Deployment | None:
        """Make `next` live and return whatever it replaced, or None."""
        with self._lock:
            prev = self._deployment
            if prev is not None:
                prev.status = SUPERSEDED
                self._remember(prev)
            next.status = LIVE
            self._deployment = next
            return prev

    def record_failure(self, attempt: Deployment, detail: str = "") -> None:
        """Log a deploy that never went live. Does not touch the current one."""
        with self._lock:
            attempt.status = FAILED
            attempt.detail = detail
            self._remember(attempt)

    def _remember(self, deployment: Deployment) -> None:
        # caller holds the lock
        self._history.insert(0, deployment)
        del self._history[self._history_limit:]
