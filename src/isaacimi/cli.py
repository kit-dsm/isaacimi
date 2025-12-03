import click

@click.group()
@click.version_option(package_name="isaacimi")
def cli_main():
    """Main cli for isaacimi.
    """

@cli_main.group()
def sim():
    """Simulation commands.
    """

@click.command()
@click.argument("blueprint_path", nargs=1, type=click.Path(exists=True, dir_okay=False))
def run(blueprint_path):
    """Run a simulation with an isaacimi blueprint
    """
    from .sim_runner import run_sim
    run_sim(blueprint_path)

@click.command()
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
def test(pytest_args):
    """Run pytest."""
    try:
        import pytest
    except ImportError:
        click.echo("The 'test' command requires additional dependencies. Please install isaacimi with:")
        click.echo(f"    scripts/install.sh --test")
        return
    pytest.main(list(pytest_args))

sim.add_command(run)
cli_main.add_command(test)

if __name__ == '__main__':
    cli_main(prog_name="isaacimi")
