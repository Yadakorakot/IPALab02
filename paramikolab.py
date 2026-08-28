import paramiko

devices = [
    ("R0", "172.31.45.1"),
    ("S0", "172.31.45.2"),
    ("S1", "172.31.45.3"),
    ("R1", "172.31.45.4"),
    ("R2", "172.31.45.5"),
]

USERNAME = "admin"

KEY = r"C:\Users\LAB308_XX\.ssh\id_rsa"

for name, ip in devices:

    print("="*50)
    print(name, ip)

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=ip,
        username=USERNAME,
        key_filename=KEY,
        look_for_keys=False,
        allow_agent=False,
    )

    stdin, stdout, stderr = ssh.exec_command("show ip interface brief")

    print(stdout.read().decode())

    ssh.close()