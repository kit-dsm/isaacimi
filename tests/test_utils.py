from isaacimi.utils import load_subclasses_from_file
from isaacimi.utils import resolve_path_in_blueprint
from pathlib import Path
import pytest

from isaacimi.robot_plugin import ImiRobotPlugin

@pytest.fixture(scope="class")
def module_filepath(tmp_path_factory):
    filepath = tmp_path_factory.mktemp("data") / "dummy_classes.py"
    filepath.write_text("""
from isaacimi.robot_plugin import ImiRobotPlugin

class ChildClass1(ImiRobotPlugin):
    def on_plugin_load(self):
        print("Hello world from ChildClass1!")

class ChildClass2(ImiRobotPlugin):
    def on_plugin_load(self):
        print("Hello world from ChildClass2!")

class ChildClass3(ImiRobotPlugin):
    def on_plugin_load(self):
        print("Hello world from ChildClass3!")
 
class ChildClass4(ImiRobotPlugin):
    def on_plugin_load(self):
        print("Hello world from ChildClass4!")

class OtherClass:
    def __init__(self):
        print("Hello world from OtherClass!")
""")
    return filepath

class TestLoadSubclassesFromFile:
    def test_all_classes_load_by_default(self, module_filepath):
        plugins = load_subclasses_from_file(str(module_filepath), ImiRobotPlugin)
        assert len(plugins) == 4

    def test_allowed_classes_load(self, module_filepath):
        allowed_classes = ["ChildClass1", "ChildClass3"]
        plugins = load_subclasses_from_file(str(module_filepath), ImiRobotPlugin, allowed_classes)
        assert len(plugins) == 2
        assert set(plugins.keys()) == set(allowed_classes)
    
    def test_missing_classes_raises_value_error(self, module_filepath):
        allowed_classes = ["ChildClass1", "ChildClass3", "RandomClass"]
        with pytest.raises(ValueError):
            load_subclasses_from_file(str(module_filepath), ImiRobotPlugin, allowed_classes)

    def test_invalid_file_raises_value_error(self):
        with pytest.raises(ValueError):
            load_subclasses_from_file("invalid/relative/path", ImiRobotPlugin)



@pytest.fixture(scope="class")
def shared_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data1")

@pytest.fixture(scope="class")
def blueprint_filepath(shared_dir):
    file = shared_dir / "blueprints" / "my_blueprint.yaml"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("Hello World!")
    return file

@pytest.fixture(scope="class")
def resolved_usd_filepath(shared_dir):
    file = shared_dir / "robots" / "custom_robot" / "my_custom_robot.usd"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("Hello World!")
    return file

class TestResolveBlueprintPath:
    @pytest.mark.parametrize("server_url", [
        "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Robots/Turtlebot/turtlebot3_burger.usd",
        "http://randomurl.com",
        "omniverse://localhost/Documents/random.usd"
    ])
    def test_server_urls_return_unchanged(self, server_url, blueprint_filepath):
        assert resolve_path_in_blueprint(server_url, str(blueprint_filepath)) == server_url

    @pytest.mark.parametrize("rel_path", [
        "../robots/custom_robot/my_custom_robot.usd",
        "./../robots/custom_robot/my_custom_robot.usd",
        "./../robots/custom_robot/../custom_robot/my_custom_robot.usd"
    ])
    def test_relative_paths_are_resolved(self, rel_path, resolved_usd_filepath, blueprint_filepath):
        assert resolve_path_in_blueprint(rel_path, str(blueprint_filepath)) == str(resolved_usd_filepath)

    @pytest.mark.parametrize("abs_path", [
        "",
        "../../././../blueprints/../robots/custom_robot/my_custom_robot.usd"
    ])
    def test_abs_paths_are_resolved(self, abs_path, resolved_usd_filepath, blueprint_filepath):
        assert resolve_path_in_blueprint(str(resolved_usd_filepath / abs_path), str(blueprint_filepath)) == str(resolved_usd_filepath)

    def test_non_existent_file_raises_file_not_found(self, blueprint_filepath):
        with pytest.raises(FileNotFoundError):
            resolve_path_in_blueprint("../robots/custom_robot/not_existent_robot.usd", str(blueprint_filepath))

    def test_directory_raises_is_a_directory_error(self, blueprint_filepath):
        with pytest.raises(IsADirectoryError):
            resolve_path_in_blueprint(str(Path(__file__).parent / "data" ), str(blueprint_filepath))

    def test_invalid_extension_raises_value_error(self, blueprint_filepath):
        with pytest.raises(ValueError):
            resolve_path_in_blueprint(str(Path(__file__)), str(blueprint_filepath), allowed_extensions={".usd"})





