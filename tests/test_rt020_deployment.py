"""
RT-020: Docker & Render Deployment Configuration Tests.
"""
from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).parent.parent


def test_dockerfile_exists():
    assert (PROJECT_ROOT / "Dockerfile").exists()


def test_dockerfile_non_root():
    """Verify Dockerfile runs as non-root user."""
    content = (PROJECT_ROOT / "Dockerfile").read_text()
    assert "USER reeltranscribe" in content
    assert "groupadd" in content


def test_dockerfile_healthcheck():
    """Verify Dockerfile has a HEALTHCHECK instruction."""
    content = (PROJECT_ROOT / "Dockerfile").read_text()
    assert "HEALTHCHECK" in content


def test_docker_compose_exists():
    assert (PROJECT_ROOT / "docker-compose.yml").exists()


def test_docker_compose_valid_yaml():
    content = (PROJECT_ROOT / "docker-compose.yml").read_text()
    parsed = yaml.safe_load(content)
    assert "services" in parsed
    assert "api" in parsed["services"]


def test_render_yaml_exists():
    assert (PROJECT_ROOT / "render.yaml").exists()


def test_render_yaml_valid():
    content = (PROJECT_ROOT / "render.yaml").read_text()
    parsed = yaml.safe_load(content)
    assert "services" in parsed
    svc = parsed["services"][0]
    assert svc["healthCheckPath"] == "/health"
    assert svc["plan"] == "free"


def test_requirements_txt_exists():
    assert (PROJECT_ROOT / "requirements.txt").exists()
    content = (PROJECT_ROOT / "requirements.txt").read_text()
    assert "fastapi" in content
    assert "uvicorn" in content
    assert "yt-dlp" in content
    assert "srt" in content
