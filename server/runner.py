import time
import urllib.error
import urllib.request

import docker

NETWORK = "sagenest"
HOST = "site.localhost"
ROUTER = "sagenest-site"

CONTAINER_PORT = 80
HEALTH_PATH = "/"
HEALTH_TIMEOUT = 30.0
HEALTH_INTERVAL = 1.0
HEALTH_REQUEST_TIMEOUT = 2.0


def start(image_tag: str) -> str:
    client = docker.from_env()
    container = client.containers.run(
        image=image_tag,
        detach=True,
        network=NETWORK,
        labels={
            "traefik.enable": "true",
            f"traefik.http.routers.{ROUTER}.rule": f"Host(`{HOST}`)",
            f"traefik.http.routers.{ROUTER}.entrypoints": "web",
            f"traefik.http.services.{ROUTER}.loadbalancer.server.port": str(CONTAINER_PORT),
            # traefik stops routing to a backend that fails this check. during
            # the overlap between old and new containers that keeps requests off
            # one that has started but isn't serving yet.
            f"traefik.http.services.{ROUTER}.loadbalancer.healthcheck.path": HEALTH_PATH,
            f"traefik.http.services.{ROUTER}.loadbalancer.healthcheck.interval": "2s",
            f"traefik.http.services.{ROUTER}.loadbalancer.healthcheck.timeout": "2s",
        },
    )

    return container.id


def address(container_id: str) -> str | None:
    """The container's IP on the sagenest network, once it has one."""
    client = docker.from_env()
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return None
    container.reload()
    endpoint = container.attrs["NetworkSettings"]["Networks"].get(NETWORK)
    if endpoint is None:
        return None
    return endpoint.get("IPAddress") or None


def wait_healthy(
    container_id: str,
    timeout: float = HEALTH_TIMEOUT,
    interval: float = HEALTH_INTERVAL,
) -> bool:
    """Poll the container until it serves HTTP, or give up.

    Checked directly over the docker network rather than through traefik, so a
    pass means this container is ready — not that routing happened to resolve
    to the old one. Returns False as soon as the container exits, since an
    image that crashes on start is never going to come back.
    """
    client = docker.from_env()
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            container = client.containers.get(container_id)
            container.reload()
        except docker.errors.NotFound:
            return False
        if container.status in ("exited", "dead"):
            return False

        ip = address(container_id)
        if ip and _responds(f"http://{ip}:{CONTAINER_PORT}{HEALTH_PATH}"):
            return True

        time.sleep(interval)

    return False


def _responds(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=HEALTH_REQUEST_TIMEOUT) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, OSError):
        # not up yet, or up and refusing — either way, not ready
        return False


def stop(container_id: str) -> None:
    if not container_id or container_id == "local":
        return

    client = docker.from_env()
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return
    container.stop(timeout=10)
    container.remove()

    print(f"Stopped container {container_id}")
