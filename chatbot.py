from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import asyncio
from unify import AsyncUnify


url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/d6d2737e-ab10-4938-8138-2ca6fdc53c13'
apikey = 'l9Dk_4NIA6r5bnFVdW3imz3I1qcXEegbXCnWVXRFKECF'


def handle_chat(url, apikey, user_input):
    # Create and set up the Watson Assistant client
    authenticator = IAMAuthenticator(apikey)
    assistant = AssistantV2(
        version='2021-11-27',
        authenticator=authenticator
    )
    assistant.set_service_url(url)

    # Create a session
    session_response = assistant.create_session(
        # Replace with your actual assistant ID
        assistant_id='d2b86adf-a2dd-4f2b-af00-fb39dca03538'
    ).get_result()
    session_id = session_response['session_id']

    # Send message and get response
    response = assistant.message(
        assistant_id='your_assistant_id',  # Replace with your actual assistant ID
        session_id=session_id,
        input={'text': user_input}
    ).get_result()

    # Process the response to extract the text
    message_output = response['output']['generic'][0]['text']
    return message_output


def main():
    st.title("🤖💬 AI Irrigation Chatbot")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display existing chat messages
    messages_container = st.container()
    for msg_type, msg_content in st.session_state.chat_history:
        if msg_type == "user":
            messages_container.chat_message("user").write(msg_content)
        elif msg_type == "assistant":
            messages_container.chat_message("assistant").write(msg_content)

    # Chat input at the bottom of the page
    user_input = st.chat_input("Say something", key="chat_input")

    if user_input:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                handle_chat, url, apikey, user_input)
            response = future.result()
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()

    else:
        st.error("Please enter valid keys to start chatting.")


if __name__ == "__main__":
    main()
