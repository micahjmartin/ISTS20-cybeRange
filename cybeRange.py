import os
import time
import json
import random
from aiohttp import web
from asyncio import create_task
import aiohttp_jinja2
from cybeRange import app, routes
import hashlib
from cybeRange.worker import getBase64Strings, getStrings, execute


async def analyze(filename, filetype, jobid):
    filename = "jobs/{}/{}".format(jobid, filename)
    command = app["config"].get("mal_types", {}).get(filetype, None)
    command = command.format(filename)

    output = {
        "command": command,
        "type": filetype,
        "filename": filename,
        "jobid": jobid,
        "strings": getStrings(filename),
        "antiv": [],
    }
    output["b64_strings"] = getBase64Strings(output["strings"])
    retval = execute(command)
    output.update(retval)

    # Generate fake Anti-virus reports
    for i in ["Clam AV", "Norton", "Kapersky", "MalwareBytes", "McAffee"]:
        if random.choice([True, True, True, True, False]):
            output["antiv"] += [{"av": i, "img": "check.png"}]
        else:
            output["antiv"] += [{"av": i, "img": "x.png"}]

    # Save the results
    with open("jobs/{}/results.json".format(jobid), "w") as ofil:
        ofil.write(json.dumps(output))


@routes.get("/")
@aiohttp_jinja2.template("index.html")
async def hello(request):
    return {"types": list(app["config"].get("mal_types", {}).keys())}


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

    # Generate a jobid
    hsh = hashlib.md5()
    hsh.update(filename.encode("utf-8"))
    hsh.update(int(time.time()).to_bytes(8, byteorder="big"))
    jobid = hsh.hexdigest()
    outdir = "jobs/" + jobid
    # Create the directory we are saving the file in
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open("{}/{}".format(outdir, filename), "wb") as outfile:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            outfile.write(chunk)

    # Get the command to execute for that type
    typ = typ.decode("utf-8")

    create_task(analyze(filename, typ, jobid))

    return {"filename": filename, "size": size, "job": jobid}


@routes.get("/results/{jobid:[\da-z]+}")
@aiohttp_jinja2.template("results.html")
async def results(request):
    jobid = request.match_info["jobid"]
    # Save the results
    filename = "jobs/{}/results.json".format(jobid)
    if not os.path.exists(filename):
        return {"message": "Invalid Job", "error": True}
    with open(filename) as fil:
        data = json.load(fil)

    return data


if __name__ == "__main__":
    print(app.get("config"))
    if not os.path.exists("jobs"):
        os.makedirs("jobs")
    app.add_routes(routes)
    web.run_app(app)
