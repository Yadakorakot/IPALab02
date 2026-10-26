from netmiko import ConnectHandler

DEVICES = {"R1": "172.31.47.4", "R2": "172.31.47.5", "S1": "172.31.47.3"}

for name, ip in DEVICES.items():
    with ConnectHandler(device_type="cisco_ios_telnet", host=ip,
                        username="admin", password="cisco") as c:
        cfg = c.send_command("show running-config", read_timeout=60)
    with open(f"{name}-running-config.txt", "w") as f:
        f.write(cfg)
    print(f"saved {name}")