"""Tests for the Windows desktop pet Qt application.

Uses pytest-qt to verify basic window flags and tray menu actions.
"""

import pytest
from PyQt5 import QtCore  # fallback to PySide6 inside code if PyQt5 unavailable
from pico.desktop.pet_app import PetWindow, PetTrayIcon

def test_pet_window_flags(qtbot):
    tray = PetTrayIcon()
    window = PetWindow(tray)
    qtbot.addWidget(window)
    flags = window.windowFlags()
    assert flags & QtCore.Qt.FramelessWindowHint
    assert flags & QtCore.Qt.WindowStaysOnTopHint
    assert flags & QtCore.Qt.Tool

def test_tray_menu_contains_actions(qtbot):
    tray = PetTrayIcon()
    window = PetWindow(tray)
    tray.set_window(window)
    actions = [a.text() for a in tray.menu.actions()]
    # Show/Hide action should be present
    assert any('Show' in a or 'Hide' in a for a in actions)
    # Click‑Through toggle action
    assert any('Click' in a for a in actions)
    # Quit action
    assert any('Quit' in a for a in actions)
