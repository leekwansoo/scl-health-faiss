import streamlit as st 
import io
import os
import json 
from langchain_community.document_loaders import TextLoader
from modules.pdf_reader import generate_question, parse_pdf, create_query_file, load_pdf, add_qa_file, check_query_exist
from modules.faissdb import store_pdf_documents
from modules.query_handler import query_faiss_db
from doc_handler import check_file_exist
from graph import search_web
from dotenv import load_dotenv
load_dotenv()

st.title("Webzine for SCL Health")

openai_api_key = st.sidebar.text_input("Enter Your OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    st.sidebar.write("반갑습니다, Welcome to SCL-HEALTH_WEBZINE")

st.session_state["DOCUMENT"] = []

st.session_state["DOCUMENT"] = os.listdir("uploaded")

doc_list =[st.session_state["DOCUMENT"]]
    
# Function to add data to DOCUMENT directory 
def check_document(value): 
    if value not in st.session_state["DOCUMENT"]:
        result = "noexist"
        return(result)
    else:
        result = "exist"
        return(result)
       
def add_document(value):         
    st.session_state["DOCUMENT"].append(value)
    st.write(f"Document added: {value}") 

# Example usage # List Document
def list_documents(): 
    if st.session_state["DOCUMENT"]:
        docs = st.session_state["DOCUMENT"]
        return(docs)
    else: st.write("No documents found in 'DOCUMENT'.")

# Main Page content 


def handle_query(file_name, query):
    response =check_query_exist(file_name, query)
    if response:
        st.write(response["answer"])
        st.write("Get Answer from Home Brewed QA store")
    else:
        response = query_faiss_db(query)
        if response:
            qa_pair = {"query": query, "answer": response.content}
            qa_file = add_qa_file(file_name, qa_pair)
            st.write(response.content)
            st.write(f"QA pair is saved in {qa_file}")
                            
st.session_state["query_message"] = []
st.session_state["query_file"] = []

# Create a sidebar for navigation
st.sidebar.title("Menu")
options = st.sidebar.radio("Select an option", ["Upload File", "Query from Uploaded File", "Web Search"])

if options == "Upload File":
    st.sidebar.header("Upload File")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf", key="pdf_uploader")
       
    if uploaded_file:
        file_name = uploaded_file.name
        dir_name = "uploaded"
        check_exist = check_file_exist(dir_name, file_name)
        if check_exist == False:
            # store the file in the uploaded file folder
            uploaded_name = f"uploaded/{file_name}"
            with open(uploaded_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            text = parse_pdf(uploaded_file)
            documents = load_pdf(uploaded_name)
            #result = load_pdf_documents(documents)  # load documents to chromadb
            result = store_pdf_documents(documents)  # load documents to faissdb
            if result:
                st.sidebar.write(result)
                add_document(file_name)     
            else: st.sidebar.write("storing PDF file into vector store failed")
            questions= generate_question(text)
            query_file = create_query_file(file_name, questions.content)
            st.session_state["query_file"].append(query_file)
            for question in questions.content:
                st.session_state["query_message"].append(question)
            st.sidebar.markdown(questions.content)
                      
            docs = list_documents()
            if docs:
                for doc in docs:
                    st.sidebar.write(f"Uploaded_Document: {doc}\n")  
        else:
            st.sidebar.write(f"{file_name} is aleardy uploaded\n")     
         
    else:
        st.sidebar.write("Please upload a PDF and select subject to get started.")
        
            
elif options == "Query from Uploaded File":
    st.header("Query from Uploaded File")
    query_file_list = os.listdir("query")
    selected = st.sidebar.selectbox("Select month to query", query_file_list)
    file_name = f"query/{selected}"
    # make query as list in the query_file
    loader =TextLoader(file_name, encoding = "utf-8")
    documents = loader.load()
    query_list = documents[0].page_content.split("\n")
    query_input = st.text_input("Enter your question for your uploaded documents")
    if query_input:
        handle_query(file_name, query_input)
        
    i = 0
    for query in query_list:
        i += 1           
        st.sidebar.write(query)  # Display the query
        if "?" in query:
            button = st.sidebar.button(f"Query", key=f"button_{i}")
            if button:# Add a button with a unique key
                handle_query(file_name, query)
         
          
elif options == "Web Search":
    st.header("Web Search")
    query = st.text_input("Enter a search query:")
    if st.button("Search Web"):
        if query:
            results = search_web(query)
            for result in results:
                st.write(result["content"])
        else:
            st.write("Please enter a search query.")
