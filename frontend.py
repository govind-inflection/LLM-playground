import streamlit as st
from api_llm import create_model, generate_answer
from funct import change_model, reset_values, clear_chat

st.set_page_config(page_title="LLM Playground", layout='wide', page_icon='🦜🔗')

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

####################################[   FRONTEND - MAIN SCREEN ]#####################################################    

# Top Bar
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("LLM Playground")
with col2:
    if st.button("Add Model", use_container_width=True):
        st.session_state.show_add_model = True

st.text("Configure two LLMs to have a conversation with each other")
st.markdown("""---""")

# Add Model Modal
if st.session_state.show_add_model:
    with st.form("add_model_form"):
        st.subheader("Add New Model")
        model_name = st.text_input("Model Name", help="Enter a name for this model configuration")
        api_url = st.text_input("API URL", help="Enter the API endpoint URL (e.g., https://api.openai.com/v1/chat/completions)")
        api_key = st.text_input("API Key", type="password", help="Enter your API key")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("Add Model")
        with col2:
            if st.form_submit_button("Cancel"):
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

# Initial Prompt Input
if st.session_state.llm_instances["human"] and st.session_state.llm_instances["assistant"]:
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
    print(st.session_state.conversation)
    print(st.session_state.llm_instances)
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



