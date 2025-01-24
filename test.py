import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("ip, expected_tags", [
    ("192.0.2.7", ["foo"]),
    ("192.0.2.9", ['bak', 'foo', 'zażółć ♥', '{$(<br>a-tag<br>)$}']),
    ("192.0.2.17", ["baz", "foo"]),
    ("203.0.113.10", ["alpha"]),
    ("203.0.113.150", ["alpha", "beta"]),
    ("203.0.113.180", ['alpha', 'beta']),
    ("10.20.30.40", ['SPAM', 'bar', 'delta']),
    ("10.20.30.41", ['bar', "delta"]),
    ("10.120.30.40", ["delta"]),
    ("10.0.2.15", ["delta", "epsilon"]),
    ("10.0.1.150", ['delta', 'epsilon', 'eta', 'zeta']),
    ("172.16.10.100", ['iota', 'theta']),
    ("192.168.0.100", ["kappa"]),
    ("192.168.1.150", ['kappa', 'lambda', 'mu']),
    ("8.8.8.8", ["SPECIAL"]),
    ("10.120.30.40", ["delta"]),
    ("192.0.3.9", []),
    ("203.0.113.255", ['alpha', 'beta']),
    ("255.255.255.255", []),
])
def test_ip_tags(ip, expected_tags, client):
    response = client.get(f"/ip-tags/{ip}")
    assert response.status_code == 200
    assert response.json() == expected_tags

def test_ip_tags_404():
    response = client.get(f"/ip-tags/255.255.255.255/24")
    assert response.status_code == 404
    assert "Not Found" in response.text

def test_ip_tags_incorrect_ip():
    response = client.get(f"/ip-tags/255.255.255.2524")
    assert response.status_code == 422
    assert "Input is not a valid IPv4 address" in response.text

@pytest.mark.parametrize("ip, expected_html", [
    ("192.0.2.7", "<td>foo</td>"),
    ("192.0.2.9", """<tr><td>foo</td></tr><tr><td>zażółć ♥</td></tr><tr><td>{$(<br>a-tag<br>)$}</td></tr>"""),
    ("255.255.255.255", "<td></td>"),
])
def test_ip_tags_report(ip, expected_html):
    response = client.get(f"/ip-tags-report/{ip}")
    assert response.status_code == 200
    assert expected_html in response.text

# TODO(test /ip-tags-report/{ip} with incorrect ip)
# TODO(test /ip-tags-report/{ip} with network like /ip-tags/255.255.255.255/24)
