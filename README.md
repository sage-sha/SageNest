# SageNest

sagenest watches one repo, whatever is on master is the live site, when
master updates the site updates, thats the whole thing. this repo is the
skeleton, the core functions are empty on purpose, you are supposed to build them out and make everything pop. if somethign isnt working your way or you find a better way, change it and stick with it. this is just something to get you started, not something you have to stick with.

    git push -> webhook -> sagenest server (python)
                             clone master
                             docker build
                             new container swaps in for the old one
    browser -> site.localhost -> traefik -> the site

## the tools and how we use them

- python + fastapi, the server. gets the webhook and runs the whole
  clone/build/deploy thing, most of the work is here
- docker, the site runs in a container built from the repos own
  dockerfile, updating is basically swapping containers
- traefik, the reverse proxy. watches docker and sends site.localhost to
  whatever container is live based on labels the server puts on it, you
  start it once with docker compose and forget about it
- git + github webhooks, github hits the server on every push, until thats
  hooked up for real scripts/fake-push.sh fakes it locally
- typescript + vite, the dashboard, little page that shows whats live

## layout

    server/ the python server, pipeline lives here
      fixtures/ canned github push payload
      scripts/ fake-push.sh
    client/ dashboard
    example-site/ the site to watch while developing
    docker-compose.yml traefik

## running

    docker compose up -d # traefik, once
    cd server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt # server deps, once
    .venv/bin/uvicorn main:app --host 0.0.0.0 --port 3000 --reload # the server
    ./scripts/fake-push.sh # fake a github push (from server/)
    cd client && npm run dev # dashboard, optional at first

## different ports

# actual site url http://site.localhost/
8080 # traefik dashboard
3000 # python server
5173 # dashboard