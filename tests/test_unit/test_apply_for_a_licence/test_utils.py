import builtins
from builtins import __import__ as builtin_import

from apply_for_a_licence.utils import get_active_regimes


def test_get_active_regimes_normal():
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert all(isinstance(regime, dict) for regime in regimes)
    assert len(regimes) >= 1


def test_get_active_regimes_import_error(monkeypatch):
    def mock_import(*args, **kwargs):
        if len(args[3]) > 0:
            if args[3][0] == "active_regimes":
                raise ImportError
            else:
                return builtin_import(*args, **kwargs)
        else:
            # we need to provide some route to the original import as the teardown of the test will fail otherwise
            return builtin_import(*args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert len(regimes) == 0
    assert regimes == []
