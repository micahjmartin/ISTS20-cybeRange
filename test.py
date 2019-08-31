"""This program will allow the scoring engine to generate and upload scripts to teh website automatically.

It might be a good idea to randomize the types of scripts that are uploaded to make it harder to cheat teh engine
"""

import requests
import random
import string
import base64
import time
import re

mal_names = [
    "l33t_warez.sh",
    "dank_shellz",
    "meterpreter",
    "code.txt",
    "test.sh",
    "ls",
    "whoami",
    "a.sh",
    "a",
    "tmp",
    "v2",
    "v6",
]


def generate_script(type="bash"):
    """This function generates a script that should print out 3 different flags"""
    retval = """#!/bin/bash
    echo this is some cool malware;
    echo stderr >&2;
    echo {flag};
    echo {flag2} | base64 -d;
    echo
    echo {flag3} > flagfile;
    echo START;
    cat flagfile;
    ls -d /*;
    # {flag4}
    echo "user = `whoami`"
    """

    flag1 = "".join(random.choice(string.ascii_letters) for i in range(48))

    # This flag should only exist if the program decodes the string
    flag2 = "".join(random.choice(string.ascii_letters) for i in range(48))
    flag2_b64 = base64.standard_b64encode(flag2.encode("utf-8")).decode()

    # This flag should be printed out after START proving that we can read/write to files
    flag3 = "".join(random.choice(string.ascii_letters) for i in range(48))

    # This flag just sits in the program and should be decoded by the analysis portion instead of during runtime
    flag4 = "".join(random.choice(string.ascii_letters) for i in range(12))
    flag4_b64 = base64.standard_b64encode(flag4.encode("utf-8")).decode()

    retval = retval.format(flag=flag1, flag2=flag2_b64, flag3=flag3, flag4=flag4_b64)

    return retval, (flag1, flag2, "START\n.*{}".format(flag3), "/bin", flag4)


def test(server):
    """This function will generate a script and have the server run it"""

    filename = random.choice(mal_names)
    script, flags = generate_script()
    multipart_form_data = {
        "type": ("", "bash"),
        "warez": (filename, script.encode("utf-8")),
    }
    # Send the script to the server
    response = requests.post("{}/upload".format(server), files=multipart_form_data)

    if response:
        content = response.content.decode("utf-8")

    if response.status_code != 200:
        print(
            "FAIL: Submission of the script failed. Code:",
            response.status_code,
            "Content:",
            content,
        )
        return

    # Assume it worked, Get the job ID from the response
    jobid = re.search(r"href=\"/results/([\d[a-z]+)\"", content)

    if not jobid:
        print("FAIL: No JOBID detected in response. Content:", content)
        return

    jobid = jobid.group(1)

    # Wait a few seconds for the script to run
    time.sleep(3)

    # Get the results from the script and search for the flags within them
    results = "{}/results/{}".format(server, jobid)
    print("Getting results from", results)
    resp = requests.get(results)

    if resp:
        content = resp.content.decode("utf-8")

    if resp.status_code != 200:
        print(
            "FAIL: Getting results failed. Code:", resp.status_code, "Content:", content
        )
        return

    # Search through the content for the flags
    for flag in flags:
        if not re.search(flag, content):
            print("FAIL: Missing flag in output (Did the script run?):", flag)
            return
    print("SUCCESS: all flags found in the program output")


if __name__ == "__main__":
    test("http://192.168.177.128:8080")
