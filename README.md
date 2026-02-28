# 3ds-up

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

A safe, automated SD card manager for Nintendo 3DS homebrew on macOS.

## Why does this exist?

Managing a hacked 3DS SD card from a Mac has the same silent dangers as the Switch — macOS injects hidden files (`.DS_Store`, `._*` files, extended attributes) that corrupt your SD and cause boot failures. On top of that, Finder's "Replace" behavior destroys folders instead of merging them, which can wipe your Luma3DS configuration in one careless drag.

**3ds-up** automates the entire process safely:

1. **Backs up** your `luma/config.ini` before touching anything
2. **Smart Merges** new files onto your SD without deleting existing content
3. **Cleans** all macOS junk files that would corrupt the 3DS
4. **Restores** your backup automatically if anything goes wrong
5. **Never touches** `Nintendo 3DS/` (encrypted game data) or `boot9strap/` (bootloader)

## Installation

### From PyPI

```bash
pip install 3ds-up
```

### From source

```bash
git clone https://github.com/OscarCampohermoso/3ds-up.git
cd 3ds-up
pip install -e .
```

## Requirements

- Python 3.8 or higher
- macOS (designed specifically for macOS-related SD card issues)

## Usage

### Update Luma3DS and GodMode9 to the latest version

Downloads the latest releases from GitHub and installs them safely to your SD card.

```bash
3ds-up update --latest
```

The tool will auto-detect your SD card if it's mounted at `/Volumes/`. If you have multiple SD cards or a custom mount point, specify the path:

```bash
3ds-up update --latest --sd-path /Volumes/MY_SD
```

### Update only Luma3DS (skip GodMode9)

```bash
3ds-up update --latest --luma-only
```

### Update only GodMode9 (skip Luma3DS)

```bash
3ds-up update --latest --gm9-only
```

### Install a local ZIP file

If you already downloaded a release ZIP manually:

```bash
3ds-up install ./Luma3DSv13.3.zip --sd-path /Volumes/MY_SD
```

### Clean macOS junk files only (no update)

Just remove the hidden files macOS left behind, without updating anything:

```bash
3ds-up fix-archive-bit /Volumes/MY_SD
```

## What happens during an update?

```
1. Backup     → Saves luma/config.ini to ~/.3ds-up/backups/ (timestamped)
2. Download   → Fetches latest Luma3DS and GodMode9 ZIPs from GitHub
3. Smart Merge → Copies new files to SD, preserving your existing content
                 Nintendo 3DS/ and boot9strap/ are NEVER touched
4. Cleanup    → Removes .DS_Store, ._* files, __MACOSX/, and xattrs
5. Done       → If anything fails at step 3, your backup is auto-restored
```

## Protected Paths

These paths are **never modified** under any circumstances:

| Path | Why |
|---|---|
| `Nintendo 3DS/` | Encrypted with your console's unique AES key — modifying corrupts all game data |
| `boot9strap/` | Core bootloader — deleting this bricks your console |

## Configuration Backups

Before every operation, 3ds-up saves your critical config files to:

```
~/.3ds-up/backups/20260228_143000/
└── luma/
    └── config.ini
```

## Commands Reference

| Command | Description |
|---|---|
| `3ds-up update --latest` | Download and install the latest Luma3DS + GodMode9 |
| `3ds-up update --latest --luma-only` | Download and install only Luma3DS |
| `3ds-up update --latest --gm9-only` | Download and install only GodMode9 |
| `3ds-up install <zip>` | Install a local ZIP file to the SD card |
| `3ds-up fix-archive-bit [path]` | Clean macOS junk files from the SD card |
| `3ds-up --version` | Show the current version |
| `3ds-up --help` | Show help for all commands |

## Platform Support

Currently, **3ds-up is macOS-only**. The tool was built specifically to address the hidden-file injection and destructive replace behavior unique to macOS.

Windows and Linux users don't face the same corruption risks, but could still benefit from the automated download and Smart Merge workflow. Contributions targeting cross-platform support are welcome — the core logic in `core.py` is already platform-agnostic.

## License


GPLv3 — See [LICENSE](LICENSE) for details.

---

## Related Projects

- [switch-up GitHub repository](https://github.com/OscarCampohermoso/switch-up.git)
