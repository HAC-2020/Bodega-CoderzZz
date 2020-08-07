import logging
import grpc
import pyaudio
from six.moves import queue
import io
from speech.Speech2TextClient import Speech2TextClient
from speech.proto_speech import audio2text_pb2_grpc
from pathlib import Path


class ReadAudioFile(object):

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
        self._buff.put(None)

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def streamAudioContent(self, localFilePath):

        with io.open(localFilePath, 'rb') as audio_file:
            data = audio_file.read()
            stream = [data]
            yield b''.join(stream)

    @staticmethod
    def trial():
        print("TestSpeech2TextClient.test_normal5sec()\n")
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/normal_15sec.flac"
            stringResp = []
            with ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                print(stringResp[len(stringResp) - 1])

if __name__ == '__main__':
    logging.basicConfig()
    ReadAudioFile.trial()
