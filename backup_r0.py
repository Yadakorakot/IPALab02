import time
from pathlib import Path

import paramiko


R0_IP = "172.31.45.1"
USERNAME = "admin"
PRIVATE_KEY = Path.home() / ".ssh" / "id_rsa"
OUTPUT_FILE = "R0-running-config.txt"


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to R0 at {R0_IP}...")

    client.connect(
        hostname=R0_IP,
        username=USERNAME,
        key_filename=str(PRIVATE_KEY),
        look_for_keys=False,
        allow_agent=False,
        timeout=10,
    )

    shell = client.invoke_shell()
    time.sleep(1)

    shell.send("terminal length 0\n")
    time.sleep(1)

    shell.send("show running-config\n")
    time.sleep(3)

    output_parts = []

    while shell.recv_ready():
        output_parts.append(
            shell.recv(65535).decode("utf-8", errors="ignore")
        )
        time.sleep(0.5)

    output = "".join(output_parts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(output)

    print(f"Backup completed: {OUTPUT_FILE}")

except Exception as error:
    print(f"Backup failed: {error}")

finally:
    client.close()