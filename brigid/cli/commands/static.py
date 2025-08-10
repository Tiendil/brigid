import asyncio
import sys
import typer
import pathlib
from brigid.library.storage import storage
from brigid.application.application import with_app
from brigid.cli.application import app
from brigid.core import logging
from brigid.jinja2_render.templates import environment
from brigid.plugins.utils import plugins
from brigid.domain.urls import UrlsPlugin, UrlsRoot
from brigid.domain import request_context

logger = logging.get_module_logger()


static_cli = typer.Typer()


async def run() -> None:
    async with with_app():
        files = []

        site = storage.get_site()

        with request_context.init():
            request_context.set("storage", storage)

            for plugin in plugins():
                url = UrlsPlugin(plugin.slug, language=site.default_language)

                for file_info in plugin.static_files():
                    full_path = pathlib.Path(file_info.sys_path).resolve()
                    files.append(f"{full_path}\t->\t{url.file_url(file_info.url_path)}")

        files.sort()

        sys.stdout.write('\n'.join(files) + '\n')


@static_cli.command()
def list() -> None:
    asyncio.run(run())


app.add_typer(static_cli, name="static", help="Manage static files")
