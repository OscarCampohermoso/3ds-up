"""Helpers: detección de SD, descompresión de ZIPs, validaciones."""

import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Marcadores que identifican una SD de 3DS con CFW
_SD_MARKERS = [
    "Nintendo 3DS",
    "luma",
    "boot9strap",
]


def detect_sd_path() -> Optional[Path]:
    """Busca automáticamente la SD de 3DS en /Volumes/.

    Returns:
        Path al punto de montaje si se detecta, None si no se encuentra.
    """
    volumes = Path("/Volumes")
    if not volumes.exists():
        return None

    for volume in volumes.iterdir():
        if not volume.is_dir():
            continue
        matches = sum(1 for marker in _SD_MARKERS if (volume / marker).exists())
        if matches >= 2:
            return volume

    return None


def validate_sd(sd_path: Path) -> bool:
    """Verifica que la ruta dada sea una SD de 3DS con CFW válida.

    Args:
        sd_path: Ruta al punto de montaje de la SD.

    Returns:
        True si parece una SD de 3DS con CFW.
    """
    matches = sum(1 for marker in _SD_MARKERS if (sd_path / marker).exists())
    return matches >= 2


def extract_zip(zip_path: Path, dest_dir: Optional[Path] = None) -> Path:
    """Descomprime un ZIP en un directorio temporal o en dest_dir.

    Args:
        zip_path: Ruta al archivo ZIP.
        dest_dir: Directorio de destino. Si es None, usa un directorio temporal.

    Returns:
        Path al directorio donde se descomprimió el contenido.
    """
    if dest_dir is None:
        dest_dir = Path(tempfile.mkdtemp(prefix="3ds-up-"))

    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    return dest_dir


def extract_zip_bytes(data: bytes, dest_dir: Optional[Path] = None) -> Path:
    """Descomprime un ZIP desde bytes en memoria.

    Args:
        data: Contenido del ZIP en bytes.
        dest_dir: Directorio de destino. Si es None, usa un directorio temporal.

    Returns:
        Path al directorio donde se descomprimió el contenido.
    """
    import io

    if dest_dir is None:
        dest_dir = Path(tempfile.mkdtemp(prefix="3ds-up-"))

    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
        zf.extractall(dest_dir)

    return dest_dir


def cleanup_temp_dir(temp_dir: Path) -> None:
    """Elimina un directorio temporal creado durante el proceso.

    Args:
        temp_dir: Directorio temporal a eliminar.
    """
    if temp_dir.exists() and "3ds-up-" in temp_dir.name:
        shutil.rmtree(temp_dir)
