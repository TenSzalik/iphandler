import pytest
from fastapi.testclient import TestClient
from main import app, IPHandler, get_iphandler
import orjson


@pytest.fixture
def test_data_file(tmp_path):
    """
    Create JSON file with test data and returns path to this.
    """
    test_data = [
        {"tag": "foo", "ip_network": "192.0.2.0/24"},
        {"tag": "foo", "ip_network": "192.0.2.0/24"},
        {"tag": "{$(<br>a-tag<br>)$}", "ip_network": "192.0.2.8/29"},
        {"tag": "bar", "ip_network": "10.20.0.0/16"},
        {"tag": "zażółć ♥", "ip_network": "192.0.2.8/29"},
        {"tag": "bak", "ip_network": "192.0.2.8/29"},
        {"tag": "baz", "ip_network": "192.0.2.16/28"},
        {"tag": "alpha", "ip_network": "203.0.113.0/24"},
        {"tag": "beta", "ip_network": "203.0.113.128/25"},
        {"tag": "gamma", "ip_network": "203.0.113.64/26"},
        {"tag": "delta", "ip_network": "10.0.0.0/8"},
        {"tag": "epsilon", "ip_network": "10.0.0.0/16"},
        {"tag": "zeta", "ip_network": "10.0.1.0/24"},
        {"tag": "eta", "ip_network": "10.0.1.128/25"},
        {"tag": "theta", "ip_network": "172.16.0.0/12"},
        {"tag": "iota", "ip_network": "172.16.10.0/24"},
        {"tag": "kappa", "ip_network": "192.168.0.0/16"},
        {"tag": "lambda", "ip_network": "192.168.1.0/24"},
        {"tag": "mu", "ip_network": "192.168.1.128/25"},
        {"tag": "SPAM", "ip_network": "10.20.30.40/32"},
        {"tag": "SPECIAL", "ip_network": "8.8.8.0/24"}
    ]
    test_file = tmp_path / "test.json"
    test_file.write_text(orjson.dumps(test_data).decode("utf-8"))
    return str(test_file)


@pytest.fixture
def override_iphandler(test_data_file):
    """
    Returns prepared instance.
    """
    handler = IPHandler(knowledge_base_file=test_data_file)
    handler._prepare_trie()
    return handler


@pytest.fixture
def client(override_iphandler, monkeypatch):
    """
    Override get_iphandler() in app and create test client.
    """
    def mock_get_iphandler():
        return override_iphandler

    app.dependency_overrides[get_iphandler] = mock_get_iphandler
    return TestClient(app)
