import subprocess
import shutil
import time
import pytest
import httpx


def is_docker_available():
    return shutil.which("docker") is not None


def docker_info_ok():
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
        return res.returncode == 0
    except Exception:
        return False


def wait_for_url(url, timeout=30.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return r
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Timed out waiting for {url}")


@pytest.mark.integration
def test_compose_cluster_responds():
    """Build the compose cluster, check /ping on each replica, then tear down.

    The test will be skipped if Docker or the docker CLI is not available
    or if `docker info` cannot be executed successfully (permissions).
    """
    if not is_docker_available():
        pytest.skip("docker CLI not found on PATH")

    if not docker_info_ok():
        pytest.skip("docker daemon not available or insufficient permissions to run 'docker info' in this environment")

    compose_file = "compose.yaml"
    up_cmd = ["docker", "compose", "-f", compose_file, "up", "--build", "-d"]
    down_cmd = ["docker", "compose", "-f", compose_file, "down", "-v"]

    try:
        subprocess.run(up_cmd, check=True)

        # check three replicas on ports 8000,8001,8002
        for port in (8000, 8001, 8002):
            url = f"http://localhost:{port}/ping"
            r = wait_for_url(url, timeout=60.0)
            assert r.json().get("msg") == "pong"

    finally:
        # best-effort cleanup
        try:
            subprocess.run(down_cmd, check=False)
        except Exception:
            pass
