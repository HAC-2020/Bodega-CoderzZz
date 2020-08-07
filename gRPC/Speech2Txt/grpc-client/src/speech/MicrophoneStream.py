import pyaudio
from six.moves import queue
from speech.Speech2TextClient import Speech2TextClient
import grpc
from speech.proto_speech import audio2text_pb2_grpc

class MicrophoneStream(Speech2TextClient.SpeechBytesSourceInterface):
    """
    * In Audio2TextGrpcServicer, change encoding from .FLAC to .LINEAR16 if not already
    * Run Code by changing directory to grpc-client/src:
        python -m speech.MicrophoneStream
    * Objects of this class open mic Interface
    """

    def __init__(self, audio_rate, audio_chunk):
        """
        * Opens Recording Stream and takes "chunks" of audio
        * Gets called upon object creation
        :param audio_rate: Rate in hertz of Audio (16000 Hz)
        :param audio_chunk: Size of Audio Packets (100 ms)
        """
        self._rate = audio_rate
        self._chunk = audio_chunk
        # Create a thread-safe buffer for audio data
        self._buff = queue.Queue()
        self.closed = True


    def __enter__(self):
        """
        * Enters Audio Stream to start receiving audio via PyAudio
        * Called when object of class "MicrophoneStream" is created using "with"
          statement and lasts till within it's scope, i.e self.closed remains False until
          outside "with" scope
        """
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,

            # API currently supports "mono-channel" audio only.
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,

            # Runs audio stream asynchronously to fill buffer object to avoid input device overflow.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        """
        * Gets executed as soon as call flow exits the scope of "with" of the Mic.
        * Closes Mic Stream, buffer memory is cleared and mic Interface is terminated.
        """
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """
        * Continuously collect data from the audio stream, into the buffer.
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def streamAudioContent(self):
        """
        * Ensures presence of at least 1 chunk data and sends "terminate client code" if no chunk present
        * i.e. Stream Audio Content as "bytes" until End of Speech is Detected.
        """
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    @staticmethod
    def run():
        """
        * Creates a TCP session with Server, Creates Mic Interface and prints streamed responses
        """
        try:
            with grpc.insecure_channel('localhost:5051') as channel:
                print("Running  MicrophoneStream...")
                stub = audio2text_pb2_grpc.Audio2TextStub(channel)
                spx2TxtClient = Speech2TextClient()
                with MicrophoneStream(16000, 100) as stream:
                    for transcript in spx2TxtClient.streamingRecognize(stub, stream):
                        print("Transcript : ", transcript)
                        # sys.stdout.write(transcript + '\r')

        except KeyboardInterrupt:
            print("\n\nGrpc Client has stopped.\n")
        # except grpc.StatusCode.UNAVAILABLE :
        #     print("\n\nAudio Grpc Server is Shut Down.\n")


if __name__ == '__main__':
    MicrophoneStream.run()
