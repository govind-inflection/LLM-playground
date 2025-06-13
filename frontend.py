import streamlit as st
from LLM_funct import create_model,generate_answer
from funct import change_model,reset_values,clear_chat


st.set_page_config(page_title="LLM Playground", layout='wide',page_icon='🦜🔗')

####################### Create a session variables #######################
with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
if "api" not in st.session_state :
    st.session_state["openaikey"] = "" 
if "chatbotcontext" not in st.session_state :
    st.session_state["chatbotcontext"] = "you are a helpful assistant answering users' questions clearly"
if "llm_task" not in st.session_state :
    st.session_state["llm_task"]= "Text Generation"
if "llm_name" not in st.session_state :
    st.session_state["llm_name"] = 1
if "llm_temp" not in st.session_state :
    st.session_state["llm_temp"]=0.1
if "llm_maxlen" not in st.session_state :
    st.session_state["llm_maxlen"]=100
if "models_per_task" not in st.session_state :
    st.session_state.models_per_task={"Text Generation":["GPT-3.5 Turbo", "meta/llama-2-70b-chat","meta/llama-2-13b-chat","meta/llama-2-7b-chat","tiiuae/falcon-7b-instruct","google/flan-ul2"]}
if "curnt_llm" not in st.session_state :
    st.session_state.curnt_llm = create_model(list(st.session_state.models_per_task["Text Generation"])[1], st.session_state.llm_temp, st.session_state.llm_maxlen,st.session_state.openaikey)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

  
####################################[   FRONTEND - MAIN SCREEN ]#####################################################    

st.title("🦜🔗 LLM Playground ")
st.text("Compare different LLM models & tune its parameters.")
st.markdown("""---""")

###########[   SIDEBAR    ]###################    
with st.sidebar:
    #API key
    st.header(" 🥽  🥼 Parameter Settings")
    st.success('Llama & Falcom API Key is provided', icon="✅")
    
    # Task
    st.session_state["llm_task"]=st.selectbox("LLM Model Task", options=tuple(st.session_state.models_per_task.keys()), index= list(st.session_state.models_per_task.keys()).index(st.session_state["llm_task"]))
    #model name
    llm_name= st.selectbox("Model Name", options=tuple(st.session_state.models_per_task[st.session_state["llm_task"]]),index= st.session_state.llm_name, help="Select the LLM model name")
    st.session_state.llm_name=list(st.session_state.models_per_task[st.session_state["llm_task"]]).index(llm_name)
            
    st.session_state["openaikey"] =st.text_input("GPT API Key", type="password", help= "Type in your GPT API token i.e. xxxxx \n\n for interacting with the GPT LLM model")

    #temperature
    st.session_state.llm_temp=st.slider("Temperature",min_value=0.1, max_value=1.0, value=st.session_state["llm_temp"], help="Set the randomness of the LLM model")

    #max length
    st.session_state.llm_maxlen=st.slider("Max Token Length",min_value=1, max_value=1000, value=st.session_state["llm_maxlen"], help="Limit/extend the length of the LLM model's results")

    #reset parameters
    col1, col2=st.columns(2)
    with col1:
        st.button("🤓 Load Parameters",type="primary", on_click=change_model,use_container_width=True)
    with col2:
        st.button("✖️ Reset Parameters",type="primary", on_click=reset_values,use_container_width=True)

    st.button("Clear Chat",type="primary", on_click=clear_chat,use_container_width=True)

###########[   Chat SCREEN    ]###################    

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt:=st.chat_input("write your message here"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role":"user", "content":prompt})

    #store the convo
    convo= f"user:{prompt} \n\n"
    for msg in st.session_state.chat_history:
        if msg['role'] =="user":
            convo=convo+f" {msg['content']} \n\n"
        else:
            convo=convo+f" {msg['content']} \n\n"
    with st.spinner('Generate '+llm_name+ " Response"):
        response=generate_answer(st.session_state.curnt_llm, convo, list(st.session_state.models_per_task["Text Generation"])[st.session_state.llm_name])
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.chat_history.append({"role":"assistant", "content":response})



