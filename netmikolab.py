from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios",
    "host": "172.31.45.4",
    "username": "admin",
    "password": "cisco",
}

R2 = {
    "device_type": "cisco_ios",
    "host": "172.31.45.5",
    "username": "admin",
    "password": "cisco",
}

S1 = {
    "device_type": "cisco_ios",
    "host": "172.31.45.3",
    "username": "admin",
    "password": "cisco",
}

# Configure VLAN 101 on S1

def configure_vlan101():

    print("=" * 60)
    print("Connecting to S1 (172.31.45.3)")

    commands = [
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

    with ConnectHandler(**S1) as ssh:

        print(f"Connected successfully: {ssh.find_prompt()}")

        print("\nConfiguring VLAN 101...")
        output = ssh.send_config_set(commands)
        print(output)

        print("\nSaving configuration...")
        ssh.save_config()

        print("\n===== S1 : SHOW VLAN BRIEF =====")
        output = ssh.send_command("show vlan brief")
        print(output)

    print("\nVLAN 101 configuration completed.")

# Configure OSPF on R1

def configure_ospf_r1():

    print("\n" + "=" * 60)
    print("Connecting to R1 (172.31.45.4)")

    commands = [
        "router ospf 1 vrf control-data",
        "network 10.45.1.0 0.0.0.255 area 0",
        "network 10.45.12.0 0.0.0.3 area 0",
    ]

    with ConnectHandler(**R1) as ssh:

        print(f"Connected successfully: {ssh.find_prompt()}")

        print("\nConfiguring OSPF on R1...")
        output = ssh.send_config_set(commands)
        print(output)

        print("\nSaving configuration...")
        ssh.save_config()

    print("\nR1 OSPF configuration completed.")

# Configure OSPF on R2

def configure_ospf_r2():

    print("\n" + "=" * 60)
    print("Connecting to R2 (172.31.45.5)")

    commands = [
        "router ospf 1 vrf control-data",
        "network 10.45.12.0 0.0.0.3 area 0",
        "network 10.45.2.0 0.0.0.255 area 0",
    ]

    with ConnectHandler(**R2) as ssh:

        print(f"Connected successfully: {ssh.find_prompt()}")

        print("\nConfiguring OSPF on R2...")
        output = ssh.send_config_set(commands)
        print(output)

        print("\nSaving configuration...")
        ssh.save_config()

    print("\nR2 OSPF configuration completed.")

# route ออก net

def configure_default_route():

    print("\n" + "=" * 60)
    print("Connecting to R2 (172.31.45.5)")

    commands = [
        "ip route vrf control-data 0.0.0.0 0.0.0.0 192.168.42.1",
        "router ospf 1 vrf control-data",
        "default-information originate",
    ]

    with ConnectHandler(**R2) as ssh:

        print(f"Connected successfully: {ssh.find_prompt()}")

        print("\nConfiguring Default Route on R2...")
        output = ssh.send_config_set(commands)
        print(output)

        print("\nSaving configuration...")
        ssh.save_config()

        print("\n===== R2 : DEFAULT ROUTE =====")
        output = ssh.send_command(
            "show ip route vrf control-data"
        )
        print(output)

    print("\nDefault Route configuration completed.")

# Verify OSPF

def verify_ospf():

    print("\n" + "=" * 60)
    print("VERIFY OSPF")
    print("=" * 60)

    print("\nConnecting to R1...")

    with ConnectHandler(**R1) as ssh:

        print("\n===== R1 : OSPF NEIGHBOR =====")
        output = ssh.send_command(
            "show ip ospf neighbor vrf control-data"
        )
        print(output)

        print("\n===== R1 : ROUTING TABLE =====")
        output = ssh.send_command(
            "show ip route vrf control-data"
        )
        print(output)

    print("\nConnecting to R2...")

    with ConnectHandler(**R2) as ssh:

        print("\n===== R2 : OSPF NEIGHBOR =====")
        output = ssh.send_command(
            "show ip ospf neighbor vrf control-data"
        )
        print(output)

        print("\n===== R2 : ROUTING TABLE =====")
        output = ssh.send_command(
            "show ip route vrf control-data"
        )
        print(output)

#config PAT

def configure_pat():

    print("\n" + "=" * 60)
    print("Connecting to R2 (172.31.45.5)")

    commands = [
        # ACL for inside networks
        "access-list 10 permit 10.45.1.0 0.0.0.255",
        "access-list 10 permit 10.45.2.0 0.0.0.255",

        # NAT Inside - traffic from R1
        "interface GigabitEthernet0/1",
        "ip nat inside",

        # NAT Inside - UbuntuCloudGuest network
        "interface GigabitEthernet0/2",
        "ip nat inside",

        # NAT Outside - NAT Cloud
        "interface GigabitEthernet0/3",
        "ip nat outside",

        # PAT / NAT Overload
        "ip nat inside source list 10 interface GigabitEthernet0/3 overload",
    ]

    with ConnectHandler(**R2) as ssh:

        print(f"Connected successfully: {ssh.find_prompt()}")

        print("\nConfiguring PAT on R2...")
        output = ssh.send_config_set(commands)
        print(output)

        print("\nSaving configuration...")
        ssh.save_config()

        print("\n===== R2 : NAT CONFIGURATION =====")
        output = ssh.send_command(
            "show running-config | include ip nat"
        )
        print(output)

        print("\n===== R2 : ACCESS LIST =====")
        output = ssh.send_command(
            "show access-lists 10"
        )
        print(output)

    print("\nPAT configuration completed.")

#Standard ACL

def configure_management_access():

    print("\n" + "=" * 60)
    print("Configuring SSH/Telnet Management Access")

    # Allow:
    # 172.31.45.0/28 = Management Plane
    # 10.30.6.0/23   = Lab306 Network
    commands = [
        "ip access-list standard MANAGEMENT-ACCESS",
        "permit 172.31.45.0 0.0.0.15",
        "permit 10.30.6.0 0.0.1.255",
        "deny any",
        "exit",

        "line vty 0 4",
        "access-class MANAGEMENT-ACCESS in",
        "transport input ssh telnet",
        "exit",
    ]

    devices = [
        ("R1", R1),
        ("R2", R2),
        ("S1", S1),
    ]

    for name, device in devices:

        print("\n" + "-" * 60)
        print(f"Connecting to {name} ({device['host']})")

        try:
            with ConnectHandler(**device) as ssh:

                print(f"Connected successfully: {ssh.find_prompt()}")

                print(f"\nConfiguring management access on {name}...")
                output = ssh.send_config_set(commands)
                print(output)

                print("\nSaving configuration...")
                ssh.save_config()

                print(f"\n===== {name} : MANAGEMENT ACL =====")
                output = ssh.send_command(
                    "show access-lists MANAGEMENT-ACCESS"
                )
                print(output)

                print(f"\n===== {name} : VTY CONFIGURATION =====")
                output = ssh.send_command(
                    "show running-config | section line vty"
                )
                print(output)

        except Exception as error:
            print(f"Configuration on {name} failed: {error}")

    print("\nManagement access configuration completed.")

# Main

def main():

    print("\n===== START NETMIKO LAB =====\n")

    configure_vlan101()

    configure_ospf_r1()
    configure_ospf_r2()

    configure_default_route()

    configure_pat()

    configure_management_access()

    verify_ospf()

    print("\n===== CONFIGURATION COMPLETE =====")


if __name__ == "__main__":
    main()