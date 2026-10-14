from dataclasses import asdict

from state import AppState


def status(state: AppState) -> dict:
    current = state.current()
    return {
        "current": asdict(current) if current is not None else None,
        "history": [asdict(deployment) for deployment in state.history()],
    }
