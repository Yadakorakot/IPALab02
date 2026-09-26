from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader


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
    {
        "name": "S1",
        "device_type": "cisco_ios",
        "host": "172.31.45.3",
        "username": "admin",
        "password": "cisco",
    },
]


# Load Jinja2 template
env = Environment(
    loader=FileSystemLoader("."),
    trim_blocks=True,
    lstrip_blocks=True
)

template = env.get_template("config.j2")


def configure_device(device):

    print("=" * 60)
    print(f"Connecting to {device['name']} ({device['host']})")

    connection = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
    )

    print(f"Connected successfully: {connection.find_prompt()}")

    # Render Jinja2 configuration
    rendered_config = template.render(
        device=device["name"]
    )

    commands = [
        command.strip()
        for command in rendered_config.splitlines()
        if command.strip()
    ]

    print("\nGenerated configuration:")
    print(rendered_config)

    print(f"\nSending configuration to {device['name']}...")

    output = connection.send_config_set(commands)
    print(output)

    print("\nSaving configuration...")
    connection.save_config()

    connection.disconnect()

    print(f"Configuration completed on {device['name']}\n")


def main():

    print("\n===== NETMIKO + JINJA2 LAB =====\n")

    for device in DEVICES:
        try:
            configure_device(device)
        except Exception as error:
            print(
                f"Configuration on {device['name']} failed: {error}"
            )

    print("\n===== CONFIGURATION COMPLETE =====")


if __name__ == "__main__":
    main()