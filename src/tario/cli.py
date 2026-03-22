from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Any

import typer

from .config import (
    Profile,
    TarioConfig,
    default_artifacts_dir,
    default_config_path,
)
from .output import OutputFormat, OutputManager, error, success
from .runner import RunRequest, ensure_docker_available, run_tests, validate_profile_files
from .schema import COMMAND_GROUPS, describe_subject

PROFILE_ADD_EXAMPLE = (
    "tario profile add default "
    "--repo-path path-to-repo "
    "--compose-file docker-compose.yml "
    "--compose-file docker-compose.test.yml "
    "--service odoo"
)
GLOBAL_OUTPUT_GUIDE = "Use global output option: tario --output json <command>"

app = typer.Typer(
    help=(
        "Agent-friendly Docker Compose test runner for Odoo addon projects. "
        "Start with 'tario doctor'."
    ),
    no_args_is_help=True,
)
profile_app = typer.Typer(help="Manage tario profiles.", no_args_is_help=True)
test_app = typer.Typer(help="Run tests through Docker Compose.", no_args_is_help=True)
app.add_typer(profile_app, name="profile")
app.add_typer(test_app, name="test")


class AppState:
    def __init__(self, output: OutputFormat) -> None:
        self.output = OutputManager(output)


def emit(ctx: typer.Context, payload: dict[str, Any]) -> None:
    state: AppState = ctx.obj
    state.output.emit(payload)


def fail(
    ctx: typer.Context,
    *,
    code: str,
    message: str,
    data: dict[str, Any] | None = None,
    next_commands: list[str] | None = None,
    exit_code: int = 1,
) -> None:
    emit(ctx, error(code=code, message=message, data=data, next_commands=next_commands))
    raise typer.Exit(code=exit_code)


def load_config_or_fail(ctx: typer.Context) -> TarioConfig:
    try:
        return TarioConfig.load()
    except FileNotFoundError:
        fail(
            ctx,
            code="CONFIG_NOT_FOUND",
            message=f"Config file not found at {default_config_path()}.",
            next_commands=[GLOBAL_OUTPUT_GUIDE, PROFILE_ADD_EXAMPLE],
            exit_code=2,
        )
    except Exception as exc:  # pragma: no cover - defensive branch
        fail(ctx, code="CONFIG_INVALID", message=str(exc), exit_code=2)


def resolve_profile_or_fail(ctx: typer.Context, profile: str | None) -> Profile:
    config = load_config_or_fail(ctx)
    try:
        selected = config.resolve_profile(profile)
    except KeyError as exc:
        fail(
            ctx,
            code="PROFILE_NOT_FOUND",
            message=str(exc),
            data={
                "requested_profile": profile,
                "active_profile": config.active_profile,
            },
            next_commands=[
                GLOBAL_OUTPUT_GUIDE,
                "tario profile list",
                PROFILE_ADD_EXAMPLE,
            ],
            exit_code=3,
        )
    return selected


def write_run_summary(
    artifacts_dir: Path,
    profile: Profile,
    result_data: dict[str, Any],
    *,
    code: str,
    ok: bool,
) -> str:
    summary = {
        "ok": ok,
        "code": code,
        "profile": asdict(profile),
        "result": result_data,
    }
    summary_path = artifacts_dir / "last-run-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return str(summary_path)


OutputOption = Annotated[
    OutputFormat,
    typer.Option("--output", help="Output format.", case_sensitive=False),
]


@app.callback()
def main_options(ctx: typer.Context, output: OutputOption = "json") -> None:
    ctx.obj = AppState(output)


@app.command("about")
def about(ctx: typer.Context) -> None:
    emit(
        ctx,
        success(
            message="tario helps run Compose-based test workflows with deterministic output.",
            data={
                "name": "tario",
                "purpose": [
                    "Run tests through Docker Compose profiles",
                    "Provide stable JSON output for automation",
                    "Keep configuration as the single source of truth",
                ],
                "interaction": {
                    "start_with": "tario doctor",
                    "discover_commands_with": "tario commands",
                    "inspect_contracts_with": "tario describe test-run",
                    "global_output_option": "tario --output json <command>",
                },
            },
            next_commands=[
                "tario commands",
                "tario --output json commands",
                "tario doctor",
            ],
        ),
    )


@app.command("commands")
def commands(ctx: typer.Context) -> None:
    emit(
        ctx,
        success(
            message="Available tario command groups.",
            data={"groups": COMMAND_GROUPS},
            next_commands=[
                "tario describe test-run",
                "tario --output json describe test-run",
                "tario doctor",
            ],
        ),
    )


@app.command("describe")
def describe(
    ctx: typer.Context,
    subject: Annotated[str | None, typer.Argument(help="Command key to describe.")] = None,
) -> None:
    try:
        description = describe_subject(subject)
    except KeyError as exc:
        fail(ctx, code="UNKNOWN_SUBJECT", message=str(exc), exit_code=4)
    emit(ctx, success(message="Command schema.", data=description))


@app.command("doctor")
def doctor(
    ctx: typer.Context,
    profile: Annotated[str | None, typer.Option("--profile", help="Profile override.")] = None,
) -> None:
    selected = resolve_profile_or_fail(ctx, profile)

    try:
        ensure_docker_available()
        validate_profile_files(selected)
    except RuntimeError as exc:
        fail(
            ctx,
            code="DOCTOR_FAILED",
            message=str(exc),
            data={"profile": selected.name, **asdict(selected)},
            exit_code=5,
        )

    emit(
        ctx,
        success(
            message=f"Profile {selected.name!r} is ready.",
            data={
                "profile": asdict(selected),
                "config_path": str(default_config_path()),
                "artifacts_dir": str(default_artifacts_dir() / selected.name),
            },
            next_commands=[f"tario test run --profile {selected.name}"],
        ),
    )


