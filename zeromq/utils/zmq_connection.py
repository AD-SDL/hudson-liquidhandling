import argparse
import json
import zmq

"""
    A collection of methods helpful in creating and
    managing connections to zmq sockets
"""


def zmq_connect(port=None, pattern="REQ"):
    """
    Connects to a queue on a given port using a
    given communication pattern


    returns a zmq context, zmq socket

    """

    context = zmq.Context()
    if pattern == "REQ":
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:" + str(port))

    return context, socket
