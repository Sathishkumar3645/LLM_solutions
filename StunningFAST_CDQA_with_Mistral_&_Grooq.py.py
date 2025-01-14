import os
import sys
import streamlit as st
from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
import time
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
load_dotenv()  #

groq_api_key = "grroq_api_key"
import getpass

# inference_api_key = getpass.getpass("Enter your HF Inference API Key:\n\n")
inference_api_key = "huggingface_key"

if "vector" not in st.session_state:
    print("in vector")
    # st.session_state.embeddings = OllamaEmbeddings()
    
    st.session_state.embeddings = embeddings = HuggingFaceInferenceAPIEmbeddings(
                                                    api_key=inference_api_key, model_name="sentence-transformers/all-MiniLM-l6-v2"
                                                    )
    print("embedding done")
    st.session_state.loader = PyPDFLoader(r"C:\Users\Sathishkumar.paranth\Desktop\ESG\[Baxter]ESG Report_[2021]_[GRI].pdf")
    st.session_state.docs = st.session_state.loader.load()
    print("loaded")
    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    st.session_state.documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
    st.session_state.vector = FAISS.from_documents(st.session_state.documents, st.session_state.embeddings)
    print("done")
st.title("CDQA - Groq Edition :) ")

llm = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name='mixtral-8x7b-32768'
    )

prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context. 
Think step by step before providing a detailed answer. 
I will tip you $200 if the user finds the answer helpful. 
<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)

retriever = st.session_state.vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

prompt = st.text_input("Input your prompt here")


# If the user hits enter
if prompt:
    # Then pass the prompt to the LLM
    start = time.process_time()
    response = retrieval_chain.invoke({"input": prompt})
    print(f"Response time: {time.process_time() - start}")

    st.write(response["answer"])

    # With a streamlit expander
    with st.expander("Document Similarity Search"):
        # Find the relevant chunks
        for i, doc in enumerate(response["context"]):
            # print(doc)
            # st.write(f"Source Document # {i+1} : {doc.metadata['source'].split('/')[-1]}")
            st.write(doc.page_content)
            st.write("--------------------------------")
