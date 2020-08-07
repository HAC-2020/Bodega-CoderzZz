import logging
import grpc
from speech.proto_speech import audio2text_pb2, audio2text_pb2_grpc


class Speech2TextClient(object):
    """
    * Interacts with MicrophoneStream type Object and accepts streamed audio bytes from it.
    * Streams this data to Audio2TextGrpcServicer(Server) and Streams back text of audio to MicrophoneStream(Client)
    """
    class SpeechBytesSourceInterface:
        def streamAudioContent (self) :
            "Stream the audio content for transcription"

    def streamingRecognizeRequest(self, speechBytesSourceInterface):
        """
        * Streams "Serialized Request" to streamingRecognize
        """
        for audio_content in speechBytesSourceInterface.streamAudioContent():
            yield audio2text_pb2.StreamingRecognizeRequest( audio_content = audio_content )

    def streamingRecognize(self, stub, speechBytesSourceInterface):
        """
        * This function links the Server and the Client.
        * Then, it Accepts Streamed Responses from server and then streams string of responses back to MicrophoneStream
        :param stub: Consists of data that bridges Server and client
        :param speechBytesSourceInterface: Takes audio from MicrophoneStream via Interface, which is sent to get Serialized
        :return:
        """
        print("In streamingRecognize")
        requests = self.streamingRecognizeRequest(speechBytesSourceInterface)
        for response in stub.StreamingRecognize(requests):
            results = response.results
            for result in results:
                alternatives = result.alternatives
                for alternative in alternatives:
                    yield alternative.transcript




    class SpeechBytesSourceImpl:

        def streamAudioContent(self) :
            messages = [
                bytes("\x9e\x06\xd7\t\xd0\tQ\x06", 'utf-8'),
                bytes("asdf", 'utf-8'),
                b'\x9e\x06\xd7\t\xd0\tQ\x06',
                b'\x9e\x06\xd7\t\xd0\tQ\x06',
                b'\x9e\x06\xd7\t\xd0\tQ\x06\xfa\x03\x06\x04\x1c\xfe\xdc\xfb\xdf\x046\rv\x0b\xcf\xff\xfb\xfa\xd9\xff\x15\x05\xc3\x06\xd6\x07\x98\x06a\x01\xc8\xffp\xff\xb0\xfd}\xfc\x15\x01r\x05\xb2\x04\xff\x00\x16\xfd~\xfe^\x02\x0b\t\x81\x05\xe4\x01b\x06\x9c\x04\xcb\x03\x00\x02\xc3\x01\x96\x01\x91\xffg\x00Z\xff>\xfe<\x05\xbe\x13\xc2\x02\x9b\xec\x97\x0f\xce(q\x15"\x06W\x0e\xb9\x15\xd4\xfcZ\xf2|\x0f\x82\'\r\x0e\xe0\xf3\xb0\n(\r\x1d\xff\x85\x0bg\x11\xa2\x00B\x03\xed\x16\x1e\x0f\\\xff\x16\xf6\xa0\xf9\xc1\r9\x0f\xf1\x02W\t \x0cM\xfdW\x01\n\x12\\\x0f9\x079\x0f\x83\x13\x07\x0bG\x05S\x03@\x05\xfb\x04\xc1\x03\xa8\x0b\xa0\x11\xda\x02O\xfb\xcb\r\x10\x15\xe5\r\x99\x0b^\x11\x9f\x12~\x06',
                b'\x9e\x06\xd7\t\xd0\tQ\x06\xfa\x03\x06\x04\x1c\xfe\xdc\xfb\xdf\x046\rv\x0b\xcf\xff\xfb\xfa\xd9\xff\x15\x05\xc3\x06\xd6\x07\x98\x06a\x01\xc8\xffp\xff\xb0\xfd}\xfc\x15\x01r\x05\xb2\x04\xff\x00\x16\xfd~\xfe^\x02\x0b\t\x81\x05\xe4\x01b\x06\x9c\x04\xcb\x03\x00\x02\xc3\x01\x96\x01\x91\xffg\x00Z\xff>\xfe<\x05\xbe\x13\xc2\x02\x9b\xec\x97\x0f\xce(q\x15"\x06W\x0e\xb9\x15\xd4\xfcZ\xf2|\x0f\x82\'\r\x0e\xe0\xf3\xb0\n(\r\x1d\xff\x85\x0bg\x11\xa2\x00B\x03\xed\x16\x1e\x0f\\\xff\x16\xf6\xa0\xf9\xc1\r9\x0f\xf1\x02W\t \x0cM\xfdW\x01\n\x12\\\x0f9\x079\x0f\x83\x13\x07\x0bG\x05S\x03@\x05\xfb\x04\xc1\x03\xa8\x0b\xa0\x11\xda\x02O\xfb\xcb\r\x10\x15\xe5\r\x99\x0b^\x11\x9f\x12~\x06',

            ]

            for msg in messages:
                print(msg)
                yield msg


    @staticmethod
    def run():
        print("Running  MicrophoneStream...")

        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            speechBytesSource = Speech2TextClient.SpeechBytesSourceImpl()
            print("grpc call about to start")
            transcripts = spx2TxtClient.streamingRecognize(stub, speechBytesSource)
            print("grpc call done")
            for transcript in transcripts:
                print(transcript)

if __name__ == '__main__':
    logging.basicConfig()
    Speech2TextClient.run()