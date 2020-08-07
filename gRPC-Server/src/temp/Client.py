import logging
import grpc
import hashlib
from datetime import datetime
from temp.proto_order import temp_pb2, temp_pb2_grpc


class Client(object):

    @staticmethod
    def run():
        """
        * Creates a TCP session with Server
        """
        try:
            with grpc.insecure_channel('localhost:50051') as channel:
                
                print("Send a Message : ", end = '')
                userMsg = str(input())
                
                stub = temp_pb2_grpc.GreeterStub(channel)

                response = stub.SayHello(temp_pb2.HelloRequest(name = userMsg))
                print(response.message)

            

        except KeyboardInterrupt:
            print("\n\nClient has stopped.\n")

if __name__ == '__main__':
    logging.basicConfig()
    Client.run()