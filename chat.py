import streamlit as st
from elasticsearch import Elasticsearch
from common import *
from chat_history import *
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ELSER_INDEX = "teamsyncfirstn"
MODEL_ID = "ibm/granite-3-8b-instruct"
model = get_model(MODEL_ID, "greedy", 1, 500)

client = Elasticsearch([{"host": "169.48.177.59", "port": 9200, "scheme": "http"}])


def search_elasticsearch(query, file_name):
    file_id_mapping = {
        "AirForce_document": "67c2ba704349f521c364a481",
        "Supplement_document_2010": "67c2baeb4349f521c364a482",
        "DPPM_Manual_2009":"67c2baeb4349f521c364a483",
        "DPPM_MANUAL_PPT":"67c2bb8a4349f521c364a484"
    }
    file_id = file_id_mapping.get(file_name, None)
    search_body = {
        "size": 1,
        "query": {
                    "bool": {
                        "must": [
                            {"match": {"username": "arpita_appolo.com"}},# Filter by username
                            {"match": {"fId": file_id}}, 
                            {
                                "bool": {
                                    "should": [
                                        {
                                            "sparse_vector": {
                                                "field": "text_embedding",
                                                "inference_id": ".elser_model_2_linux-x86_64_search",
                                                "query": query
                                            }
                                        },
                                        {
                                            "match": {
                                                "text": query  # Match exact phrase in the text field
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                },
                "_source": [
                    "text", "pageNo", "fId", "username", "tables", "fileName"
                ]  
    }
    response = client.search(index=ELSER_INDEX, body=search_body)
    hits = response['hits']['hits']
    return "\n\n".join(hit['_source']['text'] for hit in hits) if hits else "No relevant content found."


def load_prompt(content, user_input):
    try:
        with open('rag_prompt.txt', 'r') as file:
            prompt = file.read().strip()
            prompt = prompt.replace("{{question}}", user_input)
            prompt = prompt.replace("{{document}}", content)
            prompt = prompt.replace("{{chat_history}}", get_chat_history_prompt())
        return prompt
    except FileNotFoundError:
        st.error("The 'rag_prompt.txt' file was not found. Please ensure it exists in the app directory.")
        return None


def main_page():
    st.title("💬 Indian AirForce Chatbot")
    st.markdown("\n**Interact with files using AI-powered search and conversation.**")
    
    file_options = ["AirForce_document", "Supplement_document_2010","DPPM_Manual_2009","DPPM_MANUAL_PPT"]
    selected_file = st.sidebar.selectbox("📂 Select a File", file_options, index=0)
    
    if "file_selected" not in st.session_state or st.session_state["file_selected"] != selected_file:
        st.session_state["file_selected"] = selected_file
        reset_memory()
        st.session_state["messages"] = []
        st.rerun()
    
    st.sidebar.markdown(f"**Selected File:** `{st.session_state['file_selected']}`")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if user_input := st.chat_input("Type your question here..."):
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.spinner("Fetching relevant content..."):
            content = search_elasticsearch(user_input, file_name=st.session_state['file_selected'])
            print("content",content)
            prompt = load_prompt(content, user_input)
        
        if prompt:
            with st.spinner("Generating response..."):
                response_stream = generate_text_stream(model, prompt)
                with st.chat_message("assistant"):
                    answer = st.write_stream(response_stream).strip()
                st.session_state["messages"].append({"role": "assistant", "content": answer})
                update_memory(user_input, answer, content)
        else:
            st.error("Failed to generate prompt.")


if __name__ == "__main__":
    main_page()
