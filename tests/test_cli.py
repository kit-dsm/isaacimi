from click.testing import CliRunner
from isaacimi.cli import cli_main
from unittest.mock import patch

def test_sim_run_calls_sim_runner(tmp_path):
    blueprint = tmp_path / "blueprint.yaml"
    blueprint.write_text("key: value")
    runner = CliRunner()
    with patch("isaacimi.cli.run_sim") as mock_run_sim:
        result = runner.invoke(cli_main, ["sim", "run", str(blueprint)])
    assert result.exit_code == 0