import pytest

from isaacimi.blueprint_schema import blueprint_schema, BlueprintValidator
from pathlib import Path
import yaml

@pytest.fixture
def load_blueprint():
    def load(blueprint_name):
        blueprint_path = Path(__file__).parent / "data" / blueprint_name
        with open(blueprint_path, 'r') as scene_config_file:
            return yaml.safe_load(scene_config_file)
    return load

@pytest.fixture
def validator():
    return BlueprintValidator(blueprint_schema)

def test_valid_blueprint_passes(load_blueprint, validator):
    valid_blueprint = load_blueprint("valid_blueprint.yaml")
    assert validator.validate(valid_blueprint) is True

def test_unknown_field_fails(load_blueprint, validator):
    blueprint = load_blueprint("valid_blueprint.yaml")

    def resursively_add_unknown_field(config):
        count = 0
        if isinstance(config, dict):
            config["this is an unknown field"] = 5
            count += 1
            for value in config.values():
                count += resursively_add_unknown_field(value)
        elif isinstance(config, list):
            for list_item in config:
                count += resursively_add_unknown_field(list_item)
        return count
    
    num_fields_added = resursively_add_unknown_field(blueprint)
    assert validator.validate(blueprint) is False

def test_duplicate_robot_names_fails(load_blueprint, validator):
    blueprint = load_blueprint("valid_blueprint.yaml")
    blueprint["scene"]["robots"].append(blueprint["scene"]["robots"][0])
    assert validator.validate(blueprint) is False
    assert "scene" in validator.errors
    assert "robots" in validator.errors["scene"][0]

def test_duplicate_plugin_names_fails(load_blueprint, validator):
    blueprint = load_blueprint("valid_blueprint.yaml")
    blueprint["robot_plugins"][0]["classes"].append(blueprint["robot_plugins"][0]["classes"][0])
    assert validator.validate(blueprint) is False
    assert "robot_plugins" in validator.errors