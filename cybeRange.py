from aiohttp import web
import aiohttp_jinja2
from cybeRange import app, routes


@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def hello(request):
    return {
        "types": list(app['config'].get("mal_types", []))
    }

@routes.get('/upload')
async def get_upload(request):
    data = await request.multipart()



if __name__ == '__main__':
    print(app.get('config'))
    app.add_routes(routes)
    web.run_app(app)