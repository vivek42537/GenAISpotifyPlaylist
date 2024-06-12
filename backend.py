import os
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS

# RAG = Retrieval Augmented Generation
path = "./datafiles/SpotifyData.csv"
# path = os.listdir()
# print("PATH:   ", path)
# Initialize bedrock runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2",
)


# Get data from a file
def fileLoader(path):
    loader = CSVLoader(path)
    docu = loader.load()

    textSplit = RecursiveCharacterTextSplitter(chunk_size = 10000, chunk_overlap = 100)
    words = textSplit.split_documents(docu)
    return words
    # text = ""
    # for doc in docs:
    #     text += doc.page_content
    
    # print(text)

# Embed text data using Amazon Bedrock
# def embed_text_data(text_data):
#     embeddings_service = BedrockEmbeddings(model_id="amazon.titan-text-lite-v1")
#     # embeddings_service = EmbeddingsService(region_name='us-west-2')
#     embeddings = embeddings_service.embed(text_data)
#     return embeddings

def get_vector():
    # Initialize BedrockEmbeddings with the desired model ID
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_runtime)

    # Check if a local vector store exists
    if os.path.exists('./my_vectorstore'):
        # If it exists, load it using FAISS
        vectorstore_faiss = FAISS.load_local("my_vectorstore", embeddings, allow_dangerous_deserialization=True)
    else:
        docs = fileLoader(path)
        vectorstore_faiss = FAISS.from_documents(docs, embeddings)

        # Save the created vector store locally
        vectorstore_faiss.save_local("my_vectorstore")

    # Return the created or loaded vector store
    return vectorstore_faiss

# Function to create and return the LLM instance
# def initialize_llm():
#     model_kwargs = { 
#         "temperature": 0.5,  
#         "topP": 0.5,          # diversity of responses default is low - 0
#         "maxTokenCount": 512  # maximum token count
#     }
#     return Bedrock(client=bedrock_runtime, model_id="amazon.titan-text-lite-v1", model_kwargs=model_kwargs)

def initialize_llm():
    model_kwargs = { 
        "max_tokens_to_sample": 1000,
        "stop_sequences": [],
        "temperature": 1, # use 1 for more creative responses, pick closer to 0 for more numeric analytic work (randomness of response)
        "top_p": 1, # diversity of responses default is low - 0
    }
    return Bedrock(client=bedrock_runtime, model_id="anthropic.claude-v2", model_kwargs=model_kwargs)

# Initialize the LLM instance
llm_instance = initialize_llm()

# Function to create and return memory
def create_memory(llm):
    return ConversationBufferMemory(llm=llm, max_token_limit=512)

# Function to create and return conversation chain
def create_conversation_chain(llm, memory):
    return ConversationChain(llm=llm, memory=memory, verbose=True)

# Initialize memory
memory_instance = create_memory(llm_instance)


# Function to handle conversation
def convo(inputText, memory):
    locVector = get_vector()
    docs = locVector.similarity_search(inputText)

    context = ""
    for doc in docs:
        context += doc.page_content
    
    prompt = f"""Human: Only use the information here to answer the question at the end. 
    This is my Liked Songs on Spotify {context} . 
    I want to generate a playlist of recommended songs based on what question I ask. 
    Question: {inputText} \n Answer: """
    
    # Create conversation chain
    llm_chain_data = initialize_llm()
    llm_convo = create_conversation_chain(llm_chain_data, memory)
    # Get reply
    reply = llm_convo.predict(input=prompt)
    return reply
    # return call_LLM(prompt)


# Demo function for chatbot interaction
def demo_chatbot(input_text):
    response = convo(input_text, memory_instance)
    return response

