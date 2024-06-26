from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

url_tts = 'https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/ff1632e5-41e3-4736-9b2c-267fd9bce21f'
apikey_tts = 'ksGCq8JMSF_fPrDdo3cLzu2xLvhC84bEFOuaecMA-2i_'


authenticator = IAMAuthenticator(apikey_tts)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url_tts)

with open('./speech.mp3', 'wb') as audio_file:
    res = tts.synthesize("Your plant is too humid and above the optimal humidity level", accept='audio/mp3',
                         voice='en-US_AllisonV3Voice').get_result()
    audio_file.write(res.content)
