from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Profile:
    name: str
    repo_path: str
    compose_files: list[str]
    service: str = "odoo"


@dataclass(slots=True)
class TarioConfig:
    path: Path
    active_profile: str | None
    profiles: dict[str, Profile]

    @classmethod
    def load(cls, path: Path | None = None) -> "TarioConfig":
        target = path or default_config_path()
        if not target.exists():
            raise FileNotFoundError(f"Config file not found at {target}.")

        raw = tomllib.loads(target.read_text(encoding="utf-8"))
        active = raw.get("active_profile")
        profiles_raw = raw.get("profiles", {})
        profiles: dict[str, Profile] = {}

        for name, item in profiles_raw.items():
            compose_files = item.get("compose_files")
            if not isinstance(compose_files, list) or not compose_files:
                raise ValueError(f"Profile {name!r} must define non-empty compose_files.")

            profile = Profile(
                name=name,
                repo_path=str(item.get("repo_path", "")).strip(),
                compose_files=[str(value).strip() for value in compose_files],
                service=str(item.get("service", "odoo")).strip() or "odoo",
            )
            if not profile.repo_path:
                raise ValueError(f"Profile {name!r} must define repo_path.")
            profiles[name] = profile

        return cls(path=target, active_profile=active, profiles=profiles)

    @classmethod
    def create_empty(cls, path: Path | None = None) -> "TarioConfig":
        target = path or default_config_path()
        return cls(path=target, active_profile=None, profiles={})

    def resolve_profile(self, requested: str | None = None) -> Profile:
        if requested:
            if requested not in self.profiles:
                raise KeyError(f"Profile {requested!r} does not exist.")
            return self.profiles[requested]

        if not self.active_profile:
            raise KeyError("No active profile is configured.")

        if self.active_profile not in self.profiles:
            raise KeyError(f"Active profile {self.active_profile!r} does not exist.")

        return self.profiles[self.active_profile]

    def add_profile(self, profile: Profile, *, make_active: bool = True) -> None:
        self.profiles[profile.name] = profile
        if make_active:
            self.active_profile = profile.name

    def use_profile(self, name: str) -> None:
        if name not in self.profiles:
            raise KeyError(f"Profile {name!r} does not exist.")
        self.active_profile = name

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self._to_toml(), encoding="utf-8")

    def _to_toml(self) -> str:
        lines: list[str] = []
        if self.active_profile:
            lines.append(f'active_profile = "{escape(self.active_profile)}"')
        lines.append("")

        for name in sorted(self.profiles):
            profile = self.profiles[name]
            lines.append(f"[profiles.{name}]")
            lines.append(f'repo_path = "{escape(profile.repo_path)}"')
            compose = ", ".join(f'"{escape(item)}"' for item in profile.compose_files)
            lines.append(f"compose_files = [{compose}]")
            lines.append(f'service = "{escape(profile.service)}"')
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def default_config_path() -> Path:
    home = Path.home()
    return home / ".config" / "tario" / "tario.toml"
