from state import AppState, Deployment


async def handle(state: AppState, payload: dict) -> int:
    print("got a push")
    next = Deployment(
        commit="local",
        branch="main",
        image_tag="sagenest-local:dev",
        container_id="local",
        url="http://site.localhost/",
    )
    state.swap(next)
    return 200
