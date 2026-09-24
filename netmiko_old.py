from netmiko import ConnectHandler


S1 = {
    "device_type": "cisco_ios",
    "host": "172.31.45.3",
    "username": "admin",
    "password": "cisco",
}

S1_CONFIG = [
    "vlan 101",
    "name CONTROL-DATA",
    "interface GigabitEthernet0/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
    "interface GigabitEthernet1/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
]


def main() -> None:
    print("Connecting to S1...")

    with ConnectHandler(**S1) as connection:
        print(f"Connected: {connection.find_prompt()}")

        print("\nConfiguring VLAN 101...")
        output = connection.send_config_set(S1_CONFIG)
        print(output)

        print("\nSaving configuration...")
        print(connection.save_config())

        print("\nVerifying VLAN 101...")
        print(connection.send_command("show vlan brief"))


if __name__ == "__main__":
    main()