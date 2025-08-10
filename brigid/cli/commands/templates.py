import asyncio
import pathlib
import sys

import typer

from brigid.application.application import with_app
from brigid.cli.application import app
from brigid.core import logging
from brigid.jinja2_render.templates import environment

logger = logging.get_module_logger()


templates_cli = typer.Typer()


async def run_list() -> None:
    async with with_app():
        templates = []

        env = environment()
        for template_path in env.list_templates():
            template = env.get_template(template_path)
            full_path = pathlib.Path(template.filename).resolve()
            templates.append(f"{full_path}\t->\t{template_path}")

        templates.sort()

        sys.stdout.write("\n".join(templates) + "\n")


@templates_cli.command()
def list() -> None:
    asyncio.run(run_list())


async def run_copy(destination: pathlib.Path) -> None:
    async with with_app():
        env = environment()

        if not destination.exists():
            logger.info("creating_destination_directory", path=destination)
            destination.mkdir(parents=True, exist_ok=True)

        for template_path in env.list_templates():
            template = env.get_template(template_path)
            full_path = pathlib.Path(template.filename).resolve()

            destination_file = destination / template_path
            destination_file.parent.mkdir(parents=True, exist_ok=True)

            logger.info("copying_template", source=str(full_path), destination=str(destination_file))

            with open(destination_file, "w", encoding="utf-8") as f:
                f.write(full_path.read_text(encoding="utf-8"))


@templates_cli.command()
def copy(destination: pathlib.Path) -> None:
    """Copy all Jinja2 templates to the specified destination directory.

    May be helpfull:

    - for starting a new theme
    - for collecting all html code for tailwind to generate an optimal CSS file

    """
    asyncio.run(run_copy(destination))


app.add_typer(templates_cli, name="templates", help="Manage Jinja2 templates")
