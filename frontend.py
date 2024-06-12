import streamlit as st
import backend

st.title('Vivek ChatBot')

# Initialization
if 'memory' not in st.session_state:
    st.session_state.memory = backend.create_memory(backend.llm_instance)

# Session State also supports attribute based syntax
if 'conversation' not in st.session_state:
    st.session_state.conversation = [] #start chat history

print("UNO")

if 'my_vectorstore' not in st.session_state: #see if the vector index hasn't been created yet
    with st.spinner("Gears turning..."): #show a spinner while the code in this with block runs
        st.session_state.bills_vectorstore = backend.get_vector() #retrieve the index through the supporting library and store in the app's session cache

print("DOS")
# Display chat messages
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

print("TRES")
inputText = st.chat_input("Chat with bot here:")

if inputText is not None:
    with st.chat_message("user"):
        st.markdown(inputText)

    st.session_state.conversation.append({"role": "user", "content": inputText})

    chatResponse = backend.convo(inputText=inputText, memory=st.session_state.memory)

    with st.chat_message("helper"):
        st.markdown(chatResponse)
    
    st.session_state.conversation.append({"role": "assistant", "content": chatResponse})


