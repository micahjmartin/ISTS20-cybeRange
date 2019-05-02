from aiohttp import web
from cybeRange import app, routes


@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")


if __name__ == '__main__':
    app.add_routes(routes)    
    web.run_app(app)