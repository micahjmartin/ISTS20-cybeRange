from aiohttp import web
import aiohttp_jinja2
import yaml
import jinja2
import pathlib

routes = web.RouteTableDef()
app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("cybeRange/templates"))

routes.static("/static", "cybeRange/static")


def get_config():
    filename = pathlib.Path(__file__).parent / "config.yml"
    with open(filename) as fil:
        config = yaml.load(fil)
    return config


app["config"] = get_config()
