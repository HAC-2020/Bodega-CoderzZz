import time
import grpc
from speech.proto_speech import audio2text_pb2, audio2text_pb2_grpc, orderinfo2user_pb2, orderinfo2user_pb2_grpc
from speech.Audio2TextGrpcServicer import Audio2TextGrpcServicer, OrderDetails2User

from concurrent.futures import ThreadPoolExecutor

class Audio2TextGrpcServer(object):
    """
    * Start Audio2TextGrpcServer by changing directory to : grpc-server/src
    * Run : python -m speech
    """
    @staticmethod
    def run():
        print("\nAudio Grpc Server is about to run...\n")
        server = grpc.server(ThreadPoolExecutor(max_workers=3))
        audio2text_pb2_grpc.add_Audio2TextServicer_to_server(Audio2TextGrpcServicer(), server)
        orderinfo2user_pb2_grpc.add_OrderInfo2UserServicer_to_server(OrderDetails2User(), server)
        server.add_insecure_port('[::]:5051')
        server.start()
        print("\nAudio Grpc Server is now running...\n")
        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            print("\n\nAudio Grpc Server has stopped.\n")
            server.stop(0)
        server.wait_for_termination()

if __name__ == '__main__':
    Audio2TextGrpcServer.run()
