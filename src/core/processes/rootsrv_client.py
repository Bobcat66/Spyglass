import zmq
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict
import queue

#TODO: Make this run on its own thread
@dataclass
class request:
    command: str
    args: List[str]
    kwargs: Dict[str,str]
_context: zmq.Context[zmq.SyncSocket]
_socket: zmq.SyncSocket

logger = logging.getLogger(__name__)

def initialize(socket_name: str) -> None:
    global _socket,_context
    logger.info("Initialized rootsrv client at socket %s",socket_name)
    _context = zmq.Context()
    _socket = _context.socket(zmq.REQ)
    _socket.connect(socket_name)

#TODO: Make this better and more verbose
def dynamicIP() -> None:
    _socket.send_json(asdict(request("dynamicip",[],{})))
    logger.info("sent dynamicip request")
    response = _socket.recv_json()
    logger.info("received %s",str(response))

def staticIP(ip: str) -> None:
    _socket.send_json(asdict(request("staticip",[ip],{})))
    logger.info("sent staticip request")
    response = _socket.recv_json()
    logger.info("received %s",str(response))