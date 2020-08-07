import grpc
import time
from temp.proto_order import temp_pb2, temp_pb2_grpc
from concurrent.futures import ThreadPoolExecutor
from temp.Servicer import GreeterServicer


class Server(object):
    """
    * Start Audio2TextGrpcServer by changing directory to : grpc-server/src
    * Run : python -m speech.Server
    """
    @staticmethod
    def run():
        print("\nFlutter-Grpc Server is about to run...\n")
        server = grpc.server(ThreadPoolExecutor(max_workers=3))
        temp_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print("\nFlutter-Grpc Server is now running...\n")
        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            print("\n\nFlutter-Grpc Server has stopped.\n")
            server.stop(0)
        server.wait_for_termination()

if __name__ == '__main__':
    Server.run()