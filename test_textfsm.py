import pytest

from textfsm_lab import build_descriptions


def test_r1_descriptions():
    neighbors = [
        {
            "local_interface": "Gig 0/2",
            "remote_device": "R2.ipa.com",
            "remote_interface": "Gig 0/1",
        },
        {
            "local_interface": "Gig 0/0",
            "remote_device": "S0.ipa.com",
            "remote_interface": "Gig 0/1",
        },
    ]

    result = build_descriptions("R1", neighbors)

    assert result["Gig 0/2"] == "Connect to G0/1 of R2"
    assert result["Gig 0/0"] == "Connect to G0/1 of S0"


def test_r2_descriptions():
    neighbors = [
        {
            "local_interface": "Gig 0/0",
            "remote_device": "S0.ipa.com",
            "remote_interface": "Gig 0/2",
        },
        {
            "local_interface": "Gig 0/1",
            "remote_device": "R1.ipa.com",
            "remote_interface": "Gig 0/2",
        },
        {
            "local_interface": "Gig 0/2",
            "remote_device": "S1.ipa.com",
            "remote_interface": "Gig 0/1",
        },
    ]

    result = build_descriptions("R2", neighbors)

    assert result["Gig 0/0"] == "Connect to G0/2 of S0"
    assert result["Gig 0/1"] == "Connect to G0/2 of R1"
    assert result["Gig 0/2"] == "Connect to G0/1 of S1"

    # R2 G0/3 connects to NAT/WAN
    assert result["Gig 0/3"] == "Connect to WAN"


def test_s1_descriptions():
    neighbors = [
        {
            "local_interface": "Gig 0/1",
            "remote_device": "R2.ipa.com",
            "remote_interface": "Gig 0/2",
        },
        {
            "local_interface": "Gig 0/0",
            "remote_device": "S0.ipa.com",
            "remote_interface": "Gig 0/3",
        },
    ]

    result = build_descriptions("S1", neighbors)

    assert result["Gig 0/1"] == "Connect to G0/2 of R2"
    assert result["Gig 0/0"] == "Connect to G0/3 of S0"


def test_pc_interfaces():
    result_r1 = build_descriptions("R1", [])
    result_s1 = build_descriptions("S1", [])

    assert result_r1["Gig 0/1"] == "Connect to PC"
    assert result_s1["Gig 1/1"] == "Connect to PC"