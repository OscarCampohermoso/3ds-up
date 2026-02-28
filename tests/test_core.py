"""Tests para el módulo core."""

from pathlib import Path
import pytest
from tds_up.core import create_backup, restore_backup, smart_merge, PROTECTED_PATHS


def test_backup_copia_config_ini(fake_sd: Path) -> None:
    backup_dir = create_backup(fake_sd)
    assert (backup_dir / "luma" / "config.ini").exists()


def test_backup_directorio_tiene_timestamp(fake_sd: Path) -> None:
    backup_dir = create_backup(fake_sd)
    # El nombre del directorio debe ser un timestamp (14 dígitos)
    assert backup_dir.name.replace("_", "").isdigit()


def test_restore_recupera_config(fake_sd: Path, tmp_path: Path) -> None:
    backup_dir = create_backup(fake_sd)
    # Simula que el config se corrompió
    (fake_sd / "luma" / "config.ini").write_text("corrupted")
    restore_backup(backup_dir, fake_sd)
    content = (fake_sd / "luma" / "config.ini").read_text()
    assert "screen_brightness" in content


def test_smart_merge_copia_archivos(fake_sd: Path, tmp_path: Path) -> None:
    # Simula directorio extraído de un ZIP de Luma3DS
    source = tmp_path / "luma_extracted"
    source.mkdir()
    (source / "boot.firm").write_bytes(b"\xFF" * 64)
    (source / "luma").mkdir()
    (source / "luma" / "payloads").mkdir()
    (source / "luma" / "payloads" / "GodMode9.firm").write_bytes(b"\xAB" * 32)

    smart_merge(source, fake_sd)

    assert (fake_sd / "boot.firm").read_bytes() == b"\xFF" * 64
    assert (fake_sd / "luma" / "payloads" / "GodMode9.firm").exists()


def test_smart_merge_preserva_config_usuario(fake_sd: Path, tmp_path: Path) -> None:
    source = tmp_path / "luma_extracted"
    source.mkdir()
    (source / "luma").mkdir()
    # El ZIP no incluye config.ini — debe preservarse el del usuario

    smart_merge(source, fake_sd)

    assert (fake_sd / "luma" / "config.ini").exists()
    content = (fake_sd / "luma" / "config.ini").read_text()
    assert "screen_brightness" in content


def test_smart_merge_nunca_toca_protected(fake_sd: Path, tmp_path: Path) -> None:
    source = tmp_path / "malicious_zip"
    source.mkdir()
    # Un ZIP que intenta escribir en Nintendo 3DS/ (no debe ocurrir)
    (source / "Nintendo 3DS").mkdir()
    (source / "Nintendo 3DS" / "evil.txt").write_text("should not be here")

    smart_merge(source, fake_sd)

    # No debe haber copiado nada dentro de Nintendo 3DS/
    assert not (fake_sd / "Nintendo 3DS" / "evil.txt").exists()
