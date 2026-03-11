import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cosmo_nasa_bot


def test_cli_help_mentions_safety_flags(capsys):
    with pytest.raises(SystemExit) as exc:
        cosmo_nasa_bot.main(["--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--api-key" in output
    assert "--dry-run" in output
    assert "--enable-social" in output


def test_main_requires_api_key_without_dry_run(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv("BOTTUBE_API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc:
        cosmo_nasa_bot.main(["--apod", "--work-dir", str(tmp_path)])

    assert exc.value.code == 2
    assert "BoTTube API key required" in capsys.readouterr().err


def test_upload_dry_run_skips_network(monkeypatch, tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"fake-video")
    monkeypatch.setattr(cosmo_nasa_bot, "DRY_RUN", True)

    def fail_requests_post(*args, **kwargs):
        raise AssertionError("requests.post should not run in dry-run mode")

    monkeypatch.setattr(cosmo_nasa_bot.requests, "post", fail_requests_post)

    result = cosmo_nasa_bot.upload_to_bottube(
        video_path,
        "Dry Run Clip",
        "Preview only",
        ["nasa", "demo"],
    )

    assert result["dry_run"] is True
    assert result["title"] == "Dry Run Clip"


def test_browse_and_upvote_is_opt_in(monkeypatch):
    monkeypatch.setattr(cosmo_nasa_bot, "DRY_RUN", False)
    monkeypatch.setattr(cosmo_nasa_bot, "ENABLE_SOCIAL", False)

    def fail_requests_get(*args, **kwargs):
        raise AssertionError("requests.get should not run when social actions are disabled")

    monkeypatch.setattr(cosmo_nasa_bot.requests, "get", fail_requests_get)

    cosmo_nasa_bot.browse_and_upvote()
