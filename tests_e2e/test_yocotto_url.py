import os
import time
import pytest
import requests

SERVICE_URL = "http://localhost:8080/"

THE_LONGEST_URL = (
    "http://llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch.co.uk/"
)


def run_command(cmd):
    print(f"running command {cmd}")
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    return os.system(cmd)


@pytest.fixture
def setup_service():
    run_command(["docker-compose", "up", "-d"])
    time.sleep(2)
    yield
    run_command(["docker-compose", "down"])
    time.sleep(2)


def test_post(setup_service):
    response = requests.post(SERVICE_URL, json={"long_url": THE_LONGEST_URL})
    assert response.json() == {"long_url": THE_LONGEST_URL, "url_id": "1"}
    response = requests.post(SERVICE_URL, json={"long_url": THE_LONGEST_URL})
    assert response.json() == {"long_url": THE_LONGEST_URL, "url_id": "2"}


def test_post_plus_get(setup_service):
    requests.post(SERVICE_URL, json={"long_url": THE_LONGEST_URL})
    response = requests.get(SERVICE_URL + "1")
    assert THE_LONGEST_URL in response.text


def test_put_plus_get(setup_service):
    url_id = "the-longest-url"
    response_put = requests.put(
        SERVICE_URL + url_id, json={"long_url": THE_LONGEST_URL}
    )
    assert response_put.json() == {"long_url": THE_LONGEST_URL, "url_id": url_id}
    response_get = requests.get(SERVICE_URL + url_id)
    assert THE_LONGEST_URL in response_get.text
