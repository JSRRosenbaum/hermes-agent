from unittest.mock import MagicMock, patch

from cli import HermesCLI


class _FakeOutput:
    def __init__(self):
        self.titles = []

    def set_title(self, title):
        self.titles.append(title)


def _make_cli_stub():
    cli = HermesCLI.__new__(HermesCLI)
    cli._app = None
    cli._session_db = None
    cli.session_id = None
    cli._pending_title = None
    cli._secret_state = None
    cli._sudo_state = None
    cli._approval_state = None
    cli._clarify_state = None
    cli._clarify_freetext = False
    cli._voice_processing = False
    cli._command_running = False
    cli._agent_running = False
    cli._spinner_text = ""
    return cli


def test_runtime_title_helpers_initialize_missing_state_for_new_stubs():
    cli = _make_cli_stub()

    title = cli._compose_runtime_title()

    assert title == "★ Idle - hermes"
    assert cli._title_topic == "Idle"
    assert cli._title_status == "waiting"


def test_emit_terminal_title_uses_safe_subprocess_for_tmux_rename():
    cli = _make_cli_stub()
    output = _FakeOutput()
    cli._app = type("App", (), {"output": output})()
    cli._title_topic = '$(touch nope)'

    with patch("cli.os.environ", {"TMUX": "/tmp/tmux.sock"}), patch("cli.subprocess.run") as run_mock:
        cli._emit_terminal_title()

    assert output.titles == ["★ $(touch nope) - hermes"]
    run_mock.assert_called_once()
    args, kwargs = run_mock.call_args
    assert args[0] == ["tmux", "rename-window", "★ $(touch nope) - hermes"]
    assert kwargs["check"] is False
