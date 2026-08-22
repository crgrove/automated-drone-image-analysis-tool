"""
WaldoFlightLogDecisions - Per-folder persistence of flight-log choices.

Remembers, per image folder, whether the operator attached (or declined) a
ForeFlight track log, and which file it was - so re-opens silently re-apply
to any new files instead of re-asking, mirroring WaldoClockDecisions.

Decision payload shape:
    {'decision': 'accepted', 'log_path': str}   or   {'decision': 'declined'}
"""

import json
from typing import Optional

from core.services.SettingsService import SettingsService
from core.services.waldo.WaldoClockDecisions import folder_key_for  # noqa: F401  (re-exported)

FLIGHTLOG_DECISIONS_SETTING = 'WaldoFlightLogs'


def get_decisions(settings_service: Optional[SettingsService] = None) -> dict:
    """All stored per-folder decisions ({folder_key: decision_dict})."""
    settings_service = settings_service or SettingsService()
    raw = settings_service.get_setting(FLIGHTLOG_DECISIONS_SETTING)
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
    settings_service.set_setting(FLIGHTLOG_DECISIONS_SETTING, json.dumps(decisions))


def clear_decision(folder_key: str,
                   settings_service: Optional[SettingsService] = None):
    """Remove the stored decision for one folder (detach flow)."""
    settings_service = settings_service or SettingsService()
    decisions = get_decisions(settings_service)
    if folder_key in decisions:
        del decisions[folder_key]
        settings_service.set_setting(FLIGHTLOG_DECISIONS_SETTING, json.dumps(decisions))
