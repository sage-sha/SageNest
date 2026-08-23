import os
import docker

NETWORK = "sagenest"
ROUTER = "sagenest-site"


def host() -> str:
    return os.getenv("SITE_HOST", "site.localhost")


def https() -> bool:
    return os.getenv("HTTPS") == "1"


def site_url() -> str:
    scheme = "https" if https() else "http"
    return f"{scheme}://{host()}/"


def start(image_tag: str) -> str:
    client = docker.from_env()
    labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.{ROUTER}.rule": f"Host(`{host()}`)",
        f"traefik.http.routers.{ROUTER}.entrypoints": "websecure" if https() else "web",
        f"traefik.http.services.{ROUTER}.loadbalancer.server.port": "80",
    }
    if https():
        labels[f"traefik.http.routers.{ROUTER}.tls.certresolver"] = "letsencrypt"

    container = client.containers.run(
        image=image_tag,
        detach=True,
        network=NETWORK,
        labels=labels,
    )

    return container.id


def stop(container_id: str) -> None:
    if not container_id or container_id == "local":
        return

    client = docker.from_env()
    container = client.containers.get(container_id)
    container.stop(timeout=10)
    container.remove()

    print(f"Stopped container {container_id}")
