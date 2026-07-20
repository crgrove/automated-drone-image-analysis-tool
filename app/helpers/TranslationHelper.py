"""Translation resolution and loading.

Selects the UI language and locates the compiled ``.qm`` files in a way
that works identically from source and from a PyInstaller build on both
Windows and macOS. The single source of truth for the bundled data
directory is ``sys._MEIPASS`` (``_internal`` on Windows onedir,
``Contents/Frameworks`` inside a macOS ``.app``) — never a hard-coded
platform path.
"""

import os
import sys

from PySide6.QtCore import QLocale, QTranslator

# Languages that ship compiled .qm files. English is the source language
# (no translation needed), so selecting it means "install no translator".
SUPPORTED_LANGUAGES = ('en', 'es', 'it', 'nl')
DEFAULT_LANGUAGE = 'en'


def translations_dir():
    """Return the directory holding the ``app_<lang>.qm`` files.

    Frozen builds keep bundled data under ``sys._MEIPASS`` on every
    platform; from source the files live in ``<repo>/translations``
    (one level above this ``app/helpers`` package).
    """
    base = getattr(sys, '_MEIPASS', None)
    if base:
        return os.path.join(base, 'translations')
    # app/helpers/TranslationHelper.py -> repo root is three levels up.
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )
    return os.path.join(repo_root, 'translations')


def resolve_language(saved_language, system_locale_name=None):
    """Choose the UI language by priority: saved setting → system locale → English.

    Args:
        saved_language: The persisted ``Language`` setting, or None/'' if unset.
        system_locale_name: A locale name like ``"es_ES"`` (defaults to the
            OS locale). Injectable for tests.

    Returns:
        A supported language code from :data:`SUPPORTED_LANGUAGES`.
    """
    # 1. An explicit, supported saved choice always wins (including 'en',
    #    so a user on a non-English OS can force English).
    if saved_language and saved_language in SUPPORTED_LANGUAGES:
        return saved_language

    # 2. Fall back to the operating-system locale when no valid saved choice.
    if system_locale_name is None:
        system_locale_name = QLocale.system().name()
    system_lang = (system_locale_name or '').split('_')[0]
    if system_lang in SUPPORTED_LANGUAGES:
        return system_lang

    # 3. Otherwise English.
    return DEFAULT_LANGUAGE


def install_translator(app, saved_language, system_locale_name=None, translator=None):
    """Resolve the language and install its translator on ``app``.

    English installs no translator (it is the source language). The
    translator is stored on ``app`` to keep it alive past this call.

    Returns:
        The chosen language code, regardless of whether a translator was
        installed.
    """
    language = resolve_language(saved_language, system_locale_name)
    if language == DEFAULT_LANGUAGE:
        return language

    translator = translator or QTranslator(app)
    if translator.load(f"app_{language}", translations_dir()):
        app.installTranslator(translator)
        app._translator = translator  # prevent garbage collection
    return language
