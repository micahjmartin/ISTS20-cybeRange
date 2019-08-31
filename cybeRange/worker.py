import sys
import base64
from binascii import Error
import asyncio
import re

def getStrings(filename):
    """Get the 'strings' output of the data. Only show longer strings or ones that are interesting
    """
    cmd = "strings {}".format(filename)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )

    # Sort only the strings longer than 6 chars
    strings = [x for x in strings if len(x) > 6]
    return strings

def getBase64Strings(strings):
    if not strings:
        return []
    # Find all the base64 strings in the data
    reg = re.compile(r"^[A-Za-z0-9+/]+=+$")
    base64strings = list(filter(reg.match, strings))
    valid = []
    for string in base64strings:
        try:
            valid += [base64.standard_b64decode(string).decode()]
        except (UnicodeDecodeError, Error) as E:
            pass
    print(valid)

def execute(args, timeout=None):
    '''
    Execute a command. Pass the args as an array if there is more than one
    '''
    retval = {'status': 255}
    try:
        proc = Popen(args, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                     close_fds=True)
        retval['stdout'] = proc.stdout.read().decode("utf-8")
        retval['stderr'] = proc.stderr.read().decode("utf-8")
        retval['status'] = proc.wait(timeout=timeout)
    except Exception as E:
        print(args)
        print(E)
    return retval

def main():
    # Get the strings of the file
    strs = getStrings(sys.argv[1])
    decoded_strs = getBase64Strings(strs)
    # Actually run the file


if __name__ == "__main__":
    main()