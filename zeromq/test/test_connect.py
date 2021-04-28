import os
import sys
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://hudson01.bio.anl.gov:5556")

socket.send(b"Hi")
reply = socket.recv()
print(reply)

# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5556")


# while True: 
#     message = socket.recv()
#     decoded = message.decode('utf-8')
    
#     print(f"Message received: {decoded}")
    
#     socket.send(b"Message received")
    
 
    
