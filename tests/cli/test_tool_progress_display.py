from unittest.mock import MagicMock, patch

from cli import HermesCLI


def _make_cli_stub(tool_progress_mode: str = "all"):
    cli = HermesCLI.__new__(HermesCLI)
    cli.tool_progress_mode = tool_progress_mode
    cli._spinner_text = ""
    cli._tool_start_time = 0.0
    cli._voice_mode = False
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
    cli._agent_running = True
    cli._last_invalidate = 0.0
    cli._tool_progress_seen = set()
    cli._invalidate = MagicMock()
    return cli


def test_tool_progress_all_prints_durable_lines_for_each_started_tool():
    cli = _make_cli_stub("all")

    with patch("cli._cprint") as mock_print, patch.object(cli, "_invalidate"):
        cli._on_tool_progress("tool.started", "read_file", "Reading alpha.txt", {"path": "alpha.txt"})
        cli._on_tool_progress("tool.started", "write_file", "Writing beta.txt", {"path": "beta.txt"})

    printed = [call.args[0] for call in mock_print.call_args_list]
    assert len(printed) == 2
    assert "Reading alpha.txt" in printed[0]
    assert "Writing beta.txt" in printed[1]
    assert "beta.txt" in cli._spinner_text


def test_tool_progress_new_deduplicates_repeated_preview_lines():
    cli = _make_cli_stub("new")

    with patch("cli._cprint") as mock_print, patch.object(cli, "_invalidate"):
        cli._on_tool_progress("tool.started", "read_file", "Reading alpha.txt", {"path": "alpha.txt"})
        cli._on_tool_progress("tool.started", "read_file", "Reading alpha.txt", {"path": "alpha.txt"})

    printed = [call.args[0] for call in mock_print.call_args_list]
    assert len(printed) == 1
    assert "Reading alpha.txt" in printed[0]


def test_tool_progress_off_keeps_spinner_only_without_printing_lines():
    cli = _make_cli_stub("off")

    with patch("cli._cprint") as mock_print:
        cli._on_tool_progress("tool.started", "read_file", "Reading alpha.txt", {"path": "alpha.txt"})

    mock_print.assert_not_called()
    assert "alpha.txt" in cli._spinner_text
