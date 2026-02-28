"""Core logic: SD detection, backup, Smart Merge, and restore."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

# Carpetas que JAMÁS deben modificarse
PROTECTED_PATHS = {
    "Nintendo 3DS",  # Datos de juegos cifrados con clave única de consola
    "boot9strap",    # Bootloader — si se borra, brick total
}

# Archivos de configuración críticos del usuario
_BACKUP_TARGETS = [
    Path("luma") / "config.ini",
]

_BACKUP_ROOT = Path.home() / ".3ds-up" / "backups"


def detect_sd_card(sd_path: Optional[Path] = None) -> Path:
    """Detects or validates the path to the 3DS SD card.

    Args:
        sd_path: Explicit path. If None, tries to auto-detect.

    Returns:
        Validated SD card Path.

    Raises:
        FileNotFoundError: If the SD card cannot be detected or validated.
    """
    from tds_up.utils import detect_sd_path, validate_sd

    if sd_path is not None:
        path = Path(sd_path)
        if not validate_sd(path):
            raise FileNotFoundError(
                f"The path '{path}' does not appear to be a valid 3DS SD card with CFW.\n"
                "Make sure the SD card is mounted and contains the 'luma/' or 'Nintendo 3DS/' folders."
            )
        return path

    detected = detect_sd_path()
    if detected is None:
        raise FileNotFoundError(
            "No 3DS SD card detected mounted at /Volumes/.\n"
            "Mount the SD card and try again, or use --sd-path to specify the path."
        )
    return detected


def create_backup(sd_path: Path) -> Path:
    """Creates a backup of critical configuration files.

    Args:
        sd_path: Root path of the SD card.

    Returns:
        Path to the created backup folder.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = _BACKUP_ROOT / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    backed_up = 0
    for relative_path in _BACKUP_TARGETS:
        source = sd_path / relative_path
        if source.exists():
            dest = backup_dir / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            console.print(f"  [green]✓[/green] Backup: {relative_path}")
            backed_up += 1

    if backed_up == 0:
        console.print(
            "  [yellow]⚠[/yellow] No configuration files found to backup")

    return backup_dir


def restore_backup(backup_dir: Path, sd_path: Path) -> None:
    """Restores a previously created backup in case of failure.

    Args:
        backup_dir: Backup folder created by create_backup().
        sd_path: Root path of the SD card to restore to.
    """
    for relative_path in _BACKUP_TARGETS:
        source = backup_dir / relative_path
        if source.exists():
            dest = sd_path / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            console.print(f"  [green]✓[/green] Restored: {relative_path}")


def smart_merge(source_dir: Path, sd_path: Path) -> None:
    """Merges the contents of the source directory into the SD card without deleting anything.

    Copies files from the source onto the SD card using dirs_exist_ok=True,
    preserving SD card files not present in the source.
    Never touches protected paths (Nintendo 3DS/, boot9strap/).

    Args:
        source_dir: Directory extracted from the ZIP with new files.
        sd_path: Root path of the destination SD card.

    Raises:
        PermissionError: If attempting to write to a protected path.
    """
    for item in source_dir.iterdir():
        if item.name in PROTECTED_PATHS:
            console.print(
                f"  [yellow]⚠[/yellow] Skipping protected path: {item.name}/")
            continue

        dest = sd_path / item.name

        if item.is_dir():
            shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
            console.print(f"  [green]✓[/green] Merged: {item.name}/")
        else:
            shutil.copy2(str(item), str(dest))
            console.print(f"  [green]✓[/green] Copied: {item.name}")
