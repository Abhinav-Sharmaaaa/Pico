"""Command‑line entry point for the desktop pet.

The ``pico pet`` sub‑command (or the console script ``pico-pet``) imports
this module and calls ``main()``.  The function ensures that the optional auto‑
start shortcut is created on Windows when ``cfg.PET_AUTO_START`` is true, then
starts the Qt pet application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Load configuration – the defaults were added to ``pico/config.py``.
from pico import config as cfg

# Import the Qt entry point.
from .pet_app import run_pet


def _startup_shortcut_path() -> Path:
    """Return the path of the ``pico‑pet`` shortcut in the user Startup folder.

    The shortcut is a small ``.cmd`` file that runs the ``pico-pet`` console
    script.  Using a ``.cmd`` avoids the need for COM‑level ``.lnk`` creation
    (which would require ``pywin32``).  The file is created only when the
    ``PET_AUTO_START`` flag is true.
    """
    startup_dir = Path(os.getenv("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return startup_dir / "pico-pet.cmd"


def _ensure_autostart() -> None:
    """Create a ``pico-pet`` auto‑start shortcut if it does not already exist.

    The function is safe to call multiple times; it will not overwrite an
    existing shortcut unless the user explicitly deletes it.
    """
    if not cfg.PET_AUTO_START:
        return
    shortcut = _startup_shortcut_path()
    if shortcut.exists():
        return
    # Ensure the startup folder exists – on a minimal Windows install it should.
    shortcut.parent.mkdir(parents=True, exist_ok=True)
    # Write a simple command script that invokes the console entry point.
    # ``pico-pet`` is expected to be on the PATH after installation.
    script = "@echo off\r\n" f"{sys.executable} -m pico.desktop.pet_cli %*\r\n"
    try:
        shortcut.write_text(script, encoding="utf-8")
    except OSError:
        # If writing fails (e.g., permissions), we silently ignore – the user can
        # create the shortcut manually.
        pass


def main() -> None:
    """Entry point invoked by the CLI sub‑command.

    1. Ensure the auto‑start shortcut if the configuration requests it.
    2. Run the Qt pet application.
    """
    try:
        _ensure_autostart()
    finally:
        # Run the pet regardless of shortcut creation outcome.
        run_pet()


if __name__ == "__main__":  # pragma: no cover
    main()
