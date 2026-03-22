from pathlib import Path

from tario.config import Profile, TarioConfig


def test_config_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "tario.toml"
    cfg = TarioConfig.create_empty(path)
    cfg.add_profile(
        Profile(
            name="default",
            repo_path="path-to-repo",
            compose_files=["docker-compose.yml", "docker-compose.test.yml"],
            service="odoo",
        )
    )
    cfg.save()

    loaded = TarioConfig.load(path)
    selected = loaded.resolve_profile()

    assert loaded.active_profile == "default"
    assert selected.repo_path == "path-to-repo"
    assert selected.compose_files == ["docker-compose.yml", "docker-compose.test.yml"]
