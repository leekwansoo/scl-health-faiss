# modules/qa_module.py
import openai
from openai import OpenAI
from modules.chromadb import search_documents
from langchain_ollama import ChatOllama
from langchain_openai import OpenAIEmbeddings
from modules.faissdb import search_documents
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client=OpenAI()
ollama_client = ChatOllama(model="llama3.2", temperature=0.1)

def answer_question(question, context):
    chat_completion = client.chat.completions.create( messages=[ {"role": "user", "content": question} ], model="gpt-4o-mini", ) 
    return chat_completion.choices[0].message['content'].strip()

def query_faiss_db(query):     
    results = similarity_search(query, k=1) 
    context = ""
    for res in results:
        context += res.page_content     
    prompt = f"Given the context: {context}\n\nQ: {query}\nA:" 
    #print(context)
    # Generate response using OpenAI 
    chat_completion = client.chat.completions.create( messages=[ {"role": "user", "content": prompt} ], model="gpt-4o-mini", ) 
    
    return chat_completion.choices[0].message


### from webzine version ###
client=OpenAI()

embed = OpenAIEmbeddings()

def answer_question(question, context):
    chat_completion = client.chat.completions.create( messages=[ {"role": "user", "content": question} ], model="gpt-4o-mini", ) 
    return chat_completion.choices[0].message['content'].strip()

def query_chroma_db(query):     
    results = search_documents(query, k=1) 
    context = ""
    for res in results:
        context += res.page_content     
    prompt = f"Given the context: {context}\n\nQ: {query}\nA:" 
    #print(context)
    # Generate response using OpenAI 
    chat_completion = client.chat.completions.create( messages=[ {"role": "user", "content": prompt} ], model="gpt-4o-mini", ) 
    
    return chat_completion.choices[0].message

def query_faiss_db(query):     
    results = search_documents(query, k=1) 
    context = ""
    for res in results:
        context += res.page_content     
    prompt = f"Given the context: {context}\n\nQ: {query}\nA:" 
    #print(context)
    # Generate response using OpenAI 
    chat_completion = client.chat.completions.create( messages=[ {"role": "user", "content": prompt} ], model="gpt-4o-mini", ) 
    
    return chat_completion.choices[0].message