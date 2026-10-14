import shutil

import builder
import runner
from state import AppState, Deployment


async def handle(state: AppState, payload: dict) -> int:
    ref = payload.get("ref", "")
    if not ref.startswith("refs/heads/"):
        return 200
    branch = ref.removeprefix("refs/heads/")
    if branch != "main":
        return 200

    commit = payload["after"]
    clone_url = payload["repository"]["clone_url"]
    checkout = builder.clone_repo(clone_url, branch)

    candidate = Deployment(
        commit=commit[:12],
        branch=branch,
        image_tag="",
        container_id="",
        url=f"http://{runner.HOST}/",
    )

    try:
        try:
            candidate.image_tag = builder.build_image(checkout, commit)
        except Exception as exc:
            # nothing was started, so the current deployment is untouched
            state.record_failure(candidate, f"build failed: {exc}")
            return 500

        candidate.container_id = runner.start(candidate.image_tag)

        if not runner.wait_healthy(candidate.container_id):
            # never came up. tear it down and leave the running one alone —
            # this is the rollback: we simply don't swap.
            runner.stop(candidate.container_id)
            state.record_failure(
                candidate,
                f"health check failed after {runner.HEALTH_TIMEOUT:.0f}s",
            )
            return 500

        prev = state.swap(candidate)
        if prev is not None:
            runner.stop(prev.container_id)
    finally:
        shutil.rmtree(checkout, ignore_errors=True)

    return 200
