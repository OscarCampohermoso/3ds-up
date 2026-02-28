"""Anti-macOS sanitization: removes junk files that corrupt the 3DS."""

import os
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()

# Archivos y carpetas que macOS inyecta y que dañan la 3DS
_JUNK_NAMES = {".DS_Store", "__MACOSX",
               ".Spotlight-V100", ".fseventsd", ".Trashes"}


def clean_macos_junk(sd_path: Path) -> int:
    """Recursively removes all macOS junk files from the SD card.

    Removes:
    - ._* files (4KB resource forks)
    - .DS_Store
    - __MACOSX/
    - Extended attributes (xattr) with xattr -cr

    Args:
        sd_path: Root path of the SD card to clean.

    Returns:
        Number of files/folders removed.
    """
    removed = 0

    for root, dirs, files in os.walk(sd_path, topdown=True):
        root_path = Path(root)

        # Eliminar carpetas basura y evitar descender en ellas
        junk_dirs = [d for d in dirs if d in _JUNK_NAMES]
        for junk_dir in junk_dirs:
            target = root_path / junk_dir
            try:
                import shutil
                shutil.rmtree(target)
                console.print(
                    f"  [red]✗[/red] Deleted directory: {target.relative_to(sd_path)}")
                removed += 1
            except OSError as e:
                console.print(
                    f"  [yellow]⚠[/yellow] Could not delete {target}: {e}")
            dirs.remove(junk_dir)

        # Eliminar archivos ._* y otros archivos basura
        for filename in files:
            if filename.startswith("._") or filename in _JUNK_NAMES:
                target = root_path / filename
                try:
                    target.unlink()
                    console.print(
                        f"  [red]✗[/red] Deleted file: {target.relative_to(sd_path)}")
                    removed += 1
                except OSError as e:
                    console.print(
                        f"  [yellow]⚠[/yellow] Could not delete {target}: {e}")

    # Resetear atributos extendidos con xattr
    _reset_xattrs(sd_path)

    return removed


def _reset_xattrs(sd_path: Path) -> None:
    """Removes all macOS extended attributes from the SD card.

    Args:
        sd_path: Root path of the SD card.
    """
    try:
        subprocess.run(
            ["xattr", "-cr", str(sd_path)],
            check=True,
            capture_output=True,
        )
        console.print("  [green]✓[/green] Extended attributes (xattr) cleaned")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # xattr no disponible (Linux/Windows) o falló — no crítico
        pass


def reset_archive_bits(sd_path: Path) -> None:
    """Resets the archive bit on all files in the SD card.

    macOS may set the archive bit, which can confuse Hekate and 3DS tools.

    Args:
        sd_path: Root path of the SD card.
    """
    try:
        for item in sd_path.rglob("*"):
            try:
                os.chflags(item, 0)
            except (OSError, AttributeError):
                pass
        console.print("  [green]✓[/green] Archive bits reset")
    except Exception as e:
        console.print(
            f"  [yellow]⚠[/yellow] Could not reset archive bits: {e}")
