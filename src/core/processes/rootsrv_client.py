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
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict

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