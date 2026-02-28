"""Tests para el módulo cleaner."""

from pathlib import Path
from tds_up.cleaner import clean_macos_junk


def test_elimina_ds_store(fake_sd_with_junk: Path) -> None:
    clean_macos_junk(fake_sd_with_junk)
    assert not (fake_sd_with_junk / ".DS_Store").exists()
    assert not (fake_sd_with_junk / "luma" / ".DS_Store").exists()


def test_elimina_resource_forks(fake_sd_with_junk: Path) -> None:
    clean_macos_junk(fake_sd_with_junk)
    assert not (fake_sd_with_junk / "._boot.firm").exists()
    assert not (fake_sd_with_junk / "luma" / "._config.ini").exists()


def test_elimina_macosx_folder(fake_sd_with_junk: Path) -> None:
    clean_macos_junk(fake_sd_with_junk)
    assert not (fake_sd_with_junk / "__MACOSX").exists()


def test_preserva_archivos_validos(fake_sd_with_junk: Path) -> None:
    clean_macos_junk(fake_sd_with_junk)
    assert (fake_sd_with_junk / "boot.firm").exists()
    assert (fake_sd_with_junk / "luma" / "config.ini").exists()


def test_retorna_conteo_correcto(fake_sd_with_junk: Path) -> None:
    removed = clean_macos_junk(fake_sd_with_junk)
    assert removed >= 4  # .DS_Store x2, ._boot.firm, ._config.ini, __MACOSX/
