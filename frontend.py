import streamlit as st
from api_llm import create_model, generate_answer
from funct import change_model, reset_values, clear_chat
import copy
import json
from datetime import datetime
import os
import pandas as pd

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
        overflow-y: auto;
        padding-top: 0;
        margin-top: 0;
    }
    section[data-testid="stSidebar"] > div > div {
        padding-top: 0;
        margin-top: 0;
    }
    /* Hide the top banner */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Style for active tab */
    .stButton button.active-tab {
        background-color: #262730;
        color: white;
    }
    /* Custom scrollbar styling */
    section[data-testid="stSidebar"] > div::-webkit-scrollbar {
        width: 8px;
    }
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-track {
        background: #262730;
    }
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
        background: #4B4B4B;
        border-radius: 4px;
    }
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
        background: #555;
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
    st.session_state.human_system_prompt = "You are a human talking to an AI."
if "assistant_system_prompt" not in st.session_state:
    st.session_state.assistant_system_prompt = ""
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "single"  # Default to single run mode

####################################[   FRONTEND - MAIN SCREEN ]#####################################################    

# Top Bar
col1, col2, col3, col4, col5 = st.columns([0.55, 0.1, 0.1, 0.1, 0.15])
with col1:
    st.markdown("<h1 style='margin: 0; padding: 0;'>LLM Playground</h1>", unsafe_allow_html=True)
with col2:
    if st.button("Single Run", use_container_width=True, key="single_run_btn", 
                help="Run a single conversation between two models"):
        st.session_state.current_mode = "single"
        st.rerun()
with col3:
    if st.button("Multi Run", use_container_width=True, key="multi_run_btn",
                help="Run multiple conversations with different model configurations"):
        st.session_state.current_mode = "multi"
        st.rerun()
with col4:
    if st.button("Add Model", use_container_width=True):
        st.session_state.show_add_model = True

