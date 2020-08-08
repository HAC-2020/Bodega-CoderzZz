"""
Import required library functions, modules, APIs.
"""
from __future__ import print_function, division
from speech.proto_speech import audio2text_pb2, audio2text_pb2_grpc, orderinfo2user_pb2, orderinfo2user_pb2_grpc
import socket
from google.cloud import speech
from google.cloud.speech import enums, types
import os, json
from pathlib import Path
import logging
import argparse
from .test.predict import predict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path.home()) + "/github/gRPC/Speech2Txt/grpc-server/config/gapi_credentials/credentials.json"

findIntentSlot = []
prediction = {}

def sendAcknowledgement(sendOrder):
    restaurant_name = sendOrder[-1]
    print(restaurant_name + " received : " ,sendOrder)
    return restaurant_name + " has Received your Order!"

def GetWeather(prediction):
    return "THIS IS SAMPLE : The Weather in " + prediction['slots']['place_name'] + " is cloudy."    

def Descriptive(prediction):
    return "NO INTENT FOUND"

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
        # print("Making response")
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

        language_code = 'en-IN'
        sample_rate_hertz = 16000

        audioRecogConfig = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate_hertz,
            language_code=language_code)

        audioStreamingConfig = types.StreamingRecognitionConfig(config=audioRecogConfig, interim_results=True)

        requests = self.makeGoogleStreamingRecognizeRequest(request_iterator)

        responses = spxClient.streaming_recognize(audioStreamingConfig, requests)

        for response in responses:
            global findIntentSlot
            transcript, isEnd = self.makeGoogleResponsesToTranscript(response)
            if isEnd == 1:
                break
            findIntentSlot.append(self.makeStreamingRecognizeResponse(transcript))
            yield self.makeStreamingRecognizeResponse(transcript)
        findString = str(findIntentSlot[-1]).split(": ")
        findString = findString[-1].split("\n")
        findIntentSlot = findString[0].split("\"")

        parser = argparse.ArgumentParser()

        parser.add_argument("--input_sent", default=findIntentSlot[1], type=str,
                            help="Input sentence for prediction")
        parser.add_argument("--model_dir", default="./albert_fine_tuned", type=str, help="Path to save, load model")

        parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
        parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

        intentSlotConfig = parser.parse_args()
        global prediction 
        prediction = predict(intentSlotConfig)

class OrderDetails2User(orderinfo2user_pb2_grpc.OrderInfo2UserServicer):
    def SendOrderDetails(self, request, context):
        global prediction
        print("Speech -> Text -> Intent & Slots : ", json.dumps(prediction, sort_keys=False, indent=2))

        if prediction['intent'] == 'OrderFood':
            lenqty = len(prediction['slots']['qty'])
            sendOrder = []
            for i in range(lenqty):
                if i == 0:
                    yield orderinfo2user_pb2.OrderDetails(infoReceived = "*************************************ORDER DETAILS*************************************")
                if prediction['slots']['food_type'][i] == '':
                    sendString = prediction['slots']['qty'][i] + ' ' + prediction['slots']['food_name'][i]
                    sendOrder.append(sendString)
                    yield orderinfo2user_pb2.OrderDetails(infoReceived = sendString)
                else:
                    sendString = prediction['slots']['qty'][i] + ' ' + prediction['slots']['food_type'][i] + ' ' + prediction['slots']['food_name'][i]
                    sendOrder.append(sendString)
                    yield orderinfo2user_pb2.OrderDetails(infoReceived = sendString)
                if i == lenqty-1:
                    sendOrder.append(prediction['slots']['restaurant_name'])
                    yield orderinfo2user_pb2.OrderDetails(infoReceived = sendAcknowledgement(sendOrder))

        elif prediction['intent'] == 'GetWeather':
            yield orderinfo2user_pb2.OrderDetails(infoReceived = GetWeather(prediction))
        
        elif prediction['intent'] == 'Descriptive':
            yield orderinfo2user_pb2.OrderDetails(infoReceived = Descriptive(prediction))

        print("Got Disconnected with : ", socket.gethostbyname(socket.gethostname()))

        


if __name__ == '__main__':
    logging.basicConfig()


