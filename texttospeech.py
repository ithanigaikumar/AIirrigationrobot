from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

url = 'https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/ff1632e5-41e3-4736-9b2c-267fd9bce21f'
apikey = 'ksGCq8JMSF_fPrDdo3cLzu2xLvhC84bEFOuaecMA-2i_'


authenticator = IAMAuthenticator(apikey)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url)

with open('./speech.mp3', 'wb') as audio_file:
    res = tts.synthesize('Riya your socks are smelly, they stink of cheese!', accept='audio/mp3',
                         voice='en-US_AllisonV3Voice').get_result()
    audio_file.write(res.content)
