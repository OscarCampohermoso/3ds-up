"""Tests para el módulo utils."""

import zipfile
import io
from pathlib import Path
from tds_up.utils import validate_sd, extract_zip, extract_zip_bytes


def test_validate_sd_valida(fake_sd: Path) -> None:
    assert validate_sd(fake_sd) is True


def test_validate_sd_invalida(tmp_path: Path) -> None:
    assert validate_sd(tmp_path) is False


def test_validate_sd_parcial(tmp_path: Path) -> None:
    # Solo una carpeta marcadora — no es suficiente
    (tmp_path / "luma").mkdir()
    assert validate_sd(tmp_path) is False


def test_extract_zip_crea_archivos(tmp_path: Path) -> None:
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("boot.firm", b"\x00" * 16)
        zf.writestr("luma/config.ini", "[config]\n")

    dest = tmp_path / "extracted"
    extract_zip(zip_path, dest)

    assert (dest / "boot.firm").exists()
    assert (dest / "luma" / "config.ini").exists()


def test_extract_zip_bytes_crea_archivos(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("boot.firm", b"\xFF" * 16)

    dest = tmp_path / "extracted_bytes"
    extract_zip_bytes(buf.getvalue(), dest)

    assert (dest / "boot.firm").exists()
