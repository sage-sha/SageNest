import os

import docker

NETWORK = "sagenest"
HOST = "site.localhost"
ROUTER = "sagenest-site"

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
            f"traefik.http.services.{ROUTER}.loadbalancer.server.port": "80",
        
        },
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



