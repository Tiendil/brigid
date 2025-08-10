from brigid.jinja2_render.utils import jinjaglobal


@jinjaglobal
def brigid_repository() -> str:
    return "https://github.com/Tiendil/brigid"
