"""Tests for the repo validator."""
import os
import tempfile

from core.audit import validate as V


def test_secret_scan_flags_planted_key():
    # build the secret at runtime so this source file stays clean for the full-repo scan
    planted = "sk-" + "ant-" + "a" * 36
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "leak.py"), "w", encoding="utf-8") as fh:
            fh.write(f'KEY = "{planted}"\n')
        problems = V.scan_secrets(d)
        assert any("possible secret" in p for p in problems)


def test_secret_scan_clean_dir():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "ok.py"), "w", encoding="utf-8") as fh:
            fh.write("x = 1  # nothing secret here\n")
        assert V.scan_secrets(d) == []


def test_contracts_pass_on_initialized_repo():
    # the real repo's contracts are initialized (non-null paper_id, central_claim)
    problems = V.check_contracts(V._REPO_ROOT)
    assert problems == [], problems


def test_full_validation_repo_ok():
    ok, problems = V.run_validation()
    assert ok, problems
