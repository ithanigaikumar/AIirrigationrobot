
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1
from random import random
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import asyncio
from unify import AsyncUnify


url_tts = 'https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/ff1632e5-41e3-4736-9b2c-267fd9bce21f'
apikey_tts = 'ksGCq8JMSF_fPrDdo3cLzu2xLvhC84bEFOuaecMA-2i_'


authenticator = IAMAuthenticator(apikey_tts)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url_tts)

sunlight_level = random()
moisture_level = random()


with open('./moisture_speech.mp3', 'wb') as audio_file:
    res = tts.synthesize('Your plant has dropped below moisture levels and is too dry, please water it!', accept='audio/mp3',
                         voice='en-US_AllisonV3Voice').get_result()
    audio_file.write(res.content)


with open('./sunlight_speech.mp3', 'wb') as audio_file:
    res = tts.synthesize('Your plant has not absorbed enough sunlight for today please move it into the sunlight!', accept='audio/mp3',
                         voice='en-US_AllisonV3Voice').get_result()
    audio_file.write(res.content)

audiomoisture_filepath = 'moisture_speech.mp3'
audiosunlight_filepath = "sunlight_speech.mp3"


# Function to get bot response using AsyncUnify


async def get_bot_response(api_key, endpoint, user_input):
    endpoint = endpoint+"@anyscale"
    unify = AsyncUnify(api_key=api_key, endpoint=endpoint)
    response = await unify.generate(user_prompt=user_input)

    # Handle the response based on its type
    if isinstance(response, str):
        return response
    else:
        # If the response is a stream, gather chunks
        result = []
        async for chunk in response:
            result.append(chunk)
        return ''.join(result)

# Function to handle the asyncio loop and execute async calls


# Function to handle the asyncio loop and execute async calls
# Function to handle the asyncio loop and execute async calls
def run_async(api_key, endpoint, user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_bot_response(api_key, endpoint, user_input))
    finally:
        loop.close()

# Function to handle user input and get the response


def handle_user_input(user_input, api_key, endpoint):
    return run_async(api_key, endpoint, user_input)


def main():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">', unsafe_allow_html=True)

    st.sidebar.title("Configuration")
    unify_key = st.sidebar.text_input("Enter your UNIFY_KEY", type='password')
    audio_played = False

    if unify_key:
        st.session_state.unify_key = unify_key

    if 'unify_key' in st.session_state:
        model_list = [
            "mixtral-8x7b-instruct-v0.1", "llama-2-70b-chat", "llama-2-13b-chat",
            "mistral-7b-instruct-v0.2", "llama-2-7b-chat", "codellama-34b-instruct",
            "gemma-7b-it", "mistral-7b-instruct-v0.1", "mixtral-8x22b-instruct-v0.1",
            "codellama-13b-instruct", "codellama-7b-instruct", "yi-34b-chat",
            "llama-3-8b-chat", "llama-3-70b-chat", "pplx-7b-chat", "mistral-medium",
            "gpt-4", "pplx-70b-chat", "gpt-3.5-turbo", "deepseek-coder-33b-instruct",
            "gemma-2b-it", "gpt-4-turbo", "mistral-small", "mistral-large",
            "claude-3-haiku", "claude-3-opus", "claude-3-sonnet"
        ]
        selected_model = st.sidebar.selectbox("Choose a model", model_list)

        if sunlight_level < 0.5:
            print(sunlight_level)
            st.sidebar.markdown(
                "### Play the audio to hear updates about your plants")
            with open(audiosunlight_filepath, 'rb') as audio_file:
                audio_bytes_sun = audio_file.read()
                st.sidebar.audio(audio_bytes_sun, format='audio/mp3')
                audio_played = True

        if moisture_level < 0.5:
            print(moisture_level)
            st.sidebar.markdown(
                "### Play the audio to hear updates about your plants")
            with open(audiomoisture_filepath, 'rb') as audio_file:
                audio_bytes_moisture = audio_file.read()
                st.sidebar.audio(audio_bytes_moisture, format='audio/mp3')
                audio_played = True

        if audio_played:

            st.title("🌱🤖 AI Irrigation Chatbot 🌻🌿")

            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            # Display existing chat messages
            messages_container = st.container()
            for msg_type, msg_content in st.session_state.chat_history:
                if msg_type == "user":
                    messages_container.chat_message("user").write(msg_content)
                elif msg_type == "assistant":
                    messages_container.chat_message(
                        "assistant").write(msg_content)

            # Chat input at the bottom of the page
            user_input = st.chat_input(
                "Ask for any updates on PH/Sunlight/Moisture/Temperature/Happiness of your plant", key="chat_input")

            # Display the audio player widget

            if user_input:

                with ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        handle_user_input, user_input, st.session_state.unify_key, selected_model)
                    response = future.result()
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(
                        ("assistant", response))
                    st.rerun()

            else:
                st.error("Please enter valid keys to start chatting.")


if __name__ == "__main__":
    main()