@profile_app.command("add")
def profile_add(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Profile name.")],
    repo_path: Annotated[
        str,
        typer.Option("--repo-path", help="Repository path containing compose files."),
    ],
    compose_files: Annotated[
        list[str],
        typer.Option("--compose-file", help="Compose file relative to repo path."),
    ],
    service: Annotated[
        str,
        typer.Option("--service", help="Compose service for test container."),
    ] = "odoo",
) -> None:
    if not compose_files:
        fail(
            ctx,
            code="INVALID_INPUT",
            message="Provide at least one --compose-file.",
            exit_code=5,
        )

    try:
        config = TarioConfig.load()
    except FileNotFoundError:
        config = TarioConfig.create_empty()
    except Exception as exc:  # pragma: no cover - defensive branch
        fail(ctx, code="CONFIG_INVALID", message=str(exc), exit_code=2)

    profile = Profile(
        name=name,
        repo_path=repo_path,
        compose_files=compose_files,
        service=service,
    )
    config.add_profile(profile, make_active=True)
    config.save()

    emit(
        ctx,
        success(
            code="PROFILE_SAVED",
            message=f"Profile {name!r} saved and activated.",
            data={
                "profile": asdict(profile),
                "active_profile": config.active_profile,
                "config_path": str(config.path),
            },
            next_commands=["tario doctor", f"tario test run --profile {name}"],
        ),
    )


@profile_app.command("list")
def profile_list(ctx: typer.Context) -> None:
    config = load_config_or_fail(ctx)
    profiles = [asdict(profile) for _, profile in sorted(config.profiles.items())]
    emit(
        ctx,
        success(
            message="Profiles listed.",
            data={
                "profiles": profiles,
                "active_profile": config.active_profile,
                "config_path": str(config.path),
            },
        ),
    )


@profile_app.command("show")
def profile_show(
    ctx: typer.Context,
    profile: Annotated[str | None, typer.Option("--profile", help="Profile override.")] = None,
) -> None:
    selected = resolve_profile_or_fail(ctx, profile)
    config = load_config_or_fail(ctx)
    emit(
        ctx,
        success(
            message=f"Profile {selected.name!r}.",
            data={
                "profile": asdict(selected),
                "active_profile": config.active_profile,
                "config_path": str(config.path),
            },
        ),
    )


@profile_app.command("use")
def profile_use(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Profile name to activate.")],
) -> None:
    config = load_config_or_fail(ctx)
    try:
        config.use_profile(name)
    except KeyError as exc:
        fail(ctx, code="PROFILE_NOT_FOUND", message=str(exc), exit_code=3)
    config.save()
    emit(
        ctx,
        success(
            code="PROFILE_ACTIVE",
            message=f"Profile {name!r} is now active.",
            data={
                "active_profile": config.active_profile,
                "config_path": str(config.path),
            },
            next_commands=["tario doctor", f"tario test run --profile {name}"],
        ),
    )


@test_app.command("run")
def test_run(
    ctx: typer.Context,
    profile: Annotated[str | None, typer.Option("--profile", help="Profile override.")] = None,
    clean: Annotated[
        bool,
        typer.Option("--clean", help="Remove Compose services and volumes first."),
    ] = False,
    build: Annotated[
        bool,
        typer.Option("--build", help="Build images before run."),
    ] = False,
    integration: Annotated[
        bool,
        typer.Option("--integration", help="Run integration test marker flow."),
    ] = False,
    update: Annotated[
        str | None,
        typer.Option("--update", help="Comma-separated addon names for update."),
    ] = None,
    keyword: Annotated[
        str | None,
        typer.Option("--keyword", "-k", help="Pytest keyword expression."),
    ] = None,
    pytest_args: Annotated[
        list[str],
        typer.Option("--pytest-arg", help="Extra pytest argument (repeatable)."),
    ] = [],
) -> None:
    selected = resolve_profile_or_fail(ctx, profile)
    request = RunRequest(
        clean=clean,
        build=build,
        integration=integration,
        update=update,
        keyword=keyword,
        pytest_args=pytest_args,
    )

    artifacts_dir = default_artifacts_dir() / selected.name

    try:
        result = run_tests(selected, request)
    except RuntimeError as exc:
        fail(
            ctx,
            code="COMPOSE_FAILED",
            message=str(exc),
            data={"profile": asdict(selected)},
            exit_code=6,
        )

    result_data = {
        "profile": asdict(selected),
        "exit_code": result.exit_code,
        "commands": result.commands,
        "artifacts_dir": str(artifacts_dir),
    }
    if not result.ok:
        summary_path = write_run_summary(
            artifacts_dir,
            selected,
            result_data,
            code="TESTS_FAILED",
            ok=False,
        )
        result_data["summary_json_path"] = summary_path
        fail(
            ctx,
            code="TESTS_FAILED",
            message="Test run finished with failures.",
            data=result_data,
            next_commands=[
                "tario --output text test run --profile " + selected.name,
            ],
            exit_code=1,
        )

    summary_path = write_run_summary(
        artifacts_dir,
        selected,
        result_data,
        code="TESTS_PASSED",
        ok=True,
    )
    result_data["summary_json_path"] = summary_path
    emit(
        ctx,
        success(
            code="TESTS_PASSED",
            message="Test run completed successfully.",
            data=result_data,
        ),
    )


def main() -> None:
    app()
