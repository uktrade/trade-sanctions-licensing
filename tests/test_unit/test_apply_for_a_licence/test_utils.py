import builtins
from builtins import __import__ as builtin_import

from apply_for_a_licence.utils import craft_apply_for_a_licence_url, get_active_regimes
from django.test import override_settings


@override_settings(PROTOCOL="https://", APPLY_FOR_A_LICENCE_DOMAIN="apply-for-a-licence.com")
def test_craft_apply_for_a_licence_url():
    url = craft_apply_for_a_licence_url("/apply/123/")
    assert url == "https://apply-for-a-licence.com/apply/123/"


def test_get_active_regimes_normal():
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert all(isinstance(regime, dict) for regime in regimes)
    assert len(regimes) >= 1


def test_get_active_regimes_import_error(monkeypatch):
    def mock_import(*args, **kwargs):
        if args[3][0] == "active_regimes":
            raise ImportError
        else:
            # we need to provide some route to the original import as the teardown of the test will fail otherwise
            return builtin_import(*args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert len(regimes) == 0
    assert regimes == []
