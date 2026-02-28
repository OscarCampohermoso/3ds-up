"""Fixtures compartidos para los tests de 3ds-up."""

import pytest
from pathlib import Path


@pytest.fixture
def fake_sd(tmp_path: Path) -> Path:
    """Crea una SD falsa de 3DS con estructura básica para tests."""
    (tmp_path / "Nintendo 3DS").mkdir()
    (tmp_path / "luma").mkdir()
    (tmp_path / "luma" / "payloads").mkdir()
    (tmp_path / "luma" / "config.ini").write_text("[config]\nscreen_brightness=3\n")
    (tmp_path / "boot9strap").mkdir()
    (tmp_path / "3ds").mkdir()
    (tmp_path / "boot.firm").write_bytes(b"\x00" * 64)
    return tmp_path


@pytest.fixture
def fake_sd_with_junk(fake_sd: Path) -> Path:
    """SD falsa con archivos basura de macOS."""
    (fake_sd / ".DS_Store").write_text("junk")
    (fake_sd / "._boot.firm").write_bytes(b"\x00" * 4096)
    (fake_sd / "__MACOSX").mkdir()
    (fake_sd / "luma" / ".DS_Store").write_text("junk")
    (fake_sd / "luma" / "._config.ini").write_bytes(b"\x00" * 4096)
    return fake_sd
