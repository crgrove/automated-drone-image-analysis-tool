"""Tests for TranslationHelper: language resolution, .qm path, install.

QApplication/QTranslator are faked so the priority logic and frozen-path
resolution are testable on any platform without a display or real .qm files.
"""

import os
import sys

import pytest

from helpers import TranslationHelper
from helpers.TranslationHelper import (
    resolve_language,
    translations_dir,
    install_translator,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
)


# ---------------------------------------------------------------------------
# resolve_language — priority: saved -> system locale -> English
# ---------------------------------------------------------------------------

def test_saved_supported_language_wins():
    assert resolve_language('it', system_locale_name='es_ES') == 'it'


def test_saved_english_forces_english_on_non_english_os():
    """A user on a Spanish OS can pin the app to English."""
    assert resolve_language('en', system_locale_name='es_ES') == 'en'


def test_falls_back_to_system_locale_when_unset():
    assert resolve_language(None, system_locale_name='es_ES') == 'es'
    assert resolve_language('', system_locale_name='nl_NL') == 'nl'


def test_unsupported_saved_language_falls_through_to_system():
    assert resolve_language('fr', system_locale_name='it_IT') == 'it'


def test_unsupported_system_locale_defaults_to_english():
    assert resolve_language(None, system_locale_name='fr_FR') == 'en'


def test_empty_system_locale_defaults_to_english():
    assert resolve_language(None, system_locale_name='') == DEFAULT_LANGUAGE


def test_bare_language_code_without_region():
    assert resolve_language(None, system_locale_name='es') == 'es'


# ---------------------------------------------------------------------------
# translations_dir — source vs frozen (sys._MEIPASS)
# ---------------------------------------------------------------------------

def test_translations_dir_from_source(monkeypatch):
    monkeypatch.delattr(sys, '_MEIPASS', raising=False)
    result = translations_dir()
    assert result.endswith(os.path.join('translations'))
    # Points at the repo-level translations dir (sibling of app/), not app/helpers.
    assert os.path.basename(os.path.dirname(result)) != 'helpers'


def test_translations_dir_when_frozen(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    assert translations_dir() == os.path.join(str(tmp_path), 'translations')


# ---------------------------------------------------------------------------
# install_translator — English installs nothing; others load + install
# ---------------------------------------------------------------------------

class _FakeApp:
    def __init__(self):
        self.installed = []

    def installTranslator(self, translator):
        self.installed.append(translator)


class _FakeTranslator:
    def __init__(self, load_ok=True):
        self._load_ok = load_ok
        self.loaded = None

    def load(self, name, directory):
        self.loaded = (name, directory)
        return self._load_ok


def test_install_english_installs_no_translator():
    app = _FakeApp()
    lang = install_translator(app, 'en', system_locale_name='en_US',
                              translator=_FakeTranslator())
    assert lang == 'en'
    assert app.installed == []
    assert not hasattr(app, '_translator')


def test_install_non_english_loads_and_installs():
    app = _FakeApp()
    tr = _FakeTranslator(load_ok=True)
    lang = install_translator(app, 'es', system_locale_name='en_US', translator=tr)
    assert lang == 'es'
    assert tr.loaded[0] == 'app_es'
    assert app.installed == [tr]
    assert app._translator is tr


def test_install_returns_language_even_when_qm_missing():
    """A missing .qm still reports the resolved language but installs nothing."""
    app = _FakeApp()
    tr = _FakeTranslator(load_ok=False)
    lang = install_translator(app, 'nl', system_locale_name='en_US', translator=tr)
    assert lang == 'nl'
    assert app.installed == []


def test_install_uses_system_locale_when_unset():
    app = _FakeApp()
    tr = _FakeTranslator(load_ok=True)
    lang = install_translator(app, None, system_locale_name='it_IT', translator=tr)
    assert lang == 'it'
    assert tr.loaded[0] == 'app_it'


def test_supported_languages_shape():
    """English is the source language and must be in the supported set."""
    assert DEFAULT_LANGUAGE == 'en'
    assert 'en' in SUPPORTED_LANGUAGES
    assert set(SUPPORTED_LANGUAGES) == {'en', 'es', 'it', 'nl'}
