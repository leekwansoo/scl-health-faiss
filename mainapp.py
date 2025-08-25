import streamlit as st 
import io
import os
import json 
from langchain_community.document_loaders import TextLoader
from modules.pdf_reader import generate_question, generate_question_with_genai, parse_pdf, create_query_file, load_pdf, add_qa_file, check_qafile_exist
from modules.faissdb import store_pdf_documents
from modules.query_handler import query_faiss_db
from doc_handler import check_file_exist
from graph import search_web
from dotenv import load_dotenv
load_dotenv()

st.session_state["DOCUMENT"] = []

st.session_state["DOCUMENT"] = os.listdir("uploaded")

doc_list =[st.session_state["DOCUMENT"]]

st.session_state["query_input"] = [""]
    
# Function to add data to DOCUMENT directory 
def check_document(value): 
    if value not in st.session_state["DOCUMENT"]:
        result = "noexist"
        return(result)
    else:
        result = "exist"
        return(result)
       
def add_document(value):   
    if "DOCUMENT" not in st.session_state: 
        st.session_state["DOCUMENT"] = []     
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
    response = check_qafile_exist(file_name, query)
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
            
def main():
                            
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
                result = store_pdf_documents(documents)  # load documents to faiss_db
                if result:
                    st.sidebar.write(result)
                    add_document(file_name)     
                else: st.sidebar.write("storing PDF file into vector store failed")
                questions= generate_question_with_genai(text)
                print(questions)
                query_file = create_query_file(file_name, questions)
                # questions= generate_question(text)
                # query_file = create_query_file(file_name, questions.content)
                st.session_state["query_file"].append(query_file)
                for question in questions:
                    st.session_state["query_message"].append(question)
                st.sidebar.markdown(questions)
                        
                docs = list_documents()
                if docs:
                    for doc in docs:
                        st.sidebar.write(f"Uploaded_Document: {doc}\n")  
            else:
                st.sidebar.write(f"{file_name} is already uploaded\n")     

        else:
            st.sidebar.write("Please upload a PDF and select subject to get started.")
            
                
    elif options == "Query from Uploaded File":
        st.header("Query from Uploaded File")
        query_file_list = os.listdir("query")
        selected = st.sidebar.selectbox("Select document to query", query_file_list)
        file_name = f"query/{selected}"
        # make query as list in the query_file
        loader =TextLoader(file_name, encoding = "utf-8")
        documents = loader.load()
        query_list = documents[0].page_content.split("\n")
        query_input = st.text_input("Enter your question for your uploaded documents:", 
                                    key = "query_key_0",
                                    value = st.session_state["query_input"][0])
        if query_input:
            if st.button("Get Answer"):
                handle_query(file_name, query_input)

        #st.session_state["query_input"] = [""]
        i = 0
        for query in query_list:
            i += 1
            query = query.strip().rstrip(',')
            if query.startswith('{') and query.endswith('}'):
                query_dict = json.loads(query)
                st.sidebar.write(query_dict["question"])
                button = st.sidebar.button(f"Query", key=f"button_{i}")
                if button:
                    st.session_state["query_input"][0] = query_dict["question"]
                    st.rerun()

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
