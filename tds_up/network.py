"""GitHub API client: downloads Luma3DS and GodMode9 releases."""

from dataclasses import dataclass
from typing import Optional

import requests

_LUMA_API = "https://api.github.com/repos/LumaTeam/Luma3DS/releases/latest"
_GM9_API = "https://api.github.com/repos/d0k3/GodMode9/releases/latest"

_TIMEOUT = 15


@dataclass
class ReleaseAsset:
    """Represents a downloadable asset from a GitHub release."""

    version: str
    name: str
    download_url: str
    size: int


def get_latest_luma() -> ReleaseAsset:
    """Fetches the latest Luma3DS release from GitHub.

    Returns:
        ReleaseAsset with information about the Luma3DS ZIP.

    Raises:
        requests.HTTPError: If the GitHub API fails.
        ValueError: If a valid ZIP asset is not found.
    """
    return _get_latest_zip(
        api_url=_LUMA_API,
        asset_filter=lambda name: name.endswith(".zip") and "Luma3DS" in name,
        tool_name="Luma3DS",
    )


def get_latest_gm9() -> ReleaseAsset:
    """Fetches the latest GodMode9 release from GitHub.

    Returns:
        ReleaseAsset with information about the GodMode9 ZIP.

    Raises:
        requests.HTTPError: If the GitHub API fails.
        ValueError: If a valid ZIP asset is not found.
    """
    return _get_latest_zip(
        api_url=_GM9_API,
        asset_filter=lambda name: name.endswith(".zip") and "GodMode9" in name,
        tool_name="GodMode9",
    )


def _get_latest_zip(api_url: str, asset_filter, tool_name: str) -> ReleaseAsset:
    """Queries the GitHub API and returns the ZIP asset that matches the filter.

    Args:
        api_url: URL of the GitHub releases API.
        asset_filter: Function that receives the asset name and returns bool.
        tool_name: Name of the tool (for error messages).

    Returns:
        ReleaseAsset with information about the found asset.
    """
    response = requests.get(api_url, timeout=_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    version = data.get("tag_name", "desconocida")
    assets = data.get("assets", [])

    for asset in assets:
        if asset_filter(asset["name"]):
            return ReleaseAsset(
                version=version,
                name=asset["name"],
                download_url=asset["browser_download_url"],
                size=asset["size"],
            )

    raise ValueError(
        f"No se encontró un ZIP válido para {tool_name} en la versión {version}")


def download_asset(asset: ReleaseAsset, progress_callback=None) -> bytes:
    """Descarga un asset de GitHub y devuelve su contenido en bytes.

    Args:
        asset: El asset a descargar.
        progress_callback: Función opcional llamada con (bytes_descargados, total).

    Returns:
        Contenido del archivo en bytes.

    Raises:
        requests.HTTPError: Si la descarga falla.
    """
    response = requests.get(asset.download_url, stream=True, timeout=_TIMEOUT)
    response.raise_for_status()

    chunks = []
    downloaded = 0

    for chunk in response.iter_content(chunk_size=8192):
        chunks.append(chunk)
        downloaded += len(chunk)
        if progress_callback:
            progress_callback(downloaded, asset.size)

    return b"".join(chunks)
