from importlib import import_module
import importlib.util
import os
from pathlib import Path
from pkg_resources import require, resource_filename
import shutil
import subprocess
import sys

import click

from automaps.confutils import check_config_options


def _process_config_file(config_file):
    config_path = str(Path(config_file).absolute().parent)
    if config_path not in sys.path:
        sys.path.insert(0, config_path)


@click.group()
def cli():
    """This is the main entry point for all autoMaps commands.
    Take a look at the subcommands and run them with option --help to get more
    information on their usage."""
    pass


@cli.group()
def run():
    """Runs an existing autoMaps project. There are different modes to run
    a project. Take a look at the subcommands to get more information."""
    pass


@run.command(name="registry")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the config file, including the filename. The file needs to be called "
    "'automapsconf.py'.",
)
def run_registry(config_file):
    """Starts the autoMaps registry process, as defined in the config file.

    Example usage:

        automaps run registry -c ./myproject/automapsconf.py"""
    _process_config_file(config_file)
    # check_config_options()
    from automaps.messaging.registry import Registry

    registry = Registry()
    registry.listen()


@run.command(name="worker")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the config file, including the filename. The file needs to be called "
    "'automapsconf.py'.",
)
@click.option("-p", "--port", type=int, help="The port number.")
@click.option(
    "-w",
    "--worker_number_in_config",
    type=int,
    help="The worker number, "
    "starting from 1. The ports defined in the config option PORTS_WORKERS "
    "will be used.",
)
def run_worker(config_file, port, worker_number_in_config):
    """Starts a single autoMaps worker process.

    The port of the worker can either be set
    directly using the --port option, or by referencing the worker number as defined
    in the config file using the --worker_number_in_config option.

    Example usage:

        automaps run worker -c ./myproject/automaps.conf -p 12345

        automaps run worker -c ./myproject/automaps.conf -w 1"""
    _process_config_file(config_file)
    from automaps.messaging.worker import QgisWorker
    import automapsconf

    if (port is None) and (worker_number_in_config is None):
        raise ValueError(
            "Either option -p / --port or -w / --worker_number_in_config needs to be "
            "set"
        )
    elif (port is not None) and (worker_number_in_config is not None):
        raise ValueError(
            "Either option -p / --port or -w / --worker_number_in_config may be set, "
            "not both."
        )
    elif port is not None:
        QgisWorker(port)
    elif worker_number_in_config is not None:
        if worker_number_in_config == 0:
            raise ValueError("Worker numbers start from 1, you entered 0.")
        elif (worker_number_in_config) > len(automapsconf.PORTS_WORKERS):
            raise ValueError(
                f"Trying to read worker port index {worker_number_in_config} from "
                f"config, but only {len(automapsconf.PORTS_WORKERS)} ports are "
                f"configured in PORTS_WORKERS ({automapsconf.PORTS_WORKERS})."
            )
        QgisWorker(automapsconf.PORTS_WORKERS[worker_number_in_config - 1])


@run.command(name="frontend")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the config file, including the filename. The file needs to be called "
    "'automapsconf.py'.",
)
def run_frontend(config_file):
    """Starts the autoMaps frontend process.

    Example usage:

        automaps run frontend -c ./myproject/automaps.conf"""
    _process_config_file(config_file)
    config_path = str(Path(config_file).absolute().parent)
    automaps_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    automaps_run_path = os.path.join(automaps_path, "automaps")
    frontend = subprocess.Popen(
        [
            "streamlit",
            "run",
            os.path.join(automaps_run_path, "start_frontend.py"),
            "--",
            config_path,
            automaps_path,
        ]
    )
    try:
        _, _ = frontend.communicate()
    except KeyboardInterrupt:
        pass
    finally:
        frontend.kill()


@run.command(name="dev")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the config file, including the filename. The file needs to be called "
    "'automapsconf.py'.",
)
def run_dev(config_file):
    """Runs all autoMaps components - frontend, registry, worker(s) - as defined in the
    config file.

    Example usage:

        automaps run dev -c ./myproject/automaps.conf"""
    _process_config_file(config_file)
    from automaps.app import AutoMaps

    app = AutoMaps()


@cli.command(name="init-project")
@click.argument("project-name")
def init_project(project_name):
    """Initializes a new autoMaps project.

    The project will be created in a subirectory (called PROJECT_NAME) of the current
    working directory.

    Example usage:

        automaps init-project my_new_project"""
    try:
        os.mkdir(project_name)
    except FileExistsError:
        project_path = os.path.join(os.getcwd(), project_name)
        print(
            f"Directory '{project_path}' already exists. Please choose a different "
            "project name or delete the existing directory."
        )
        sys.exit()
    resource_filenames = [
        "automapsconf.py",
        "automapsconf_poly.py",
        "db.py",
        "generate_poly.py",
        "init_project.qgz",
        "test_data.gpkg",
    ]
    for filename in resource_filenames:
        source_path = resource_filename("automaps", "data/" + filename)
        shutil.copy(source_path, project_name)


@cli.command(name="init-demo")
def init_demo_project():
    """Initializes a new autoMaps demo project.
    The project will be created in a subdirectory 'automaps-demo' of the current working
    directory.

    Example usage:

        automaps init-demo"""
    project_name = "automaps-demo"
    project_path = os.path.join(os.getcwd(), project_name)
    try:
        os.mkdir(project_name)
    except FileExistsError:
        print(
            f"Directory '{project_path}' already exists. Please delete the existing "
            "directory."
        )
        sys.exit()
    resource_filenames = [
        "automapsconf.py",
        "automapsconf_poly.py",
        "db.py",
        "demo_data.gpkg",
        "demo_project.qgz",
        "generate_poly.py",
    ]
    for filename in resource_filenames:
        source_path = resource_filename("automaps", "data/demo/" + filename)
        shutil.copy(source_path, project_name)
    os.mkdir(os.path.join(os.getcwd(), project_name, ".streamlit"))
    shutil.copy(
        resource_filename("automaps", "data/demo/.streamlit/config.toml"),
        os.path.join(os.getcwd(), project_name, ".streamlit"),
    )

    print(
        f"Demo project successfully created in {project_path}. Enter "
        "'automaps run dev -c ./automaps-demo/automapsconf.py' to start it."
    )


if __name__ == "__main__":
    cli()
