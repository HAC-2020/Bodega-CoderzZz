"""
Import required library functions, modules, APIs.
"""
from __future__ import print_function, division
import logging
import os
from google.cloud import speech
from google.cloud.speech import enums, types
from pathlib import Path
from six.moves import queue
import pyaudio

class GoogleSpeech2TextClient(object):
    """
    * Testing of recognizeRequest
    """
    # Validate Credentials to access Google Cloud Speech-To-Text API
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path.home()) + "/github/grpc/grpc-server/config/gapi_credentials/credentials.json"

    def recognizeRequest(self, audioClientRequests):
        spxClient = speech.SpeechClient()

        language_code = 'en-US'  # English-(US)
        sample_rate_hertz = 16000

        audioRecogConfig = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate_hertz,
            language_code=language_code)

        audioStreamingConfig = types.StreamingRecognitionConfig(config=audioRecogConfig, interim_results=True)

        requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audioClientRequests)

        responses = spxClient.streaming_recognize(audioStreamingConfig, requests)

        return responses



class MicrophoneStream(object):

    # Opens Recording Stream and takes "chunks" of audio
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer for audio data
        self._buff = queue.Queue()
        self.closed = True

    # Enters Audio Stream to start receiving audio via PyAudio
    def __enter__(self):
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

    # Exits Audio Stream, ending client code.

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    # Continuously collect data from the audio stream, into the buffer.

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def streamAudioContent(self):

        # Ensures presence of at least 1 chunk data and sends "terminate client code" request if no chunk present i.e. End of Speech
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

def GoogleSpeech2TextClientTest():
    gSpx2TxtClient = GoogleSpeech2TextClient()
    with MicrophoneStream(16000, 100) as stream:
        print("\nYou may Speak Now...\n")
        audioStream = stream.streamAudioContent()
        responses = gSpx2TxtClient.recognizeRequest(audioStream)
        for response in responses:
            printResponses(response)

def printResponses(responses):
    for response in responses:

        # End of Speech Detection
        if not response.results:
            break

        # Store the most probable result
        result = response.results[0]
        if not result.alternatives:
            continue

        # Stores result in transcript
        transcript = result.alternatives[0].transcript

        # If not yet the last detected word, print the transcript and continue printing in same line.
        # Else, print with end as new line.

        if not result.is_final:
            print(transcript)
        else:
            print(transcript)
            break

if __name__ == '__main__':
    logging.basicConfig()
    GoogleSpeech2TextClientTest()