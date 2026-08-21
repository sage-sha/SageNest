from dataclasses import dataclass
from threading import Lock


@dataclass
class Deployment:
    commit: str
    branch: str
    image_tag: str
    container_id: str
    url: str


class AppState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._deployment: Deployment | None = None

    def current(self) -> Deployment | None:
        with self._lock:
            return self._deployment

    def swap(self, next: Deployment) -> Deployment | None:
        with self._lock:
            prev = self._deployment
            self._deployment = next
            return prev
