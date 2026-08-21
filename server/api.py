from state import AppState, Deployment


def status(state: AppState) -> Deployment | None:
    return state.current()
