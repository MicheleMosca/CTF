# Persistence

Thousands of years ago, sending a GET request to **/flag** would grant immense power and wisdom. Now it's broken and usually returns random data, but keep trying, and you might get lucky... Legends say it works once every 1000 tries.

## Writeup

Write a script that make a request more than 1000 times to get the flag:

```bash
#!/bin/bash

for ((i=0;i<1200;i++))
do
	curl -s -X GET http://178.62.9.10:30845/flag
done
```

Make it executable:

```bash
chmod u+x script.sh
```

Then launch it with command:

```bash
./script.sh | grep HTB
```

The flag is:

```
HTB{y0u_h4v3_p0w3rfuL_sCr1pt1ng_ab1lit13S!}
```