# LLM-playground
Large Language Model Playground: experiment with Llama2, Falcon, GPT, and Flan chat LLM and tune LLM parameters

| **Model**              | **Source** | **Parameters** | **Fine tuned for dialog task** | **Open-source** | **Model Link**                                         |
|------------------------|------------|----------------|--------------------------------|-----------------|--------------------------------------------------|
| **GPT**                | OpenAI     | 14.8 Billion   | No                             | No              | [Click He](https://openai.com/pricing)                     |
| **llama-2-70b-chat**   | Meta       | 70 Billion     | Yes                            | Yes             | [Click He](https://replicate.com/meta/llama-2-70b-chat)      |
| **llama-2-13b-chat**   | Meta       | 13 Billion     | Yes                            | Yes             | [Click He](https://replicate.com/meta/llama-2-13b-chat)      |
| **llama-2-7b-chat**    | Meta       | 7 Billion      | Yes                            | Yes             | [Click He](https://replicate.com/meta/llama-2-7b-chat)       |
| **falcon-7b-instruct** | TII        | 7 Billion      | Yes                            | Yes             | [Click He](https://huggingface.co/tiiuae/falcon-7b-instruct) |
| **flan-ul2**           | Google     | 20 Billion     | Yes                            | Yes             | [Click He](https://huggingface.co/google/flan-ul2)           |

## Control the LLM powered chatbot using LLM parameters
- **Six LLM models**: Change the used model
- **Temperature range [0.1-1]**: Control the creativity of the answer 
- **Output length range [1-1000]**: Control the output's maximum number of tokens

## Features of the project
- Interacting with conversational agents via simple UI
- Fast load and delete models for assessing the LLM models' performance on specific
- API keys for all models are provided except for GPT model (provided by users)
## Demo
For live demo visit https://llm-playground-etp4.onrender.com/

https://github.com/shaimaaK/LLM-playground/assets/54285485/90293af5-c7b7-4c48-a65b-31589ada3c9d



## A Guide to Installation and Use
Make sure all libraries included in the ``requirements.txt`` file and their dependencies are installed using pip or conda command on your virtual environment.
```
pip install langchain==0.0.345
pip install python-dotenv==1.0.0
pip install streamlit==1.29.0
pip install replicate==0.20.0
pip install huggingface_hub==0.19.4
pip instal

https://github.com/shaimaaK/LLM-playground/assets/54285485/e18bbeaa-4b81-4f1e-84e9-2c100ff64491

l openai==1.3.5
```
To run the application, open the terminal in the root directory and execute the following command
```
streamlit run frontend.py 
```

