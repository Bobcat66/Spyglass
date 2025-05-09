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
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("smsight-rootsrv")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket_name = os.getenv("ROOTSRV_SOCK")
socket.bind(socket_name)
logger.info("smsight-rootsrv running on socket %s",socket_name)

development = os.getenv("APP_ENV") == "development"

#TODO: Add error handling

#Reserved error codes: 42=development mode, 71=unrecognized commands
while True:
    #JSON Schema: {"command":"<command>",args: list of positional arguments,kwargs: dict of keyword arguments}
    message = socket.recv_json()
    command = message.get("command")
    logger.info("Received %s command",command)
    msg: str
    exit: int
    match command:
        case "dynamicip":
            if development:
                msg = "rootsrv services are disabled in development mode"
                exit = 42
                break
            subprocess.run(["/opt/SamuraiSight/bin/rootsrv/netconfig","-d"])
            socket.send_json(response("dynamicip",0,"success"))
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
            subprocess.run(["/opt/SamuraiSight/bin/rootsrv/netconfig","-s",addr])
            msg = "success"
            exit = 0
        case _:
            msg = f"unrecognized command '{command}'"
            exit = 71
    logger.info(msg)
    socket.send_json(asdict(response(command,exit,msg)))

logger.info("Shut down rootsrv server")



