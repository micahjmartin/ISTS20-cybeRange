from aiohttp import web
import aiohttp_jinja2
from cybeRange import app, routes


@routes.get("/")
@aiohttp_jinja2.template("index.html")
async def hello(request):
    return {"types": list(app["config"].get("mal_types", []))}


@routes.post("/upload")
@aiohttp_jinja2.template("success.html")
async def get_upload(request):
    data = await request.multipart()

    # Get the type of the malware
    field = await data.next()
    # assert field.name == 'type'
    typ = await field.read()  # decode=True)

    # Get the file of the malware
    field = await data.next()
    assert field.name == "warez"
    filename = field.filename

    size = 0
    with open("/tmp/{}".format(filename), "wb") as outfile:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            outfile.write(chunk)

    # TODO: Random Job name here
    # TODO: Actually call the action whenever it works
    return {"filename": filename, "size": size, "job": "asdlfhk4r8fadf"}


if __name__ == "__main__":
    print(app.get("config"))
    app.add_routes(routes)
    web.run_app(app)
