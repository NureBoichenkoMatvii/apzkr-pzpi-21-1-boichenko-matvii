import os
from pathlib import Path

from fastapi_babel import Babel, BabelConfigs

configs = BabelConfigs(
    ROOT_DIR=os.path.join(Path(__file__).resolve().parent.parent, "localisation"),
    BABEL_DEFAULT_LOCALE="en_US",
    BABEL_TRANSLATION_DIRECTORY="localisation/locales",
    BABEL_DOMAIN="messages.pot"
)
babel = Babel(configs=configs)
