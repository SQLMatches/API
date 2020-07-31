from starlette.templating import Jinja2Templates

from .resources import Config

TEMPLATE = Jinja2Templates(directory=Config.templates_dir)
