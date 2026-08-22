"""
WaldoClockDecisions - Per-folder persistence of clock-correction choices.

Stores the operator's accept/decline decision (and the accepted values) for
each image folder in application settings, so the pre-pass neither re-asks
on every open nor silently re-applies stale values after an amendment.
Shared by WaldoPrePassController (folder-open flow) and the Person
Reference dialog's manual "Adjust clock" flow.
"""

import json
import os
from typing import Optional

from core.services.SettingsService import SettingsService

CLOCK_DECISIONS_SETTING = 'WaldoClockCorrections'


def folder_key_for(path: str) -> str:
    """Canonical settings key for the folder containing an image path."""
    return os.path.normcase(os.path.abspath(os.path.dirname(path)))


def get_decisions(settings_service: Optional[SettingsService] = None) -> dict:
    """All stored per-folder decisions ({folder_key: decision_dict})."""
    settings_service = settings_service or SettingsService()
    raw = settings_service.get_setting(CLOCK_DECISIONS_SETTING)
    if not raw:
        return {}
    try:
        decisions = json.loads(raw)
        return decisions if isinstance(decisions, dict) else {}
    except (TypeError, ValueError):
        return {}


def get_decision(folder_key: str,
                 settings_service: Optional[SettingsService] = None) -> Optional[dict]:
    """The stored decision for one folder, or None."""
    return get_decisions(settings_service).get(folder_key)


def store_decision(folder_key: str, decision: dict,
                   settings_service: Optional[SettingsService] = None):
    """Persist (or overwrite) the decision for one folder."""
    settings_service = settings_service or SettingsService()
    decisions = get_decisions(settings_service)
    decisions[folder_key] = decision
    settings_service.set_setting(CLOCK_DECISIONS_SETTING, json.dumps(decisions))
