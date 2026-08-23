from pathlib import Path
import docker

import tempfile
import subprocess


def clone_repo(clone_url: str, branch: str) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="sagenest-"))
    subprocess.run(
        [
            "git",
            "clone",
            "--depth", "1",
            "--branch", branch,
            clone_url,
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return dest


def build_image(checkout: Path, commit: str) -> str:
    tag = f"sagenest:{commit[:12]}"
    client = docker.from_env()
    client.images.build(path=str(checkout), tag=tag)
   
    return tag


