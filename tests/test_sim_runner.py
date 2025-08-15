from isaacimi.sim_runner import run_sim
import pytest

@pytest.fixture
def json_file(tmp_path):
    file = tmp_path / "blueprint.json"
    file.write_text("{'key':'value'}")
    return file

def test_non_existent_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        run_sim("random/path/to/file.yaml")

def test_non_yaml_file_raises_value_error(json_file):
    with pytest.raises(ValueError):
        run_sim(str(json_file))