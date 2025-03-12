import streamlit as st 
import os
from mainapp import main
from dotenv import load_dotenv
load_dotenv()
#os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
#openai_api_key = os.environ["OPENAI_API_KEY"]
st.title("Webzine for SCL Health")
#st.write(openai_api_key)

openai_api_key = st.sidebar.text_input("Enter Your OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    st.sidebar.write("반갑습니다, Welcome to SCL-HEALTH_WEBZINE")
    from mainapp import main
    
    main()


