import sys
import base64
from binascii import Error
import re
import subprocess


def getStrings(filename):
    """Get the 'strings' output of the data. Only show longer strings or ones that are interesting
    """
    p = subprocess.Popen(["strings", filename, "-n", "6"], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    strings = out.decode("utf-8").strip().split("\n")
    return strings


def getBase64Strings(strings):
    if not strings:
        return []
    base64strings = []
    # Find all the base64 strings in the data
    reg = re.compile(r"[A-Za-z0-9+/]{7,}=*")
    for string in strings:
        base64strings += reg.findall(string)
    valid = []
    for string in base64strings:
        try:
            valid += [base64.standard_b64decode(string).decode()]
        except (UnicodeDecodeError, Error):
            pass
    return valid


def execute(args, timeout=None):
    """
    Execute a command. Pass the args as an array if there is more than one
    """
    retval = {"status": 255, "stdout": "", "stderr": ""}
    try:
        proc = subprocess.Popen(
            args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        retval["stdout"], retval["stderr"] = proc.communicate(timeout=30)
        retval["status"] = proc.wait()
        retval["message"] = "The process executed normally"
    except Exception as E:
        print(type(E), E)
        retval["message"] = "The process exceeded the time limit (30 seconds)"
    return retval


def main():
    # Get the strings of the file
    strs = getStrings(sys.argv[1])
    decoded_strs = getBase64Strings(strs)

    print("Detected strings:", strs)
    print("Decoded B64 strings:", decoded_strs)
    # Actually run the file
    print(execute("bash {}".format(sys.argv[1])))


if __name__ == "__main__":
    main()
