import sys
import base64
from binascii import Error
import re
import subprocess


def getStrings(filename):
    """Get the 'strings' output of the data. Only show longer strings or ones that are interesting
    """
    p = subprocess.Popen(
        ["strings", filename, "-n", "6"], stdout=subprocess.PIPE, text=True
    )
    out, _ = p.communicate()
    strings = out.strip()
    return strings


def getBase64Strings(strings):
    if not strings:
        return ""
    # Find all the base64 strings in the data
    reg = re.compile(r"[A-Za-z0-9+/]{7,}=*")
    # for string in strings:
    base64strings = list(reg.findall(strings))
    # base64strings = []

    valid = []
    for string in base64strings:
        try:
            valid += [base64.standard_b64decode(string).decode()]
        except (UnicodeDecodeError, Error):
            pass
    return "".join(valid)


def execute(args, timeout=None):
    """
    Execute a command. Pass the args as an array if there is more than one
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
