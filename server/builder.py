from pathlib import Path


def clone_repo(clone_url: str, branch: str) -> Path:
    raise NotImplementedError


def build_image(checkout: Path, commit: str) -> str:
    raise NotImplementedError
