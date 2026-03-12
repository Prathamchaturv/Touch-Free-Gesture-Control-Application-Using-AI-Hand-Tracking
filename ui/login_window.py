"""
Module: login_window.py
Description: Optional login dialog shown before the main MMGI dashboard.
             Credentials are loaded from config/users.json; passwords are
             stored as SHA-256 hashes (never in plaintext).
Author: Pratham Chaturvedi

Behaviour
---------
* If config/users.json is missing or ``"enabled": false``, login is skipped
  and this module returns Accepted immediately.
* On incorrect credentials a red error message is shown; the dialog is NOT
  closed so the user can retry.
* On three consecutive failures the Login button is disabled for 5 seconds
  (brute-force throttle).
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QFont
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
)

_USERS_PATH = Path(__file__).parent.parent / 'config' / 'users.json'
_MAX_ATTEMPTS  = 3      # failed attempts before temporary lockout
_LOCKOUT_SECS  = 5      # lockout duration in seconds


def _hash_pw(password: str) -> str:
    """Return the SHA-256 hex digest of *password*."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def _load_users() -> dict:
    """
    Load users.json.  Returns an empty dict (login disabled) on any error.
    """
    try:
        with open(_USERS_PATH, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def login_is_enabled() -> bool:
    """Return True when the login screen should be shown."""
    data = _load_users()
    return bool(data.get('enabled', False))


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

_QSS = """
QDialog {
    background: #0d0d1a;
}
QLabel#title {
    color: #00e5ff;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 2px;
}
QLabel#subtitle {
    color: #8888aa;
    font-size: 11px;
    letter-spacing: 1px;
}
QLabel#field_label {
    color: #ccccdd;
    font-size: 12px;
}
QLineEdit {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    color: #e0e0ff;
    font-size: 13px;
    padding: 7px 10px;
}
QLineEdit:focus {
    border: 1px solid #00e5ff;
}
QPushButton#login_btn {
    background: #00e5ff;
    color: #0d0d1a;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 9px 0;
}
QPushButton#login_btn:hover {
    background: #33edff;
}
QPushButton#login_btn:disabled {
    background: #2a2a4a;
    color: #555577;
}
QLabel#error_label {
    color: #ff4466;
    font-size: 11px;
}
QLabel#success_label {
    color: #00ff88;
    font-size: 11px;
}
QFrame#divider {
    background: #2a2a4a;
    max-height: 1px;
}
"""


class LoginWindow(QDialog):
    """
    Simple login dialog.

    Call ``LoginWindow.should_show()`` first; if False, skip instantiation.
    ``exec()`` returns ``QDialog.DialogCode.Accepted`` on success.
    """

    @staticmethod
    def should_show() -> bool:
        """Return True when the login screen is enabled in users.json."""
        return login_is_enabled()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('MMGI — Login')
        self.setFixedSize(360, 320)
        self.setStyleSheet(_QSS)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint
        )

        self._users  = _load_users()
        self._attempts = 0
        self._locked   = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(0)

        # Title
        title = QLabel('MMGI')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        root.addSpacing(2)

        subtitle = QLabel('MULTI-MODAL GESTURE INTELLIGENCE')
        subtitle.setObjectName('subtitle')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        root.addSpacing(20)

        div = QFrame()
        div.setObjectName('divider')
        root.addWidget(div)

        root.addSpacing(20)

        # Username
        user_lbl = QLabel('Username')
        user_lbl.setObjectName('field_label')
        root.addWidget(user_lbl)
        root.addSpacing(5)

        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText('Enter username')
        self._username_edit.returnPressed.connect(self._on_login)
        root.addWidget(self._username_edit)

        root.addSpacing(14)

        # Password
        pw_lbl = QLabel('Password')
        pw_lbl.setObjectName('field_label')
        root.addWidget(pw_lbl)
        root.addSpacing(5)

        self._password_edit = QLineEdit()
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_edit.setPlaceholderText('Enter password')
        self._password_edit.returnPressed.connect(self._on_login)
        root.addWidget(self._password_edit)

        root.addSpacing(8)

        # Error / status message
        self._msg_label = QLabel('')
        self._msg_label.setObjectName('error_label')
        self._msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg_label.setFixedHeight(18)
        root.addWidget(self._msg_label)

        root.addSpacing(10)

        # Login button
        self._login_btn = QPushButton('Login')
        self._login_btn.setObjectName('login_btn')
        self._login_btn.clicked.connect(self._on_login)
        root.addWidget(self._login_btn)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _on_login(self) -> None:
        if self._locked:
            return

        username = self._username_edit.text().strip()
        password = self._password_edit.text()

        # Basic presence check
        if not username or not password:
            self._show_error('Please enter both username and password.')
            return

        stored_user = self._users.get('username', '')
        stored_hash = self._users.get('password', '')

        if username == stored_user and _hash_pw(password) == stored_hash:
            self._msg_label.setObjectName('success_label')
            self._msg_label.setText('Access granted.')
            self._msg_label.setStyleSheet('color: #00ff88; font-size: 11px;')
            # Brief pause so the user sees the confirmation, then accept
            QTimer.singleShot(300, self.accept)
        else:
            self._attempts += 1
            remaining = _MAX_ATTEMPTS - self._attempts
            if remaining > 0:
                self._show_error(
                    f'Invalid credentials. {remaining} attempt(s) remaining.'
                )
            else:
                self._lock_temporarily()

    def _show_error(self, message: str) -> None:
        self._msg_label.setStyleSheet('color: #ff4466; font-size: 11px;')
        self._msg_label.setText(message)

    def _lock_temporarily(self) -> None:
        """Disable the login button for _LOCKOUT_SECS seconds."""
        self._locked = True
        self._login_btn.setEnabled(False)
        self._show_error(
            f'Too many failed attempts. Try again in {_LOCKOUT_SECS}s.'
        )
        QTimer.singleShot(_LOCKOUT_SECS * 1000, self._unlock)

    def _unlock(self) -> None:
        self._locked    = False
        self._attempts  = 0
        self._login_btn.setEnabled(True)
        self._msg_label.setText('')
        self._password_edit.clear()
        self._password_edit.setFocus()
