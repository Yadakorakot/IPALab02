from netmiko import ConnectHandler


# ==========================================
# Device Information
# ==========================================

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


# ==========================================
# Helper Functions
# ==========================================

def short_interface(interface):
    """
    Convert:
    Gig 0/1 -> G0/1
    GigabitEthernet0/1 -> G0/1
    """
    interface = interface.strip()

    if interface.startswith("GigabitEthernet"):
        return interface.replace("GigabitEthernet", "G")

    if interface.startswith("Gig"):
        return interface.replace("Gig ", "G")

    return interface


def short_device(device):
    """
    Convert:
    R1.ipa.com -> R1
    S0.ipa.com -> S0
    """
    return device.split(".")[0]


# ==========================================
# Build Interface Descriptions
# ==========================================

def build_descriptions(device_name, neighbors):

    descriptions = {}

    # Cisco-to-Cisco connections from CDP
    for neighbor in neighbors:

        local_interface = neighbor["local_interface"]

        remote_device = short_device(
            neighbor["remote_device"]
        )

        remote_interface = short_interface(
            neighbor["remote_interface"]
        )

        descriptions[local_interface] = (
            f"Connect to {remote_interface} "
            f"of {remote_device}"
        )

    # Interface connected to PC
    if device_name == "R1":
        descriptions["Gig 0/1"] = "Connect to PC"

    if device_name == "S1":
        descriptions["Gig 1/1"] = "Connect to PC"

    # R2 G0/3 connects to WAN
    if device_name == "R2":
        descriptions["Gig 0/3"] = "Connect to WAN"

    return descriptions


# ==========================================
# Convert NTC Template Result
# ==========================================

def convert_neighbors(cdp_data):

    neighbors = []

    for item in cdp_data:

        # NTC Templates may return lists
        local_interface = item.get(
            "local_interface", ""
        )

        remote_device = item.get(
            "neighbor_name", ""
        )

        remote_interface = item.get(
            "neighbor_interface", ""
        )

        if isinstance(remote_interface, list):
            remote_interface = remote_interface[0]

        neighbors.append(
            {
                "local_interface": local_interface,
                "remote_device": remote_device,
                "remote_interface": remote_interface,
            }
        )

    return neighbors


# ==========================================
# Configure Device
# ==========================================

def configure_device(device):

    print("=" * 60)
    print(
        f"Connecting to {device['name']} "
        f"({device['host']})"
    )

    connection = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
    )

    print(
        f"Connected successfully: "
        f"{connection.find_prompt()}"
    )

    # --------------------------------------
    # Run CDP and parse using TextFSM
    # --------------------------------------

    print("\nReading CDP neighbors...")

    cdp_data = connection.send_command(
        "show cdp neighbors",
        use_textfsm=True
    )

    if not isinstance(cdp_data, list):
        print("TextFSM parsing failed.")
        connection.disconnect()
        return

    neighbors = convert_neighbors(cdp_data)

    # --------------------------------------
    # Build descriptions
    # --------------------------------------

    descriptions = build_descriptions(
        device["name"],
        neighbors
    )

    print("\nGenerated interface descriptions:")

    for interface, description in descriptions.items():
        print(
            f"{interface} -> {description}"
        )

    # --------------------------------------
    # Generate Cisco configuration
    # --------------------------------------

    commands = []

    for interface, description in descriptions.items():

        interface_name = short_interface(interface)

        # Convert G0/1 -> GigabitEthernet0/1
        if interface_name.startswith("G"):
            interface_name = interface_name.replace(
                "G",
                "GigabitEthernet",
                1
            )

        commands.extend(
            [
                f"interface {interface_name}",
                f"description {description}",
            ]
        )

    # --------------------------------------
    # Send configuration
    # --------------------------------------

    print("\nSending configuration...")

    output = connection.send_config_set(commands)

    print(output)

    print("\nSaving configuration...")

    connection.save_config()

    # --------------------------------------
    # Verification
    # --------------------------------------

    print("\nInterface descriptions:")

    verify = connection.send_command(
        "show interfaces description"
    )

    print(verify)

    connection.disconnect()

    print(
        f"\nConfiguration completed on "
        f"{device['name']}\n"
    )


# ==========================================
# Main
# ==========================================

def main():

    print(
        "\n===== TEXTFSM + NTC TEMPLATES LAB =====\n"
    )

    for device in DEVICES:

        try:
            configure_device(device)

        except Exception as error:

            print(
                f"Configuration on "
                f"{device['name']} failed: "
                f"{error}"
            )


if __name__ == "__main__":
    main()