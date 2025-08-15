import click

from .sim_runner import run_sim

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
    run_sim(blueprint_path)

sim.add_command(run)

if __name__ == '__main__':
    cli_main(prog_name="isaacimi")
