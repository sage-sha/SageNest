import shutil
import tempfile
from pathlib import Path

import runner
import builder
from state import AppState, Deployment;


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
    try:
        image_tag = builder.build_image(checkout / "example-site", commit) # change to: builder.build_image(checkout, commit) after testing locally
        container_id = runner.start(image_tag)
        next = Deployment(
            commit=commit[:12],
            branch=branch,
            image_tag=image_tag,
            container_id=container_id,
            url="http://site.localhost/",
        )
        prev = state.swap(next)
        if prev is not None:
            runner.stop(prev.container_id)
    finally:
        shutil.rmtree(checkout, ignore_errors=True)
    return 200