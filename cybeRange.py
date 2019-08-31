import os
import time
import json
import random
from aiohttp import web
from asyncio import create_task
import aiohttp_jinja2
from cybeRange import app, routes
import hashlib

import base64
from binascii import Error
import re
import subprocess


def getStrings(filename):
    """
    Get the 'strings' output of the data. Only show strings longer than 6
    """
    p = subprocess.Popen(
        ["strings", filename, "-n", "6"], stdout=subprocess.PIPE, text=True
    )
    out, _ = p.communicate()
    strings = out.strip()
    return strings


def getBase64Strings(strings):
    """
    Search the given text for Base64 strings, if they are detected, decode them
    """
    if not strings:
        return ""
    # Find all the base64 strings in the data
    reg = re.compile(r"[A-Za-z0-9+/]{7,}=*")
    # for string in strings:
    base64strings = list(reg.findall(strings))

    valid = []
    for string in base64strings:
        try:
            valid += [base64.standard_b64decode(string).decode()]
        except (UnicodeDecodeError, Error):
            pass
    return "\n".join(valid)


def execute(args, timeout=None):
    """
    Execute a program and return information after execution
    """
    retval = {"status": 255, "stdout": "", "stderr": ""}
    try:
        proc = subprocess.Popen(
            args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        retval["stdout"], retval["stderr"] = proc.communicate(timeout=30)
        retval["status"] = proc.wait()
        retval["message"] = "The process executed normally"
    except subprocess.TimeoutExpired:
        retval["message"] = "The process exceeded the time limit (30 seconds)"
    except UnicodeDecodeError:
        retval["message"] = "Binary output detected in program"
    return retval


async def analyze(filename, filetype, jobid):
    """Async function that will analyze the program and save the results in a json template.
    When /results/JOBID is called, the results file will be read
    """
    output = {"type": filetype, "filename": filename, "jobid": jobid, "antiv": []}

    filename = "jobs/{}/{}".format(jobid, filename)
    command = app["config"].get("mal_types", {}).get(filetype, None)
    command = command.format(filename)
    output["command"] = command

    # Run strings and the program
    output["strings"] = getStrings(filename)
    output["b64_strings"] = getBase64Strings(output["strings"])
    retval = execute(command)
    output.update(retval)

    # Generate fake Anti-virus reports
    for i in app["config"].get("antivirus", ["Kapersky"]):
        if random.choice([True, True, True, True, False]):
            output["antiv"] += [{"av": i, "img": "check.png", "status": "Bypassed"}]
        else:
            output["antiv"] += [{"av": i, "img": "x.png", "status": "Malware Detected"}]

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
    typ = await field.read()  # decode=True)

    # Get the file of the malware
    field = await data.next()
    assert field.name == "warez"
    filename = field.filename

    size = 0

    # Generate a "random" jobid
    hsh = hashlib.md5()
    hsh.update(filename.encode("utf-8"))
    hsh.update(int(time.time()).to_bytes(8, byteorder="big"))
    jobid = hsh.hexdigest()

    # Create the directory we are saving the file in
    outdir = "jobs/" + jobid
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Read the file chunk by chunk and save it on disk
    with open("{}/{}".format(outdir, filename), "wb") as outfile:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            outfile.write(chunk)

    typ = typ.decode("utf-8")

    # Spawn the async function that runs the binary
    create_task(analyze(filename, typ, jobid))

    return {"filename": filename, "size": size, "job": jobid}


@routes.get("/results/{jobid:[\da-z]+}")
@aiohttp_jinja2.template("results.html")
async def results(request):
    jobid = request.match_info["jobid"]
    filename = "jobs/{}/results.json".format(jobid)
    if not os.path.exists(filename):
        return {"message": "Invalid Job", "error": True}
    with open(filename) as fil:
        data = json.load(fil)
    return data


if __name__ == "__main__":
    if not os.path.exists("jobs"):
        os.makedirs("jobs")
    app.add_routes(routes)
    web.run_app(app)
