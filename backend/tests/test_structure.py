"""Tests for project directory structure."""

from pathlib import Path

BACKEND_ROOT = Path(__file__).parent.parent


def test_app_package_exists() -> None:
    """app/ package exists with __init__.py."""
    assert (BACKEND_ROOT / "app" / "__init__.py").exists()


def test_auth_module_exists() -> None:
    """app/auth/ module exists."""
    assert (BACKEND_ROOT / "app" / "auth" / "__init__.py").exists()


def test_sounds_module_exists() -> None:
    """app/sounds/ module exists."""
    assert (BACKEND_ROOT / "app" / "sounds" / "__init__.py").exists()


def test_scraper_module_exists() -> None:
    """app/scraper/ module exists."""
    assert (BACKEND_ROOT / "app" / "scraper" / "__init__.py").exists()


def test_admin_module_exists() -> None:
    """app/admin/ module exists."""
    assert (BACKEND_ROOT / "app" / "admin" / "__init__.py").exists()


def test_core_module_exists() -> None:
    """app/core/ module exists."""
    assert (BACKEND_ROOT / "app" / "core" / "__init__.py").exists()


def test_main_py_exists() -> None:
    """app/main.py exists."""
    assert (BACKEND_ROOT / "app" / "main.py").exists()


def test_config_py_exists() -> None:
    """app/config.py exists."""
    assert (BACKEND_ROOT / "app" / "config.py").exists()


def test_env_example_exists() -> None:
    """.env.example exists."""
    assert (BACKEND_ROOT / ".env.example").exists()


def test_pyproject_toml_exists() -> None:
    """pyproject.toml exists."""
    assert (BACKEND_ROOT / "pyproject.toml").exists()
