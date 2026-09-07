"""Every image algorithm service must name itself correctly.

``AlgorithmService.name`` is a public identifier, and two services shipped
for a long time announcing themselves as ``MatchedFilter`` because their
constructors were copied from it. Nothing in production reads the field
today - the results XML takes its ``algorithm`` attribute from
``algorithms.conf`` instead - which is exactly why the drift went unnoticed
and why a wrong value is dangerous rather than merely untidy: the first
consumer to trust it (a log line, a report header, a per-algorithm branch)
inherits a lie about which algorithm produced a detection.

This test walks the registry rather than listing names, so a new algorithm
is covered the day it is added.
"""

import inspect
import json
import os

import pytest

from core.services.AnalyzeService import AnalyzeService

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
    'algorithms.conf',
)


def _image_algorithms():
    with open(CONFIG_PATH, encoding='utf-8') as handle:
        return json.load(handle)['algorithms']


ALGORITHMS = _image_algorithms()


def test_the_registry_was_actually_read():
    """A silently empty parametrisation would make every case below vacuous."""
    assert len(ALGORITHMS) >= 9


@pytest.mark.parametrize('algorithm', ALGORITHMS, ids=lambda a: a['name'])
def test_service_module_lives_where_the_config_says(algorithm):
    service_class = AnalyzeService._resolve_algorithm_service_class(algorithm)
    assert service_class.__name__ == algorithm['service']
    # The module path is derived from the config name, so a mismatch here is
    # a misfiled directory rather than a wrong literal.
    assert f".{algorithm['name']}." in service_class.__module__


@pytest.mark.parametrize('algorithm', ALGORITHMS, ids=lambda a: a['name'])
def test_service_announces_its_own_name(algorithm):
    """The name the service passes to super().__init__ must be its own."""
    service_class = AnalyzeService._resolve_algorithm_service_class(algorithm)
    source = inspect.getsource(service_class)
    marker = f"super().__init__('{algorithm['name']}'"
    assert marker in source, (
        f"{service_class.__name__} does not pass '{algorithm['name']}' as its "
        f"algorithm name; check the first argument to super().__init__"
    )
