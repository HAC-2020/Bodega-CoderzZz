import unittest
import logging
import grpc
import pyaudio
from six.moves import queue
import io
from speech.Speech2TextClient import Speech2TextClient
from speech.proto_speech import audio2text_pb2_grpc
from pathlib import Path

class TestAllAudioFiles(unittest.TestCase):

    """
        1) Run Tests in Terminal by changing directory to : grpc-client/test
        2) In Audio2TextGrpcServicer, change encoding from .LINEAR16 to .FLAC if not already
        3) Run this : python -m unittest -vvv  speech.TestAllAudioFiles
    """

    def setUp(self):
        return

    def tearDown(self):
        return

    def testDefaultSize(self):
        return

    def testResize(self):
        return

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

    def test_normal5sec(self):
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/normal_5sec.flac"
            stringResp = []
            with self.ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                expected = "hello my name is John and I'm 27 years old"
                self.assertEqual(expected, stringResp[len(stringResp) - 1])

    def test_normal15sec(self):
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/normal_15sec.flac"
            stringResp = []
            with self.ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                expected = "probably the most effective way to achieve paragraph Unity is to express a central idea of the paragraph in a topic sentence topic sentences are similar to mini thesis statement"
                self.assertEqual(expected, stringResp[len(stringResp) - 1])

    def test_normal1min15sec(self):
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/normal_1min15sec.flac"
            stringResp = []
            with self.ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                expected = "probably the most effective way to achieve paragraph Unity specs versus central idea of the paragraph in the topic sentence topic sentences are similar to Mini PC statement like a thesis statement and topic sentence has a specific mean Point whereas there is the main point of the essay on the topic sentence is the main point of the paragraph like this statement a topic sentence has a unifying function but a statement or topic sentence alone doesn't guarantee Unity an essay is Unified if all the paragraph relate to the thesis wear as a paragraph is Unified if all the sentences relate to the topic sentence note not all the paragraph new topic sentences in particular opening and closing paragraph with serve different functions from body paragraph General don't have topic sentences in a guy to make writing the topic sentence nearly always works best at the beginning of a paragraph so that the reader knows what to expect"
                self.assertEqual(expected, stringResp[len(stringResp) - 1])



    def test_speech_noise_speech1(self):
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/speech_noise_speech1.flac"
            stringResp = []
            with self.ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                expected = "hello my name is John and I'm 27 years old actually I'm 28 years old"
                self.assertEqual(expected, stringResp[len(stringResp) - 1])

    def test_speech_noise_speech2(self):
        with grpc.insecure_channel('localhost:5051') as channel:
            stub = audio2text_pb2_grpc.Audio2TextStub(channel)
            spx2TxtClient = Speech2TextClient()
            localFilePath = str(Path.home()) + "/github/grpc/grpc-client/test/speech/audioFiles/speech_noise_speech2.flac"
            stringResp = []
            with self.ReadAudioFile(16000, 100) as stream:
                for transcript in spx2TxtClient.streamingRecognize(stub, localFilePath, stream):
                    stringResp.append(transcript)
                expected = "hello how are you doing would you like some breakfast"
                self.assertEqual(expected, stringResp[len(stringResp) - 1])




