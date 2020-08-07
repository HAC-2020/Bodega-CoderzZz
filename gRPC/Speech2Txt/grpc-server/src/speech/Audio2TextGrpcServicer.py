"""
Import required library functions, modules, APIs.
"""
from __future__ import print_function, division
from speech.proto_speech import audio2text_pb2, audio2text_pb2_grpc
import socket
from google.cloud import speech
from google.cloud.speech import enums, types
import os
from pathlib import Path
import logging

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path.home()) + "/github/grpc/grpc-server/config/gapi_credentials/credentials.json"


class Audio2TextGrpcServicer(audio2text_pb2_grpc.Audio2TextServicer):

    """
    * Speech to Text Service provided by bridging Google API and Client.
    """

    def makeSpeechRecognitionAlternative(self, transcript):
        """
        :param transcript: Returns "Serialized" string from the alternative predicted by Google
        """
        return audio2text_pb2.SpeechRecognitionAlternative(
            transcript=transcript
        )

    def makeStreamingRecognitionResult(self, transcript):
        """
        :param transcript: Returns "Serialized" most probable alternative
        """
        alternatives = []
        alternative = self.makeSpeechRecognitionAlternative(transcript)
        alternatives.append(alternative)
        return audio2text_pb2.StreamingRecognitionResult(
            alternatives=alternatives
        )

    def makeStreamingRecognizeResponse(self, transcript):
        """
        :param transcript: Returns "Serialized" prediction of Google
        """
        print("Making response")
        results = []
        result = self.makeStreamingRecognitionResult(transcript)
        results.append(result)

        return audio2text_pb2.StreamingRecognizeResponse(
            results=results
        )

    def makeGoogleResponsesToTranscript(self, response):
        """
        * Returns string of Prediction
        """

        if not response.results:
            return

        # Store the most probable result
        result = response.results[0]
        if not result.alternatives:
            return

        transcript = result.alternatives[0].transcript

        if not result.is_final:
            return transcript, 0
        else:
            return transcript, 1

    def makeGoogleStreamingRecognizeRequest(self, request_iterator):
        """
        * Sends audio bytes to StreamingRecognize in a form recognizable by Google
        :param request_iterator: Audio bytes from Client
        """
        for request in request_iterator:
            yield types.StreamingRecognizeRequest(audio_content=request.audio_content)

    def StreamingRecognize(self, request_iterator, context):
        """
        * Links Google and Client; Iterates request to Google and returns the string response; Gets Disconnected when Mic Stream terminates.
        :param request_iterator: Audio bytes from Client
        """
        print("Got Connected with : ", socket.gethostbyname(socket.gethostname()))

        spxClient = speech.SpeechClient()

        language_code = 'en-US'
        sample_rate_hertz = 16000

        audioRecogConfig = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=sample_rate_hertz,
            language_code=language_code)

        audioStreamingConfig = types.StreamingRecognitionConfig(config=audioRecogConfig, interim_results=True)

        requests = self.makeGoogleStreamingRecognizeRequest(request_iterator)

        responses = spxClient.streaming_recognize(audioStreamingConfig, requests)

        for response in responses:
            transcript, isEnd = self.makeGoogleResponsesToTranscript(response)
            if isEnd == 1:
                break
            yield self.makeStreamingRecognizeResponse(transcript)

        print("Got Disconnected with : ", socket.gethostbyname(socket.gethostname()))


    def StreamingRecognize_working_old(self, request_iterator, context):
        """*
        Client can call this method multiple times to specify audio chunks.
        OPUS encoding and 100ms chunk is expected.
        """

        print("Got Connected with : ", socket.gethostbyname(socket.gethostname()))
        print("Type of request_iterator : ", type(request_iterator))
        for request in request_iterator:
            print("Type of request : ", type(request))
            string = 'asdfghijklmnop' + " 12"
            recog_result = self.makeStreamingRecognizeResponse(string)
            yield recog_result

        print("Got Disconnected with : ", socket.gethostbyname(socket.gethostname()))


if __name__ == '__main__':
    logging.basicConfig()


