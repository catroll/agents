# A host times out through the local proxy but works directly

## Symptom

With the proxy exported from `~/.proxyrc`:

    source ~/.proxyrc
    curl -sSL --max-time 25 https://documentation.ubuntu.com/desktop/en/latest/
    # curl: (28) Connection timed out after 25002 milliseconds

The same URL returns 200 when the proxy variables are removed:

    env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
        -u all_proxy -u ALL_PROXY \
        curl -sSL --max-time 25 https://documentation.ubuntu.com/desktop/en/latest/

`ubuntu.com` and GitHub worked through the proxy in the same shell, so the
proxy itself was up; only this host failed.

## Why

The proxy's upstream path does not reach every host. A proxy timeout is not
evidence that the origin is down, and it is not evidence that the network is
down.

## Procedure

1. Retry the exact URL with the proxy variables unset before concluding the
   site is gone.
2. If the direct request succeeds, use direct for that host for the rest of the
   session (do not unset the proxy globally; other hosts need it).
3. `web_fetch` may use a different egress and can succeed where `curl` through
   the proxy fails, but it refuses cross-origin redirects; a direct `curl -L`
   is often simpler.

## Negative result

`curl -I` through the proxy returned `000` twice; the direct request returned
`200` immediately. The docs host was never down.
