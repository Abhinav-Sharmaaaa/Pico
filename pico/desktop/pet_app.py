"""Qt application for the desktop pet.

The pet is a frameless, transparent window that shows an animated
sprite sequence. It stays on top of other windows, can be dragged by the
mouse, and supports a click‑through mode toggled from the system‑tray icon.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Import Qt – try PyQt5 first, fall back to PySide6
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:  # pragma: no cover
    from PySide6 import QtCore, QtGui, QtWidgets

# Load configuration defaults – these are added to pico.config.py
from pico import config as cfg
from pico.config import load_config

config = load_config()

# ---------------------------------------------------------------------------
# Helper to load sprite frames from the compiled Qt resource file.
# ---------------------------------------------------------------------------

def _load_frames(prefix: str, count: int) -> List[QtGui.QPixmap]:
    """Load QPixmap frames from the *sprites* directory.

    ``prefix`` should be the base filename without the index, e.g. ``"Pico_idle_frame"``.
    The function looks for PNG files in the sibling ``sprites`` folder next to this
    module. This avoids the need for a compiled ``.qrc`` resource at runtime.
    """
    base_dir = Path(__file__).parent / "sprites"
    frames: List[QtGui.QPixmap] = []
    for i in range(1, count + 1):
        path = base_dir / f"{prefix}{i}.png"
        pix = QtGui.QPixmap(str(path))
        if not pix.isNull():
            scale = config.get("PET_SCALE", 1.0)
            if scale != 1.0:
                size = pix.size()
                pix = pix.scaled(
                    int(size.width() * scale),
                    int(size.height() * scale),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            frames.append(pix)
    return frames
    """Load a list of QPixmap objects.

    ``prefix`` is the resource path without the frame number and extension,
    e.g. ``":/sprites/Pico_idle_frame"``. ``count`` is how many sequential
    frames exist.
    """
    frames: List[QtGui.QPixmap] = []
    for i in range(1, count + 1):
        path = f"{prefix}{i}.png"
        pix = QtGui.QPixmap(path)
        if not pix.isNull():
            # Apply user scaling factor
            scale = config.get("PET_SCALE", 1.0)
            if scale != 1.0:
                size = pix.size()
                pix = pix.scaled(
                    int(size.width() * scale),
                    int(size.height() * scale),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            frames.append(pix)
    return frames


# ---------------------------------------------------------------------------
# Main window that displays the pet animation.
# ---------------------------------------------------------------------------

class PetWindow(QtWidgets.QWidget):
    """A frameless, transparent window that cycles sprite frames.

    The window can be dragged with the mouse and switches to a sleep
    animation after a period of inactivity defined by ``cfg.PET_IDLE_TIMEOUT``.
    """

    def __init__(self, tray: "PetTrayIcon | None" = None) -> None:
        super().__init__(parent=None)
        self.tray = tray
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool  # No taskbar entry
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        # Click‑through default from config
        config_dict = load_config()
        self.setAttribute(
            QtCore.Qt.WA_TransparentForMouseEvents,
            config_dict.get("PET_CLICK_THROUGH_DEFAULT", False),
        )

        # Load animation frames
        self.idle_frames = _load_frames(":/sprites/Pico_idle_frame", 6)
        self.sleep_frames = _load_frames(":/sprites/Pico_sleep_frame", 6)
        self.current_frames = self.idle_frames
        self.frame_index = 0

        # QLabel to show the pixmap
        self.label = QtWidgets.QLabel(self)
        self.label.setPixmap(self.current_frames[0])
        self.label.setScaledContents(True)
        self.resize(self.current_frames[0].size())

        # Timers
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self._next_frame)
        self.animation_timer.start(30)  # ~33 fps

        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self._enter_sleep)
        self._reset_idle_timer()

        # Drag handling state
        self._drag_pos: QtCore.QPoint | None = None

        # Position the window at the configured default location
        default_x, default_y = cfg.PET_DEFAULT_POS
        self.move(default_x, default_y)

    # -------------------------------------------------------------------
    # Animation handling
    # -------------------------------------------------------------------
    def _next_frame(self) -> None:
        self.frame_index = (self.frame_index + 1) % len(self.current_frames)
        self.label.setPixmap(self.current_frames[self.frame_index])

    def _reset_idle_timer(self) -> None:
        """Reset the timer that triggers the sleep animation."""
        self.idle_timer.start(cfg.PET_IDLE_TIMEOUT * 1000)
        if self.current_frames is self.sleep_frames:
            # Switch back to idle animation if we were sleeping
            self.current_frames = self.idle_frames
            self.frame_index = 0

    def _enter_sleep(self) -> None:
        """Switch to the sleep animation sequence."""
        if self.sleep_frames:
            self.current_frames = self.sleep_frames
            self.frame_index = 0

    # -------------------------------------------------------------------
    # Mouse interaction – dragging and double‑click to toggle sleep/idle
    # -------------------------------------------------------------------
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # pragma: no cover – UI
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # pragma: no cover – UI
        if self._drag_pos is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # pragma: no cover – UI
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:  # pragma: no cover – UI
        # Double‑click toggles between idle and sleep instantly.
        if self.current_frames is self.idle_frames:
            self._enter_sleep()
        else:
            self.current_frames = self.idle_frames
            self.frame_index = 0
        self._reset_idle_timer()
        super().mouseDoubleClickEvent(event)

    # -------------------------------------------------------------------
    # Public API for the tray icon to toggle click‑through mode.
    # -------------------------------------------------------------------
    def set_click_through(self, enabled: bool) -> None:
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, enabled)
        if self.tray:
            self.tray.update_menu()


# ---------------------------------------------------------------------------
# System‑tray integration.
# ---------------------------------------------------------------------------

class PetTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        # Use the first idle sprite as the tray icon
        icon_pix = QtGui.QIcon(":/sprites/Pico_idle_frame1.png")
        super().__init__(icon_pix, parent)
        self.window: PetWindow | None = None
        self.menu = QtWidgets.QMenu()
        self.update_menu()
        self.setContextMenu(self.menu)
        self.activated.connect(self._on_activated)
        self.show()

    def set_window(self, win: PetWindow) -> None:
        self.window = win

    def _on_activated(self, reason: QtWidgets.QSystemTrayIcon.ActivationReason) -> None:  # pragma: no cover
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            # Left‑click toggles visibility
            if self.window:
                if self.window.isVisible():
                    self.window.hide()
                else:
                    self.window.show()

    def _toggle_click_through(self) -> None:
        if self.window:
            current = self.window.testAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.window.set_click_through(not current)

    def _quit(self) -> None:
        QtWidgets.QApplication.quit()

    def update_menu(self) -> None:
        self.menu.clear()
        if self.window:
            if self.window.isVisible():
                hide_action = self.menu.addAction("Hide")
                hide_action.triggered.connect(self.window.hide)
            else:
                show_action = self.menu.addAction("Show")
                show_action.triggered.connect(self.window.show)
            ct_action = self.menu.addAction(
                "Click‑Through: " + ("On" if self.window.testAttribute(QtCore.Qt.WA_TransparentForMouseEvents) else "Off")
            )
            ct_action.triggered.connect(self._toggle_click_through)
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self._quit)


# ---------------------------------------------------------------------------
# Public entry point used by the CLI wrapper.
# ---------------------------------------------------------------------------

def run_pet() -> None:
    """Start the Qt event loop and show the pet.

    This function is imported by ``pico.desktop.pet_cli`` and also serves as a
    convenient hook for tests.
    """
    app = QtWidgets.QApplication(sys.argv)
    # Enable high‑DPI scaling for crisp sprites on modern displays.
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    tray = PetTrayIcon()
    window = PetWindow(tray)
    tray.set_window(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    run_pet()
