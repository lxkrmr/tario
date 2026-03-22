from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .config import Profile


@dataclass(slots=True)
class RunRequest:
    clean: bool
    build: bool
    integration: bool
    update: str | None
    keyword: str | None
    pytest_args: list[str]


@dataclass(slots=True)
class RunResult:
    ok: bool
    exit_code: int
    commands: list[list[str]]
    junitxml_path: str


def ensure_docker_available() -> None:
    if shutil.which("docker") is None:
        raise RuntimeError("Docker CLI not found in PATH.")


def validate_profile_files(profile: Profile) -> None:
    repo = Path(profile.repo_path)
    if not repo.exists() or not repo.is_dir():
        raise RuntimeError(f"Profile repo_path does not exist: {profile.repo_path}")

    for compose_file in profile.compose_files:
        candidate = repo / compose_file
        if not candidate.exists():
            raise RuntimeError(f"Compose file does not exist: {compose_file}")


def compose_base_args(profile: Profile) -> list[str]:
    args = ["docker", "compose", "--project-directory", profile.repo_path]
    for compose_file in profile.compose_files:
        args.extend(["-f", compose_file])
    return args


def run_checked(command: Sequence[str], *, cwd: str) -> None:
    process = subprocess.run(command, cwd=cwd, check=False)
    if process.returncode != 0:
        joined = " ".join(command)
        raise RuntimeError(f"Command failed with exit code {process.returncode}: {joined}")


def run_tests(profile: Profile, request: RunRequest) -> RunResult:
    validate_profile_files(profile)
    base = compose_base_args(profile)
    commands: list[list[str]] = []

    if request.clean:
        down_cmd = [*base, "down", "--volumes"]
        commands.append(down_cmd)
        run_checked(down_cmd, cwd=profile.repo_path)

    up_cmd = [*base, "up"]
    if request.build:
        up_cmd.append("--build")
    up_cmd.extend(["--detach", "--scale", f"{profile.service}=0"])
    commands.append(up_cmd)
    run_checked(up_cmd, cwd=profile.repo_path)

    pytest_parts = []
    if request.keyword:
        pytest_parts.extend(["-k", request.keyword])
    pytest_parts.extend(request.pytest_args)

    run_cmd = [
        *base,
        "run",
        "--rm",
        "--env",
        f"PYTEST_ARGS={' '.join(pytest_parts)}",
        "--env",
        f"ODOO_UPDATE_ARG={request.update or ''}",
        "--env",
        f"INTEGRATION_TEST={'true' if request.integration else 'false'}",
    ]
    if request.build:
        run_cmd.append("--build")
    run_cmd.append(profile.service)

    commands.append(run_cmd)
    run_process = subprocess.run(run_cmd, cwd=profile.repo_path, check=False)

    junitxml_path = str(Path(profile.repo_path) / "test-report.xml")
    return RunResult(
        ok=run_process.returncode == 0,
        exit_code=run_process.returncode,
        commands=commands,
        junitxml_path=junitxml_path,
    )
