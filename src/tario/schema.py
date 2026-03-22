from __future__ import annotations

from typing import Any

COMMAND_SCHEMAS: dict[str, dict[str, Any]] = {
    "about": {
        "summary": "Describe tario purpose and interaction model.",
        "arguments": [],
        "options": [{"name": "--output", "type": "json|text", "required": False}],
        "examples": ["tario about", "tario --output json about"],
    },
    "commands": {
        "summary": "List command groups.",
        "arguments": [],
        "options": [{"name": "--output", "type": "json|text", "required": False}],
        "examples": ["tario commands", "tario --output json commands"],
    },
    "describe": {
        "summary": "Describe one command contract.",
        "arguments": [{"name": "subject", "type": "string", "required": False}],
        "options": [{"name": "--output", "type": "json|text", "required": False}],
        "examples": ["tario describe", "tario describe test-run"],
    },
    "doctor": {
        "summary": "Validate local config and Docker Compose prerequisites.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False},
            {"name": "--output", "type": "json|text", "required": False},
        ],
        "examples": ["tario doctor", "tario --output json doctor --profile default"],
    },
    "profile-add": {
        "summary": "Create or update a profile and set it active.",
        "arguments": [{"name": "name", "type": "string", "required": True}],
        "options": [
            {"name": "--repo-path", "type": "string", "required": True},
            {"name": "--compose-file", "type": "string[]", "required": True},
            {"name": "--service", "type": "string", "required": False},
            {"name": "--output", "type": "json|text", "required": False},
        ],
        "examples": [
            (
                "tario profile add default --repo-path path-to-repo "
                "--compose-file docker-compose.yml "
                "--compose-file docker-compose.test.yml --service odoo"
            )
        ],
    },
    "profile-list": {
        "summary": "List available profiles.",
        "arguments": [],
        "options": [{"name": "--output", "type": "json|text", "required": False}],
        "examples": ["tario profile list"],
    },
    "profile-show": {
        "summary": "Show one profile or the active profile.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False},
            {"name": "--output", "type": "json|text", "required": False},
        ],
        "examples": ["tario profile show", "tario profile show --profile default"],
    },
    "profile-use": {
        "summary": "Set active profile.",
        "arguments": [{"name": "name", "type": "string", "required": True}],
        "options": [{"name": "--output", "type": "json|text", "required": False}],
        "examples": ["tario profile use default"],
    },
    "test-run": {
        "summary": "Run tests through Docker Compose from the selected profile.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False},
            {"name": "--clean", "type": "flag", "required": False},
            {"name": "--build", "type": "flag", "required": False},
            {"name": "--integration", "type": "flag", "required": False},
            {"name": "--update", "type": "string", "required": False},
            {"name": "--keyword", "type": "string", "required": False},
            {"name": "--pytest-arg", "type": "string[]", "required": False},
            {"name": "--output", "type": "json|text", "required": False},
        ],
        "examples": [
            "tario test run --profile default",
            "tario test run --profile default --integration --keyword foo",
        ],
    },
}


COMMAND_GROUPS = [
    {"name": "introspection", "commands": ["about", "commands", "describe"]},
    {"name": "health", "commands": ["doctor"]},
    {
        "name": "profiles",
        "commands": ["profile add", "profile list", "profile show", "profile use"],
    },
    {"name": "testing", "commands": ["test run"]},
]


def describe_subject(subject: str | None = None) -> dict[str, Any]:
    if not subject:
        return {
            "subject": "commands",
            "summary": "Available command contracts.",
            "commands": sorted(COMMAND_SCHEMAS),
        }

    normalized = subject.strip().lower().replace(" ", "-")
    if normalized not in COMMAND_SCHEMAS:
        available = ", ".join(sorted(COMMAND_SCHEMAS))
        raise KeyError(f"Unknown subject {subject!r}. Available subjects: {available}.")

    return {
        "subject": normalized,
        **COMMAND_SCHEMAS[normalized],
    }
