import socket
import json
from datetime import datetime
import time
from temp.proto_order import temp_pb2, temp_pb2_grpc

class GreeterServicer(temp_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):


        userMsg = request
        print("Got Connected with : ", socket.gethostbyname(socket.gethostname())) 
        print("User Sent -> ", userMsg.name)
        print("Got Disconnected with : ", socket.gethostbyname(socket.gethostname()))
        return temp_pb2.HelloReply(message = "Hello " + userMsg.name)

