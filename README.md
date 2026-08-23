# SageNest

SageNest watches one repo's `main` branch and keeps a containerized
preview of it live — push to `main`, the site updates. That's the whole
thing. Point it at your own frontend repo (it just needs a `Dockerfile`).

    git push -> webhook -> sagenest server (python)
                             clone repo
                             docker build
                             new container swaps in for the old one
    browser -> your domain -> traefik -> the site

## the tools and how we use them

- python + fastapi, the server. gets the webhook and runs the whole
  clone/build/deploy pipeline, most of the work is here
- docker, the site runs in a container built from the target repo's own
  `Dockerfile`, updating is basically swapping containers
- traefik, the reverse proxy. watches docker and routes traffic to
  whatever container is currently live, based on labels the server puts
  on it. start it once with docker compose and forget about it
- git + github webhooks, github hits the server on every push
- typescript + vite, the dashboard, little page that shows what's live

## layout

    server/       the python server, pipeline lives here
    client/       dashboard
    example-site/ a small static site + Dockerfile, stand-in for
                   whatever frontend repo you actually point this at
    docker-compose.yml  traefik
    scripts/dev.sh      convenience wrapper for the commands below

## running

    docker compose up -d                                          # traefik, once
    cd server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # server deps, once
    .venv/bin/uvicorn main:app --host 0.0.0.0 --port 3000 --reload  # the server
    cd client && npm run dev                                       # dashboard, optional

Or use the wrapper:

    ./scripts/dev.sh start   # traefik + server + dashboard together
    ./scripts/dev.sh stop    # tear traefik down

On Windows, run the server pieces from WSL — the venv and shell scripts
assume a POSIX environment.

## pointing this at your own site

`site.localhost` only works because it resolves to your own machine with
no setup — going live for real needs a few things true first:

- **DNS**: your domain needs an A/AAAA record pointing at whatever
  machine is going to run this stack.
- **port 80 reachable**: that machine needs to actually be reachable on
  port 80 from the internet — open in any firewall, and forwarded if
  it's sitting behind a router/NAT.
- **`server/runner.py`**: `HOST = "site.localhost"` — this is what
  traefik routes to visitors by. Rename it to your actual domain.
- **the GitHub webhook**: point it at `http://<your-server>:3000/webhook`
  on whatever repo you want live-previewed, with `Content-Type:
  application/json` and a secret matching `WEBHOOK_SECRET` below.
- **keep it running**: the "running" commands above are dev-shaped — a
  `--reload` server in a foreground terminal dies the moment that
  terminal closes. For a real deploy, run `uvicorn` under something
  that keeps it alive and restarts it (systemd, a process manager,
  `tmux` + disown, whatever). Traefik itself now has
  `restart: unless-stopped` in `docker-compose.yml`, so it survives a
  reboot on its own.

`webhook.py` reads which repo to clone straight from the push payload,
so none of this is tied to any one project.

## config (`.env` at the repo root, gitignored)

    WEBHOOK_SECRET=   shared with the github webhook, verifies X-Hub-Signature-256.
                      if unset, signature checking is skipped entirely.
    REPO_URL=         reserved, not read by any code yet
    GITHUB_TOKEN=     reserved, not read by any code yet (would be needed
                      to clone a private repo — clone_repo() only does a
                      plain unauthenticated `git clone` today)

## how a deploy actually happens

1. github POSTs to `/webhook` with a push payload.
2. the signature is checked against `WEBHOOK_SECRET`, if set.
3. pushes to any branch other than `main` are ignored (`200`, no-op).
4. the pushed repo is shallow-cloned at that commit.
5. `docker build` runs against the root of that checkout — the repo
   needs its own `Dockerfile` there, and that image needs to serve HTTP
   on port `80` inside the container, since that's what traefik routes to.
6. the new container is started, labeled for traefik, and swapped in as
   "current" — the previous container is then stopped and removed.

## known limitations

- one live deployment at a time — pushing swaps the site, it doesn't run
  previews side by side (no per-branch or per-PR environments yet).
- no health check before swapping — a broken build/crash-on-start image
  still replaces the working container, with no automatic rollback.
- `main` is hardcoded as the only deployed branch.
- old images and stopped containers aren't garbage collected.

## different ports

    8080  # traefik dashboard
    3000  # python server
    5173  # dashboard dev server