with col5:
    if st.button("Save Conversation", use_container_width=True):
        if st.session_state.conversation:
            # Create conversations directory if it doesn't exist
            conversations_dir = "single_run_results"
            os.makedirs(conversations_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            filepath = os.path.join(conversations_dir, filename)
            
            # Save conversation to file
            with open(filepath, 'w') as f:
                json.dump({
                    "models_used": st.session_state.selected_models,
                    "human_system_prompt": st.session_state.human_system_prompt,
                    "assistant_system_prompt": st.session_state.assistant_system_prompt,
                    "max_turns": st.session_state.max_turns,
                    "conversation": st.session_state.conversation
                }, f, indent=2)
            st.success(f"Conversation saved to {filepath}")
        else:
            st.warning("No conversation to save")
st.markdown("---")

# Add Model Dialog
@st.dialog("Add New Model")
def add_model_dialog():
    model_name = st.text_input("Model Name", help="Enter a name for this model configuration")
    api_url = st.text_input("API URL", help="Enter the API endpoint URL (e.g., https://api.openai.com/v1/chat/completions)")
    api_key = st.text_input("API Key", type="password", help="Enter your API key")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Model", use_container_width=True, key="dialog_add_model_btn"):
            if model_name and api_url and api_key:
                st.session_state.saved_models[model_name] = {
                    "api_url": api_url,
                    "api_key": api_key
                }
                st.success(f"Model '{model_name}' added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all fields")
    with col2:
        if st.button("Cancel", use_container_width=True, key="dialog_cancel_btn"):
            st.rerun()

# Call the dialog when show_add_model is True
if st.session_state.show_add_model:
    add_model_dialog()
    st.session_state.show_add_model = False

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
    if st.session_state.current_mode == "single":
        # Single Run Mode (existing chat interface)
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
            for message in st.session_state.conversation:
                display_role = "human" if message["role"] == "user" else message["role"]
                with st.chat_message(display_role):
                    st.markdown(message["content"])
            
            # Continue conversation if not reached max turns
            if st.session_state.current_turn <= st.session_state.max_turns:
                with st.spinner('Generating next response...'):
                    # Get the last message
                    last_message = st.session_state.conversation[-1]
                    next_role = "assistant" if last_message["role"] == "user" else "user"

                    # Flip roles in conversation history if it's the user LLM's turn
                    conversation_for_llm = copy.deepcopy(st.session_state.conversation)
                    if next_role == "user":
                        for message in conversation_for_llm:
                            message["role"] = "assistant" if message["role"] == "user" else "user"
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
                    
                    # Only increment turn counter when we complete a full exchange (user + assistant)
                    if next_role == "assistant":
                        st.session_state.current_turn += 1
                    st.rerun()
            else:
                st.info("Conversation reached maximum turns")
    else:
        # Multi Run Mode
        st.header("Multi Run Mode")
        
        # File upload section
        uploaded_file = st.file_uploader("Upload JSON file with prompts", type=['json'], 
                                       help="Upload a JSON file containing prompts for multiple conversations")
        
        if uploaded_file is not None:
            try:
                # Read and parse the JSON file
                prompts_data = json.load(uploaded_file)
                
                # Validate JSON structure
                if not isinstance(prompts_data, list):
                    st.error("JSON file must contain an array of prompts")
                else:
                    # Display the prompts in a table
                    st.subheader("Loaded Prompts")
                    prompts_df = pd.DataFrame(prompts_data)
                    prompts_df.index = prompts_df.index + 1
                    prompts_df.columns = ["Prompt"]
                    st.dataframe(prompts_df, use_container_width=True)
                    
                    # Run button
                    if st.button("Run Conversations", type="primary", use_container_width=True):
                        if st.session_state.llm_instances["assistant"]:
                            # Create a progress bar
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Store results
                            results = []
                            
                            # Run each conversation
                            for i, prompt in enumerate(prompts_data):
                                status_text.text(f"Running conversation {i+1}/{len(prompts_data)}...")
                                
                                # Initialize conversation
                                assistant_conversation = [{"role": "system", "content": st.session_state.assistant_system_prompt},
                                              {"role": "user", "content": prompt}]
                                
                                user_conversation = [{"role": "system", "content": st.session_state.human_system_prompt},
                                              {"role": "assistant", "content": prompt}]
                                
                                # Run conversation
                                for turn in range(st.session_state.max_turns): 
                                    # Generate response
                                    assistant_response = generate_answer(
                                        st.session_state.llm_instances["assistant"],
                                        assistant_conversation
                                    )
                                    
                                    # Add response to conversation
                                    assistant_conversation.append({"role": "assistant", "content": assistant_response})
                                    user_conversation.append({"role": "user", "content": assistant_response})
                                    
                                    # Add user's next prompt if not the last turn
                                    if turn < st.session_state.max_turns - 1:
                                        user_response = generate_answer(
                                            st.session_state.llm_instances["user"],
                                            user_conversation
                                        )
                                        user_conversation.append({"role": "assistant", "content": user_response})
                                        assistant_conversation.append({"role": "user", "content": user_response})
                                
                                print(assistant_conversation)
                                # Store results
                                results.append({
                                    "prompt": prompt,
                                    "conversation": assistant_conversation
                                })
                                
                                # Update progress
                                progress_bar.progress((i + 1) / len(prompts_data))
                            
                            # Save results
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            results_dir = "multi_run_results"
                            os.makedirs(results_dir, exist_ok=True)
                            results_file = os.path.join(results_dir, f"results_{timestamp}.json")
                            
                            with open(results_file, 'w') as f:
                                json.dump({
                                    "models_used": st.session_state.selected_models,
                                    "human_system_prompt": st.session_state.human_system_prompt,
                                    "assistant_system_prompt": st.session_state.assistant_system_prompt,
                                    "max_turns": st.session_state.max_turns,
                                    "results": results
                                }, f, indent=2)
                            
                            st.success(f"All conversations completed! Results saved to {results_file}")
                            
                            # Display results
                            st.subheader("Results")
                            for i, result in enumerate(results):
                                with st.expander(f"Conversation {i+1}"):
                                    for message in result["conversation"]:
                                        if message["role"] != "system":  # Skip system messages
                                            st.markdown(f"**{message['role'].title()}**: {message['content']}")
                        else:
                            st.error("Please initialize the assistant model in the sidebar first")
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid JSON file.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.info("""
            Please upload a JSON file containing an array of prompts. The file should be formatted like this:
            ```json
            [
                "What is the capital of France?",
                "Explain quantum computing",
                "Write a short poem about AI"
            ]
            ```
            """)



