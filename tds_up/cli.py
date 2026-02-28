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
    latest: bool = typer.Option(False, "--latest", help="Descarga e instala la última versión disponible."),
    luma_only: bool = typer.Option(False, "--luma-only", help="Actualiza solo Luma3DS."),
    gm9_only: bool = typer.Option(False, "--gm9-only", help="Actualiza solo GodMode9."),
    sd_path: Optional[Path] = typer.Option(None, "--sd-path", help="Ruta manual a la SD si no se detecta automáticamente."),
) -> None:
    """Descarga e instala Luma3DS y/o GodMode9 en la SD de forma segura."""
    from tds_up import core, cleaner, network
    from tds_up.utils import extract_zip_bytes, cleanup_temp_dir

    if not latest:
        console.print("[red]Usa --latest para descargar la última versión.[/red]")
        raise typer.Exit(1)

    console.print(Panel("[bold cyan]3ds-up — Actualizador seguro para Nintendo 3DS[/bold cyan]"))

    # 1. Detectar SD
    console.print("\n[bold]1. Detectando SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detectada: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    # 2. Backup
    console.print("\n[bold]2. Creando backup de configuración...[/bold]")
    backup_dir = core.create_backup(sd)
    console.print(f"  [green]✓[/green] Backup guardado en: {backup_dir}")

    # 3. Descargar y aplicar
    try:
        if not gm9_only:
            _install_luma(sd, core, network, extract_zip_bytes, cleanup_temp_dir)

        if not luma_only:
            _install_gm9(sd, core, network, extract_zip_bytes, cleanup_temp_dir)

        # 4. Limpiar basura de macOS
        console.print("\n[bold]4. Limpiando archivos macOS de la SD...[/bold]")
        removed = cleaner.clean_macos_junk(sd)
        cleaner.reset_archive_bits(sd)
        console.print(f"  [green]✓[/green] {removed} archivos basura eliminados")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        console.print("[yellow]Restaurando backup...[/yellow]")
        core.restore_backup(backup_dir, sd)
        raise typer.Exit(1)

    console.print(Panel("[bold green]¡Actualización completada! Inserta la SD en tu 3DS.[/bold green]"))


def _install_luma(sd, core, network, extract_zip_bytes, cleanup_temp_dir):
    console.print("\n[bold]3a. Descargando Luma3DS...[/bold]")
    asset = network.get_latest_luma()
    console.print(f"  [green]✓[/green] Versión encontrada: {asset.version}")

    with console.status(f"  Descargando {asset.name}..."):
        data = network.download_asset(asset)

    tmp = extract_zip_bytes(data)
    try:
        console.print("  Aplicando Smart Merge...")
        core.smart_merge(tmp, sd)
    finally:
        cleanup_temp_dir(tmp)


def _install_gm9(sd, core, network, extract_zip_bytes, cleanup_temp_dir):
    console.print("\n[bold]3b. Descargando GodMode9...[/bold]")
    asset = network.get_latest_gm9()
    console.print(f"  [green]✓[/green] Versión encontrada: {asset.version}")

    with console.status(f"  Descargando {asset.name}..."):
        data = network.download_asset(asset)

    tmp = extract_zip_bytes(data)
    try:
        console.print("  Aplicando Smart Merge...")
        core.smart_merge(tmp, sd)
    finally:
        cleanup_temp_dir(tmp)


@app.command(name="fix-archive-bit")
def fix_archive_bit(
    sd_path: Optional[Path] = typer.Argument(None, help="Ruta a la SD. Si no se indica, se auto-detecta."),
) -> None:
    """Elimina archivos basura de macOS de la SD sin actualizar nada."""
    from tds_up import core, cleaner

    console.print(Panel("[bold cyan]3ds-up — Limpieza de archivos macOS[/bold cyan]"))

    console.print("\n[bold]Detectando SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detectada: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold]Limpiando...[/bold]")
    removed = cleaner.clean_macos_junk(sd)
    cleaner.reset_archive_bits(sd)

    console.print(Panel(f"[bold green]Limpieza completada. {removed} archivos eliminados.[/bold green]"))


@app.command()
def install(
    zip_file: Path = typer.Argument(..., help="Ruta al archivo ZIP a instalar."),
    sd_path: Optional[Path] = typer.Option(None, "--sd-path", help="Ruta manual a la SD."),
) -> None:
    """Instala un ZIP local (Luma3DS, GodMode9, etc.) en la SD de forma segura."""
    from tds_up import core, cleaner
    from tds_up.utils import extract_zip, cleanup_temp_dir

    console.print(Panel("[bold cyan]3ds-up — Instalación desde archivo local[/bold cyan]"))

    if not zip_file.exists():
        console.print(f"  [red]✗[/red] Archivo no encontrado: {zip_file}")
        raise typer.Exit(1)

    console.print("\n[bold]1. Detectando SD...[/bold]")
    try:
        sd = core.detect_sd_card(sd_path)
        console.print(f"  [green]✓[/green] SD detectada: {sd}")
    except FileNotFoundError as e:
        console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold]2. Creando backup...[/bold]")
    backup_dir = core.create_backup(sd)

    try:
        console.print("\n[bold]3. Extrayendo e instalando...[/bold]")
        tmp = extract_zip(zip_file)
        try:
            core.smart_merge(tmp, sd)
        finally:
            cleanup_temp_dir(tmp)

        console.print("\n[bold]4. Limpiando archivos macOS...[/bold]")
        removed = cleaner.clean_macos_junk(sd)
        cleaner.reset_archive_bits(sd)
        console.print(f"  [green]✓[/green] {removed} archivos basura eliminados")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        console.print("[yellow]Restaurando backup...[/yellow]")
        core.restore_backup(backup_dir, sd)
        raise typer.Exit(1)

    console.print(Panel("[bold green]¡Instalación completada![/bold green]"))
