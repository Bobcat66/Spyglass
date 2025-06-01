# MIT License
#
# Copyright (c) 2025 FRC 1076 PiHi Samurai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import zmq
import subprocess
import logging
import os
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class response:
    command: str
    exit_code: int
    msg: str

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Use DEBUG for more verbose logs
    format='[%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("spg-rootsrv")

context = zmq.Context()
socket = context.socket(zmq.REP)
rawname = os.getenv("ROOTSRV_SOCK")
socket_name: str
if rawname is not None:
    socket_name = rawname
else:
    raise RuntimeError("ROOTSRV SOCKET NOT FOUND")
socket.bind(socket_name)

# Gives rootsrv-client group access to the socket file, if the system detects that the zmq socket is an IPC socket
if (socket_name[:6] == "ipc://"):
    subprocess.run(["chown","root:rootsrv-client",socket_name[6:]])
    subprocess.run(["chmod","g+rw",socket_name[6:]])

logger.info("spg-rootsrv running on address %s",socket_name)

development = os.getenv("APP_ENV") == "development"

#TODO: Add error handling

#Reserved error codes: 42=development mode, 71=unrecognized commands
while True:
    #JSON Schema: {"command":"<command>",args: list of positional arguments,kwargs: dict of keyword arguments}
    logger.info("heartbeat")
    message = socket.recv_json()
    command = message.get("command")
    logger.info("Received %s request",command)
    msg: str
    exit: int
    match command:
        case "dynamicip":
            if development:
                msg = "rootsrv services are disabled in development mode"
                exit = 42
                break
            subprocess.run(["/opt/Spyglass/bin/rootsrv/netconfig","-d"])
            msg = "success"
            exit = 0
        case "staticip":
            addr = message.get("args")[0]
            if addr is None:
                msg = "no ip address specified"
                exit = 1
                break
            if development:
                msg = "rootsrv services are disabled in development mode"
                exit = 42
                break
            subprocess.run(["/opt/Spyglass/bin/rootsrv/netconfig","-s",addr])
            msg = "success"
            exit = 0
        case _:
            msg = f"unrecognized command '{command}'"
            exit = 71
    logger.info(msg)
    socket.send_json(asdict(response(command,exit,msg)))

logger.info("Shut down rootsrv server")



