"""
Import required library functions, modules, APIs.
"""

from __future__ import print_function, division
import logging
import time
import re
import os
import sys
import subprocess as sp
import signal
import pyaudio
import grpc
from six.moves import queue
from pathlib import Path

"""
Install required dependencies if not present by default in system.
"""

try:
    from google.cloud import speech
except:
    sp.call("pip install google.cloud", shell=True)
    from google.cloud import speech

try:
    from google.cloud.speech import enums
except:
    sp.call("pip install google-cloud-speech", shell=True)
    from google.cloud.speech import enums

from google.cloud.speech import types

"""
Proto Buffer Files.
"""
# from .generated import audio_pb2
# from .generated import audio_pb2_grpc

# Validate Credentials to access Google Cloud Speech-To-Text API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path.home()) + "/github/grpc/grpc-server/config/gapi_credentials/credentials.json"

# Audio Recording Parameters
sample_rate_hertz = 16000
audio_chunk = 100


# Checks for NO RESPONSE from User in first 4 seconds

def check(flag):
    if (flag == 0):
        print("Flag is 0 so exiting...")
        signal.signal(signal.SIGALRM, receive_alarm)
    else:
        signal.alarm(0)


# In case of NO RESPONSE from User in first 4 seconds, termination of program takes place,

def receive_alarm(signum, stack):
    sys.exit("Time Up!")


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

    def generator(self):

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

            # print ("data", data)
            yield b''.join(data)

            # bytes = b''.join('\x9e\x06\xd7\t\xd0\tQ\x06\xfa\x03\x06\x04\x1c\xfe\xdc\xfb\xdf\x046\rv\x0b\xcf\xff\xfb\xfa\xd9\xff\x15\x05\xc3\x06\xd6\x07\x98\x06a\x01\xc8\xffp\xff\xb0\xfd}\xfc\x15\x01r\x05\xb2\x04\xff\x00\x16\xfd~\xfe^\x02\x0b\t\x81\x05\xe4\x01b\x06\x9c\x04\xcb\x03\x00\x02\xc3\x01\x96\x01\x91\xffg\x00Z\xff>\xfe<\x05\xbe\x13\xc2\x02\x9b\xec\x97\x0f\xce(q\x15"\x06W\x0e\xb9\x15\xd4\xfcZ\xf2|\x0f\x82\'\r\x0e\xe0\xf3\xb0\n(\r\x1d\xff\x85\x0bg\x11\xa2\x00B\x03\xed\x16\x1e\x0f\\\xff\x16\xf6\xa0\xf9\xc1\r9\x0f\xf1\x02W\t \x0cM\xfdW\x01\n\x12\\\x0f9\x079\x0f\x83\x13\x07\x0bG\x05S\x03@\x05\xfb\x04\xc1\x03\xa8\x0b\xa0\x11\xda\x02O\xfb\xcb\r\x10\x15\xe5\r\x99\x0b^\x11\x9f\x12~\x06')
            # yield bytes


""" 
Iterates through server responses and prints them.

The responses passed is a generator that will send "terminate client code" request
if response is of over 1 minute or 4 seconds of inactivity is detected.
"""


def listen_print_loop(responses):
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
            sys.stdout.write(transcript + '\r')
            sys.stdout.flush()

        else:

            print(transcript)
            break


def main():
    # Start a timer of 4 seconds to check inactivity of user at the beginning of code.
    # signal.alarm(4)

    client = speech.SpeechClient()

    # Audio Recognition Configurations...
    language_code = 'en-US'  # English-(US)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    # Stream audio to print for simultaneous speech to text
    with MicrophoneStream(sample_rate_hertz, audio_chunk) as stream:
        print("\n\nYou may Speak Now...\n\n")
        audio_generator = stream.generator()

        requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses)


def run():
    # with grpc.insecure_channel('localhost:50051') as channel:
    #     stub = audio_pb2_grpc.AudioStub(channel)
        main()


if __name__ == '__main__':
    logging.basicConfig()
    run()