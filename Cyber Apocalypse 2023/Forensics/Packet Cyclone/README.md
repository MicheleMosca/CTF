# Packet Cyclone

Pandora's friend and partner, Wade, is the one that leads the investigation into the relic's location. Recently, he noticed some weird traffic coming from his host. That led him to believe that his host was compromised. After a quick investigation, his fear was confirmed. Pandora tries now to see if the attacker caused the suspicious traffic during the exfiltration phase. Pandora believes that the malicious actor used rclone to exfiltrate Wade's research to the cloud. Using the tool called "chainsaw" and the sigma rules provided, can you detect the usage of rclone from the event logs produced by Sysmon? To get the flag, you need to start and connect to the docker service and answer all the questions correctly.

## Writeup

To solve this challenge download the **chainsaw** program from github:

```bash
git clone https://github.com/WithSecureLabs/chainsaw
```

Build the program with **cargo**

```bash
cargo build --release
```

Now open a connection with the docker container:

```
nc 206.189.112.129 31448
```

Launch **chainsaw** with the **sigma** rules:

```bash
./chainsaw hunt ../../../Logs/ -s ../../../sigma_rules/ --mapping ../../mappings/sigma-event-logs-all.yml
```

And now search for the answers.

- What is the email of the attacker used for the exfiltration process? (for example: name@email.com)    
    > majmeret@protonmail.com

- What is the password of the attacker used for the exfiltration process? (for example: password123)
    > FBMeavdiaFZbWzpMqIVhJCGXZ5XXZI1qsU3EjhoKQw0rEoQqHyI

- What is the Cloud storage provider used by the attacker? (for example: cloud)
    > mega

- What is the ID of the process used by the attackers to configure their tool? (for example: 1337)
    > 3820

- What is the name of the folder the attacker exfiltrated; provide the full path. (for example: C:\Users\user\folder)
    > C:\Users\Wade\Desktop\Relic_location

- What is the name of the folder the attacker exfiltrated the files to? (for example: exfil_folder)
    > exfiltration

The flag will now appear:

```
[+] Here is the flag: HTB{3v3n_3xtr4t3rr3str14l_B31nGs_us3_Rcl0n3_n0w4d4ys}
```