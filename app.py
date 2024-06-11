from flask import Flask, request, jsonify, render_template
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

app = Flask(__name__)

# IBM Watson TTS setup
api_key = 'your_api_key_here'
url_tts = 'your_service_url_here'
authenticator = IAMAuthenticator(api_key)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url_tts)

@app.route('/')
def home():
    # Render an HTML file with your virtual assistant and form
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize_text():
    data = request.json
    text = data['text']
    response = tts.synthesize(text, accept='audio/mp3', voice='en-US_AllisonV3Voice').get_result()
    return response.content, 200, {'Content-Type': 'audio/mp3'}

if __name__ == '__main__':
    app.run(debug=True)
