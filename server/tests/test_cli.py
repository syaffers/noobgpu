from noobgpu.cli import display_host


def test_display_host_maps_bind_addresses():
    assert display_host("0.0.0.0") == "127.0.0.1"
    assert display_host("::") == "127.0.0.1"
    assert display_host("127.0.0.1") == "127.0.0.1"
    assert display_host("192.168.1.20") == "192.168.1.20"
