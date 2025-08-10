import asyncio
import sys
import typer
import pathlib

from brigid.application.application import with_app
from brigid.cli.application import app
from brigid.core import logging
from brigid.jinja2_render.templates import environment

logger = logging.get_module_logger()


templates_cli = typer.Typer()


async def run() -> None:
    async with with_app():
        templates = []

        env = environment()
        for template_path in env.list_templates():
            template = env.get_template(template_path)
            full_path = pathlib.Path(template.filename).resolve()
            templates.append(f"{full_path}\t->\t{template_path}")

        templates.sort()

        sys.stdout.write('\n'.join(templates) + '\n')


@templates_cli.command()
def list() -> None:
    asyncio.run(run())


app.add_typer(templates_cli, name="templates", help="Manage Jinja2 templates")
