from netmiko import ConnectHandler
import re

# Device Information
DEVICES = [
    {
        "name": "R1",
        "device_type": "cisco_ios",
        "host": "172.31.45.4",
        "username": "admin",
        "password": "cisco",
    },
    {
        "name": "R2",
        "device_type": "cisco_ios",
        "host": "172.31.45.5",
        "username": "admin",
        "password": "cisco",
    },
]

# Check Active Interfaces and Uptime
def check_device(device):

    print("=" * 60)
    print(f"Connecting to {device['name']} ({device['host']})")

    connection = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
    )

    print(f"Connected successfully: {connection.find_prompt()}")

    interface_output = connection.send_command(
        "show ip interface brief"
    )

    version_output = connection.send_command(
        "show version"
    )

    interface_pattern = re.compile(
        r"^(\S+).*?\s+up\s+up\s*$",
        re.MULTILINE
    )

    active_interfaces = interface_pattern.findall(
        interface_output
    )

    uptime_pattern = re.compile(
        r"^\S+\s+uptime is\s+(.+)$",
        re.MULTILINE
    )

    uptime_match = uptime_pattern.search(
        version_output
    )

    print(
        f"\n===== {device['name']} : "
        f"ACTIVE INTERFACES ====="
    )

    if active_interfaces:
        for interface in active_interfaces:
            print(interface)
    else:
        print("No active interfaces found")

    print(
        f"\n===== {device['name']} : "
        f"UPTIME ====="
    )

    if uptime_match:
        print(uptime_match.group(1))
    else:
        print("Uptime not found")

    connection.disconnect()

    print(
        f"\nDisconnected from "
        f"{device['name']}\n"
    )

# Main

def main():

    print(
        "\n===== NETMIKO + "
        "REGULAR EXPRESSION LAB =====\n"
    )

    for device in DEVICES:

        try:
            check_device(device)

        except Exception as error:

            print(
                f"Connection to "
                f"{device['name']} failed: "
                f"{error}"
            )


if __name__ == "__main__":
    main()