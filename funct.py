import streamlit as st
from LLM_funct import create_model


def change_model():
    clear_chat()
    llm_task = st.session_state["llm_task"]
    llm_name = list(st.session_state.models_per_task[llm_task])[st.session_state.llm_name]
    llm_temp = st.session_state["llm_temp"]
    llm_maxlen = st.session_state["llm_maxlen"]
    llm_key= st.session_state.openaikey
    with st.toast('Loading :\n\n'+llm_name +' \n\n- Temperature = '+str(llm_temp)+'\n\n- Max token = '+str(llm_maxlen), icon="🔥"):
        st.session_state.curnt_llm=create_model(llm_name, llm_temp, llm_maxlen,llm_key)
        
    st.toast('Model Ready', icon="🚨")

    

def reset_values():
    st.session_state["llm_task"]="Text Generation"
    st.session_state["llm_name"] =0
    st.session_state["llm_temp"]=0.5
    st.session_state["llm_maxlen"]=50

def clear_chat():
    st.session_state.chat_history = []