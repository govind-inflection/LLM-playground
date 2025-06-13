import streamlit as st
from api_llm import create_model


def change_model():
    clear_chat()
    selected_model = st.session_state["selected_model"]
    llm_temp = st.session_state["llm_temp"]
    llm_maxlen = st.session_state["llm_maxlen"]
    
    if not selected_model or selected_model not in st.session_state.saved_models:
        st.error("Please select a valid model")
        return
        
    model_config = st.session_state.saved_models[selected_model]
    
    with st.toast(f'Loading model: {selected_model}\n\n- Temperature = {llm_temp}\n\n- Max token = {llm_maxlen}', icon="🔥"):
        st.session_state.curnt_llm = create_model(
            selected_model,
            model_config["api_url"],
            model_config["api_key"],
            llm_temp,
            llm_maxlen
        )
        
    st.toast('Model Ready', icon="🚨")

    

def reset_values():
    st.session_state["llm_temp"] = 0.5
    st.session_state["llm_maxlen"] = 50
    st.session_state.curnt_llm = None

def clear_chat():
    st.session_state.chat_history = []