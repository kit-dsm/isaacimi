import pytest


@pytest.fixture(scope="session")
def simulation_app():
    from isaacsim import SimulationApp
    simulation_app = SimulationApp({"headless": True})
    yield simulation_app
    simulation_app.close()

@pytest.fixture()
def world(simulation_app):
    from isaacsim.core.api import World
    yield World(stage_units_in_meters=1.0)
    World.clear_instance()