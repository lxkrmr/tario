from tario.schema import describe_subject


def test_describe_known_subject() -> None:
    payload = describe_subject("test-run")
    assert payload["subject"] == "test-run"
    assert payload["summary"]


def test_describe_all_commands() -> None:
    payload = describe_subject()
    assert payload["subject"] == "commands"
    assert "test-run" in payload["commands"]
