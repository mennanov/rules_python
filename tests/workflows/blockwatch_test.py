"""Tests for .github/workflows/ci.yaml blockwatch configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from python.runfiles import runfiles


def _repo_file(rel_path: str) -> Path:
    """Returns the runfile Path for `rel_path` relative to the workspace root."""
    return runfiles.CreateOrRaise().root() / f"rules_python/{rel_path}"


def _assert_ci_download_step_in_sync(
    *,
    repo_url: str,
    expected_hooks: list[str],
    job_id: str,
    step_id: str,
    url_template: str,
    archive_member: str = "",
) -> list[dict[str, Any]]:
    pre_commit = yaml.safe_load(
        _repo_file(".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    matching = [repo for repo in pre_commit["repos"] if repo.get("repo") == repo_url]
    assert len(matching) == 1
    rev = matching[0]["rev"]
    assert [hook["id"] for hook in matching[0]["hooks"]] == expected_hooks

    ci = yaml.safe_load(
        _repo_file(".github/workflows/ci.yaml").read_text(encoding="utf-8")
    )
    job = ci["jobs"][job_id]
    assert job["runs-on"] == "ubuntu-latest"
    steps = job["steps"]

    download_step = next(s for s in steps if s.get("id") == step_id)
    assert download_step["uses"] == "./.github/actions/download-tool"
    assert download_step["with"]["name"] == step_id
    assert download_step["with"].get("archive-member", "") == archive_member
    urls = [
        line.strip()
        for line in download_step["with"]["urls"].splitlines()
        if line.strip()
    ]
    assert urls == [url_template.format(rev=rev)]
    assert (
        download_step["with"]["sha256"]
        == "e789d0b0fef20fead0ad05cb39e924fd7d9950205d880a2940329950bf1b4a57"
    )
    return steps


def test_ci_workflow_blockwatch_in_sync_with_pre_commit() -> None:
    steps = _assert_ci_download_step_in_sync(
        repo_url="https://github.com/mennanov/blockwatch",
        expected_hooks=["blockwatch"],
        job_id="blockwatch",
        step_id="blockwatch",
        url_template="https://github.com/mennanov/blockwatch/releases/download/{rev}/blockwatch-x86_64-unknown-linux-gnu.tar.xz",
        archive_member="blockwatch-x86_64-unknown-linux-gnu/blockwatch",
    )

    checkout_step = steps[0]
    assert checkout_step["uses"].startswith("actions/checkout@")
    assert checkout_step["with"]["fetch-depth"] == 0

    check_step = next(s for s in steps if s.get("name") == "Check blockwatch")
    assert check_step["if"] == "github.event_name != 'pull_request'"
    assert check_step["env"] == {
        "BLOCKWATCH_BIN": "${{ steps.blockwatch.outputs.path }}"
    }
    assert check_step["run"] == '"$BLOCKWATCH_BIN"'

    diff_step = next(s for s in steps if s.get("name") == "Check blockwatch diff")
    assert diff_step["if"] == "github.event_name == 'pull_request'"
    assert diff_step["env"] == {
        "BASE_SHA": "${{ github.event.pull_request.base.sha }}",
        "HEAD_SHA": "${{ github.event.pull_request.head.sha }}",
        "BLOCKWATCH_BIN": "${{ steps.blockwatch.outputs.path }}",
    }
    assert (
        diff_step["run"]
        == 'git diff --patch "${BASE_SHA}...${HEAD_SHA}" | "$BLOCKWATCH_BIN" --diff'
    )
