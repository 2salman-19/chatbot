# --- streamlit_app.py  Simple app ---
# Lets import the necessary libraries
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from scripts.ingest_to_chromadb import ingest_to_chromadb
from scripts.query_llm import query_llm

st.set_page_config(page_title="Jazz Package Chatbot", layout="centered")
st.title("Jazz Package Chatbot")

st.sidebar.title("Options")
option = st.sidebar.selectbox(
    "Select an action",
    ["Chatbot", "Ingest Packages"]
)

if option == "Ingest Packages":
    st.write("## Ingest or Update Jazz Packages")
    if st.button("Run Ingestion"):
        try:
            ingest_to_chromadb()
            st.success("Package data ingested and embeddings updated successfully!")
        except Exception as e:
            st.error(f"Error during ingestion: {e}")
    st.info("This will (re)generate embeddings and update the ChromaDB vector store.")

elif option == "Chatbot":
    st.write("## Jazz Packages Chatbot")
    st.info("Ask about weekly, daily, or monthly packages, prices, activation codes, etc. Type your question below.")

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for entry in st.session_state.chat_history:
        if entry['role'] == 'user':
            st.markdown(f"**You:** {entry['content']}")
        else:
            st.markdown(f"**JazzBot:** {entry['content']}")

    # Chat input
    user_input = st.text_input("Your message:", key="user_input")
    send = st.button("Send")

    if send and user_input.strip():
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        with st.spinner("JazzBot is typing..."):
            try:
                response = query_llm(user_input)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            except Exception as e:
                error_msg = f"Error during LLM query: {e}"
                st.session_state.chat_history.append({'role': 'assistant', 'content': error_msg})
        st.experimental_rerun()

    # Option to clear chat
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Developed by [Salman Siddique](https://github.com/2salman-19)")
st.sidebar.markdown("""
This app allows you to interact with Jazz's mobile packages using a chatbot interface.\
You can ingest package data into ChromaDB and query the LLM for information about Jazz packages.
""")

