"""
ThemeHelper - Centralised application of the qdarktheme theme.

``qdarktheme.setup_theme()`` applies the theme as a *stylesheet* plus a
**minimal** palette. In stylesheet mode qdarktheme only sets the ``Text`` and
``Link`` palette roles reliably; it deliberately leaves ``WindowText``,
``ButtonText``, ``Mid`` and friends unset, so those roles fall back to the Qt
platform palette. On Qt 6.7+ that platform palette follows the operating
system's light/dark setting.

The practical consequence: any widget that reads one of those unset roles
(custom ``paintEvent`` painters, or stylesheets using ``palette(button-text)``)
renders with an OS-dependent colour. On a machine whose Windows is in *light*
mode the text comes out near-black even though the app is showing the dark
theme -- which is why the wizard slider labels and some buttons appeared black
"on some computers" only.

Applying the *full* palette (``load_palette`` with ``for_stylesheet=False``)
in addition to the stylesheet pins ``WindowText``/``ButtonText``/``Mid`` to the
theme's own colours, so every widget renders consistently regardless of the OS
setting. This module is the single place that does both, so all theme-apply
call sites stay in sync.
"""

import qdarktheme
from PySide6.QtWidgets import QApplication


def normalize_theme(theme):
    """Normalise a theme name to qdarktheme's ``"dark"``/``"light"`` values.

    Args:
        theme: Theme name in any casing (e.g. ``"Dark"``, ``"light"``) or None.

    Returns:
        str: ``"light"`` when the input is light, otherwise ``"dark"``
        (dark is the default for unknown/empty input).
    """
    return "light" if str(theme or "").strip().lower() == "light" else "dark"


def apply_theme(theme="dark"):
    """Apply the qdarktheme stylesheet *and* the full palette for ``theme``.

    Use this instead of calling ``qdarktheme.setup_theme()`` directly so that
    the application palette (``WindowText``, ``ButtonText``, ``Mid`` ...) is
    always pinned to the theme rather than left to follow the OS light/dark
    setting.

    Args:
        theme: Theme name (``"Dark"``/``"Light"`` or ``"dark"``/``"light"``).

    Returns:
        str: The normalised theme actually applied (``"dark"`` or ``"light"``).
    """
    normalized = normalize_theme(theme)
    qdarktheme.setup_theme(normalized)
    app = QApplication.instance()
    if app is not None:
        # for_stylesheet defaults to False here, so this is the *full* palette
        # (unlike the minimal one setup_theme installs internally).
        app.setPalette(qdarktheme.load_palette(normalized))
    return normalized
