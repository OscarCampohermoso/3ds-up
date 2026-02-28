"""Entry point del CLI: define los comandos con Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from tds_up import __version__

app = typer.Typer(
    name="3ds-up",
    help="Actualizador seguro de Nintendo 3DS para macOS.",
    add_completion=False,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"3ds-up v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Muestra la versión instalada.",
    ),
) -> None:
    pass


@app.command()
def update(
    latest: bool = typer.Option(
        False, "--latest", help="Download and install the latest available version."),
    luma_only: bool = typer.Option(
        False, "--luma-only", help="Update only Luma3DS."),
    gm9_only: bool = typer.Option(
        False, "--gm9-only", help="Update only GodMode9."),
    sd_path: Optional[Path] = typer.Option(
        None, "--sd-path", help="Manual path to the SD if not auto-detected."),
) -> None:
    """Download and install Luma3DS and/or GodMode9 to the SD safely."""
    from tds_up import core, cleaner, network
    from tds_up.utils import extract_zip_bytes, cleanup_temp_dir

    if not latest:
        console.print(
            "[red]Use --latest to download the latest version.[/red]")
        raise typer.Exit(1)

    console.print(
        Panel("[bold cyan]3ds-up — Safe updater for Nintendo 3DS[/bold cyan]"))

    # 1. Detect SD
    console.print("\n[bold]1. Detecting SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detected: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    # 2. Backup
    console.print("\n[bold]2. Creating configuration backup...[/bold]")
    backup_dir = core.create_backup(sd)
    console.print(f"  [green]✓[/green] Backup saved at: {backup_dir}")

    # 3. Descargar y aplicar
    try:
        if not gm9_only:
            _install_luma(sd, core, network,
                          extract_zip_bytes, cleanup_temp_dir)

        if not luma_only:
            _install_gm9(sd, core, network,
                         extract_zip_bytes, cleanup_temp_dir)

        # 4. Clean macOS junk
        console.print("\n[bold]4. Cleaning macOS junk files from SD...[/bold]")
        removed = cleaner.clean_macos_junk(sd)
        cleaner.reset_archive_bits(sd)
        console.print(f"  [green]✓[/green] {removed} junk files removed")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        console.print("[yellow]Restoring backup...[/yellow]")
        core.restore_backup(backup_dir, sd)
        raise typer.Exit(1)

    console.print(
        Panel("[bold green]Update complete! Insert the SD into your 3DS.[/bold green]"))


def _install_luma(sd, core, network, extract_zip_bytes, cleanup_temp_dir):
    console.print("\n[bold]3a. Downloading Luma3DS...[/bold]")
    asset = network.get_latest_luma()
    console.print(f"  [green]✓[/green] Version found: {asset.version}")

    with console.status(f"  Downloading {asset.name}..."):
        data = network.download_asset(asset)

    tmp = extract_zip_bytes(data)
    try:
        console.print("  Applying Smart Merge...")
        core.smart_merge(tmp, sd)
    finally:
        cleanup_temp_dir(tmp)


def _install_gm9(sd, core, network, extract_zip_bytes, cleanup_temp_dir):
    console.print("\n[bold]3b. Downloading GodMode9...[/bold]")
    asset = network.get_latest_gm9()
    console.print(f"  [green]✓[/green] Version found: {asset.version}")

    with console.status(f"  Downloading {asset.name}..."):
        data = network.download_asset(asset)

    tmp = extract_zip_bytes(data)
    try:
        console.print("  Applying Smart Merge...")
        core.smart_merge(tmp, sd)
    finally:
        cleanup_temp_dir(tmp)


@app.command(name="fix-archive-bit")
def fix_archive_bit(
    sd_path: Optional[Path] = typer.Argument(
        None, help="Path to the SD. If not provided, auto-detects."),
) -> None:
    """Removes macOS junk files from the SD without updating anything."""
    from tds_up import core, cleaner

    console.print(Panel("[bold cyan]3ds-up — macOS file cleanup[/bold cyan]"))

    console.print("\n[bold]Detecting SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detected: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold]Cleaning...[/bold]")
    removed = cleaner.clean_macos_junk(sd)
    cleaner.reset_archive_bits(sd)

    console.print(
        Panel(f"[bold green]Cleanup complete. {removed} files removed.[/bold green]"))


@app.command()
def install(
    zip_file: Path = typer.Argument(...,
                                    help="Path to the ZIP file to install."),
    sd_path: Optional[Path] = typer.Option(
        None, "--sd-path", help="Manual path to the SD."),
) -> None:
    """Installs a local ZIP (Luma3DS, GodMode9, etc.) to the SD safely."""
    from tds_up import core, cleaner
    from tds_up.utils import extract_zip, cleanup_temp_dir

    console.print(
        Panel("[bold cyan]3ds-up — Installation from local file[/bold cyan]"))

    if not zip_file.exists():
        console.print(f"  [red]✗[/red] File not found: {zip_file}")
        raise typer.Exit(1)

    console.print("\n[bold]1. Detecting SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detected: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold]2. Creating backup...[/bold]")
    backup_dir = core.create_backup(sd)

    try:
        console.print("\n[bold]3. Extracting and installing...[/bold]")
        tmp = extract_zip(zip_file)
        try:
            core.smart_merge(tmp, sd)
        finally:
            cleanup_temp_dir(tmp)

        console.print("\n[bold]4. Cleaning macOS files...[/bold]")
        removed = cleaner.clean_macos_junk(sd)
        cleaner.reset_archive_bits(sd)
        console.print(f"  [green]✓[/green] {removed} junk files removed")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        console.print("[yellow]Restoring backup...[/yellow]")
        core.restore_backup(backup_dir, sd)
        raise typer.Exit(1)

    console.print(Panel("[bold green]Installation complete![/bold green]"))
