import importlib
import sys

import pytest

pytestmark = pytest.mark.offline

_original_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
utils_api = importlib.import_module("lightrag.api.utils_api")
sys.argv = _original_argv


class _LegacyEncodedStdout:
    def __init__(self):
        self.calls = []

    def reconfigure(self, **kwargs):
        self.calls.append(kwargs)


def test_console_output_uses_non_strict_encoding_errors(monkeypatch):
    stream = _LegacyEncodedStdout()
    monkeypatch.setattr(utils_api.sys, "stdout", stream)

    utils_api._make_console_output_unicode_safe()

    assert stream.calls == [{"errors": "backslashreplace"}]


def test_console_output_allows_stream_without_reconfigure(monkeypatch):
    monkeypatch.setattr(utils_api.sys, "stdout", object())

    utils_api._make_console_output_unicode_safe()
