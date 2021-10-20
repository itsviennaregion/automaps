from importlib import import_module
import importlib.util
import os
from pkg_resources import resource_filename
import shutil
import sys

import click

@click.group()
def cli():
    pass


@cli.command(name="run")
@click.argument("app-file")
def run(app_file):
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
        print(f"Directory '{project_path}' already exists. Please choose a different "
               "project name or delete the existing directory.")
        sys.exit()
    resource_filenames = [
        "app.py",
        "automapsconf.py",
        "automapsconf_poly.py",
        "db.py",
        "generate_poly.py",
        "init_project.qgz",
        "test_data.gpkg"
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
        print(f"Directory '{project_path}' already exists. Please delete the existing "
               "directory.")
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

    print(f"Demo project successfully created in {project_path}. Enter "
          "'automaps run ./automaps-demo/app.py' to start it.")


if __name__ == "__main__":
    cli()