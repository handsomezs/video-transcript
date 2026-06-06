# tests/test_cli.py
from click.testing import CliRunner
from transcript.cli import main


def test_cli_get_help():
    runner = CliRunner()
    result = runner.invoke(main, ["get", "--help"])
    assert result.exit_code == 0
    assert "--lang" in result.output
    assert "--format" in result.output


def test_cli_list_help():
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--help"])
    assert result.exit_code == 0


def test_cli_main_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "get" in result.output
    assert "list" in result.output
