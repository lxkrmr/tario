from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Literal

import typer

OutputFormat = Literal["json", "text"]
CONTRACT_VERSION = "2026-03-22"


@dataclass(slots=True)
class OutputManager:
    fmt: OutputFormat = "json"

    def emit(self, payload: dict[str, Any]) -> None:
        if self.fmt == "text":
            typer.echo(text_view(payload))
            return
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def tool_version() -> str:
    try:
        return version("tario")
    except PackageNotFoundError:
        return "dev"


def meta() -> dict[str, str]:
    return {
        "tool": "tario",
        "version": tool_version(),
        "contract_version": CONTRACT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def success(
    *,
    code: str = "OK",
    message: str = "OK",
    data: dict[str, Any] | None = None,
    next_commands: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "code": code,
        "message": message,
        "data": data or {},
        "next_commands": next_commands or [],
        "meta": meta(),
    }


def error(
    *,
    code: str,
    message: str,
    data: dict[str, Any] | None = None,
    next_commands: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "code": code,
        "message": message,
        "data": data or {},
        "next_commands": next_commands or [],
        "meta": meta(),
    }


def text_view(payload: dict[str, Any]) -> str:
    status = "OK" if payload.get("ok") else "ERROR"
    code = payload.get("code", "UNKNOWN")
    message = payload.get("message", "")
    lines = [f"{status} [{code}] {message}"]

    next_commands = payload.get("next_commands") or []
    if next_commands:
        lines.append("Next:")
        lines.extend(f"- {item}" for item in next_commands)

    data = payload.get("data")
    if isinstance(data, dict) and data:
        lines.append("Data:")
        lines.append(json.dumps(data, indent=2, sort_keys=True))

    return "\n".join(lines)
