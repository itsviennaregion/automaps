from importlib import import_module
import importlib.util
import os
from pathlib import Path
from pkg_resources import require, resource_filename
import shutil
import subprocess
import sys

import click


def _process_config_file(config_file):
    config_path = str(Path(config_file).absolute().parent)
    if config_path not in sys.path:
        sys.path.insert(0, config_path)


@click.group()
def cli():
    pass


@cli.group()
def run():
    pass


@run.command(name="registry")
@click.option("-c", "--config-file", type=click.Path(exists=True), required=True)
def run_registry(config_file):
    _process_config_file(config_file)
    from automaps.registry.registry import Registry

    registry = Registry()
    registry.listen()


@run.command(name="worker")
@click.option("-c", "--config-file", type=click.Path(exists=True), required=True)
@click.argument("port", type=int)
def run_worker(config_file, port):
    _process_config_file(config_file)
    from automaps.worker.worker import QgisWorker

    QgisWorker(port)


@run.command(name="frontend")
@click.option("-c", "--config-file", type=click.Path(exists=True), required=True)
def run_frontend(config_file):
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


@cli.command(name="run-dev")
@click.argument("app-file")
def run_dev(app_file):
    module_name = "automaps_project"
    spec = importlib.util.spec_from_file_location(module_name, app_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


@cli.command(name="init-project")
@click.argument("project-name")
def init_project(project_name):
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
        "app.py",
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
        "app.py",
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
        "'automaps run ./automaps-demo/app.py' to start it."
    )


if __name__ == "__main__":
    cli()
