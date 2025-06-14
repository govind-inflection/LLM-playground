import streamlit as st
from api_llm import create_model, generate_answer
from funct import change_model, reset_values, clear_chat
import copy
import json
from datetime import datetime
import os

st.set_page_config(page_title="LLM Playground", layout='wide', page_icon='🦜🔗')
reduce_header_height_style = """
<style>
    div.block-container {padding-top:1rem;}  /* Adjust the '1rem' to your desired padding */
    section[data-testid="stSidebar"] {
        height: 100vh;
        overflow: hidden;
        padding-top: 0;
        margin-top: 0;
    }
    section[data-testid="stSidebar"] > div {
        height: 100%;
        overflow: hidden;
        padding-top: 0;
        margin-top: 0;
    }
    section[data-testid="stSidebar"] > div > div {
        padding-top: 0;
        margin-top: 0;
    }
</style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

####################### Create a session variables #######################
with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state variables
if "saved_models" not in st.session_state:
    st.session_state.saved_models = {}
if "show_add_model" not in st.session_state:
    st.session_state.show_add_model = False
if "selected_models" not in st.session_state:
    st.session_state.selected_models = {"user": None, "assistant": None}
if "max_turns" not in st.session_state:
    st.session_state.max_turns = 5
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "current_turn" not in st.session_state:
    st.session_state.current_turn = 0
if "llm_instances" not in st.session_state:
    st.session_state.llm_instances = {"user": None, "assistant": None}
if "human_system_prompt" not in st.session_state:
    st.session_state.human_system_prompt = ""
if "assistant_system_prompt" not in st.session_state:
    st.session_state.assistant_system_prompt = ""

####################################[   FRONTEND - MAIN SCREEN ]#####################################################    

# Top Bar
col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
with col1:
    st.markdown("<h1 style='margin: 0; padding: 0;'>LLM Playground</h1>", unsafe_allow_html=True)
with col2:
    if st.button("Add Model", use_container_width=True):
        st.session_state.show_add_model = True
with col3:
    if st.button("Save Conversation", use_container_width=True):
        if st.session_state.conversation:
            # Create conversations directory if it doesn't exist
            conversations_dir = "conversations"
            os.makedirs(conversations_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            filepath = os.path.join(conversations_dir, filename)
            
            # Save conversation to file
            with open(filepath, 'w') as f:
                json.dump({
                    "conversation": st.session_state.conversation,
                    "human_system_prompt": st.session_state.human_system_prompt,
                    "assistant_system_prompt": st.session_state.assistant_system_prompt,
                    "models_used": st.session_state.selected_models
                }, f, indent=2)
            st.success(f"Conversation saved to {filepath}")
        else:
            st.warning("No conversation to save")
st.markdown("---")

# Add Model Modal
if st.session_state.show_add_model:
    with st.form("add_model_form"):
        st.subheader("Add New Model")
        model_name = st.text_input("Model Name", help="Enter a name for this model configuration")
        api_url = st.text_input("API URL", help="Enter the API endpoint URL (e.g., https://api.openai.com/v1/chat/completions)")
        api_key = st.text_input("API Key", type="password", help="Enter your API key")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("Add Model", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_add_model = False
                st.rerun()
        
        if submit_button:
            if model_name and api_url and api_key:
                st.session_state.saved_models[model_name] = {
                    "api_url": api_url,
                    "api_key": api_key
                }
                st.session_state.show_add_model = False
                st.success(f"Model '{model_name}' added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all fields")

###########[   SIDEBAR    ]###################    
with st.sidebar:
    st.header("Conversation Settings")
    
    if st.session_state.saved_models:
        # Model Selection
        st.subheader("Select LLMs")
        st.session_state.selected_models["user"] = st.selectbox(
            "Human LLM",
            options=list(st.session_state.saved_models.keys()),
            help="Select the LLM that will act as the human"
        )
        
        st.session_state.selected_models["assistant"] = st.selectbox(
            "Assistant LLM",
            options=list(st.session_state.saved_models.keys()),
            help="Select the LLM that will act as the assistant"
        )
        
        # System Prompts
        st.subheader("System Prompts")
        st.session_state.human_system_prompt = st.text_area(
            "Human LLM System Prompt",
            value=st.session_state.human_system_prompt,
            help="Enter the system prompt for the human LLM"
        )
        
        st.session_state.assistant_system_prompt = st.text_area(
            "Assistant LLM System Prompt",
            value=st.session_state.assistant_system_prompt,
            help="Enter the system prompt for the assistant LLM"
        )
        
        # Conversation Settings
        st.subheader("Conversation Settings")
        st.session_state.max_turns = st.number_input(
            "Maximum Conversation Turns",
            min_value=1,
            max_value=20,
            value=st.session_state.max_turns,
            help="Maximum number of turns in the conversation"
        )
        
        # Initialize Models
        if st.button("Initialize Models", type="primary", use_container_width=True):
            for role, model_name in st.session_state.selected_models.items():
                if model_name:
                    model_config = st.session_state.saved_models[model_name]
                    st.session_state.llm_instances[role] = create_model(
                        model_name,
                        model_config["api_url"],
                        model_config["api_key"]
                    )
            st.success("Models initialized successfully!")
        
        # Reset Conversation
        if st.button("Reset Conversation", type="primary", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.current_turn = 0
            st.rerun()
    else:
        st.info("Please add models using the 'Add Model' button above")

###########[   MAIN CONTENT    ]###################    

# Only show main content if add model modal is not visible
if not st.session_state.show_add_model:
    # Initial Prompt Input
    if st.session_state.llm_instances["user"] and st.session_state.llm_instances["assistant"]:
        if not st.session_state.conversation:
            initial_prompt = st.text_area(
                "Enter the initial prompt for the human LLM:",
                height=100,
                help="This will be the starting point of the conversation"
            )
            
            if st.button("Start Conversation", type="primary"):
                if initial_prompt:
                    st.session_state.conversation.append({"role": "user", "content": initial_prompt})
                    st.session_state.current_turn = 1
                    st.rerun()
                else:
                    st.error("Please enter an initial prompt")

    # Display Conversation
    if st.session_state.conversation:
        # print(st.session_state.conversation)
        for message in st.session_state.conversation:
            display_role = "human" if message["role"] == "user" else message["role"]
            with st.chat_message(display_role):
                st.markdown(message["content"])
        
        # Continue conversation if not reached max turns
        if st.session_state.current_turn < st.session_state.max_turns:
            with st.spinner('Generating next response...'):
                # Get the last message
                last_message = st.session_state.conversation[-1]
                next_role = "assistant" if last_message["role"] == "user" else "user"

                # Flip roles in conversation history if it's the user LLM's turn
                conversation_for_llm = copy.deepcopy(st.session_state.conversation)
                if next_role == "user":
                    for message in conversation_for_llm:
                        message["role"] = "assistant" if message["role"] == "user" else "user"
                    # del conversation_for_llm[0]
                    conversation_for_llm.insert(0, {"role": "system", "content": st.session_state.human_system_prompt})
                else:
                    conversation_for_llm.insert(0, {"role": "system", "content": st.session_state.assistant_system_prompt})
                print(conversation_for_llm)
                # Generate response
                response = generate_answer(
                    st.session_state.llm_instances[next_role],
                    st.session_state.conversation,
                )
                
                # Add response to conversation
                st.session_state.conversation.append({"role": next_role, "content": response})
                st.session_state.current_turn += 1
                st.rerun()
        else:
            st.info("Conversation reached maximum turns")



