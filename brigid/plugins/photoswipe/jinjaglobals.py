from brigid.theme.utils import jinjafilter, jinjaglobal
from brigid.plugins.photoswipe.settings import settings, Settings


# TODO: do we need this now?
@jinjaglobal
def photoswipe_settings() -> Settings:
    return settings
