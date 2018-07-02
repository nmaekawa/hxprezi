from dotenv import load_dotenv
import os
# if dotenv file, load it now
dotenv_path = os.environ.get('HXPREZI_DOTENV_PATH', None)
if dotenv_path:
    load_dotenv(dotenv_path)

from flask.helpers import get_debug_flag
from hxprezi.settings import DevConfig, ProdConfig
CONFIG = DevConfig if get_debug_flag() else ProdConfig

from hxprezi.app import create_app
application = create_app(CONFIG)
