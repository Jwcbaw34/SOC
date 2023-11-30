import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from htmlTemplates import css, bot_template, user_template
from langchain import PromptTemplate

# Call set_page_config here at the top-level scope
st.set_page_config(page_title="SOC-Call Centre chatbot", page_icon=":phone:")

openai_api_key = os.environ.get("OPENAI_API_KEY")

# Read the content of the txt file
with open('faq_content.txt', 'r') as file:
    faq_content = file.read()

template = """
Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question: 
------
<ctx>
{context}
</ctx>
------
<hs>
{history}
</hs>
------
{question}
Answer:
"""
def generate_answer(user_input, faq_content):
    # Access the initialized objects from session_state
    llm = st.session_state.llm
    memory = st.session_state.memory

    # Save user input to memory
    memory.save_context({"input": user_input}, {"output": ""})

    # Prepare the context with FAQs and history
    history = memory.load_memory_variables({}).get('history', '')
    context_with_faq = faq_content

    # Create the prompt
    prompt_text = template.format(history=history, context=context_with_faq, question=user_input)

    # Get the response from the model
    response = llm.predict(prompt_text)
    answer = response

    # Update memory with the system's response
    memory.save_context({"input": user_input}, {"output": response})

    return answer

def handle_userinput(user_question):
    response = generate_answer(user_question, st.session_state.faq_content)

    #response = st.session_state.answer({"query": user_question})

    # Add user's question and bot's response to the chat history
    st.session_state.chat_history.append(('user', user_question))
    st.session_state.chat_history.append(('bot', response))

    # Display the entire chat history
    for sender, message in st.session_state.chat_history:
        if sender == 'user':
            st.write(
                user_template.replace("{{MSG}}", message),
                unsafe_allow_html=True,
            )
        else:
            st.write(
                bot_template.replace("{{MSG}}", message),
                unsafe_allow_html=True
            )

def main():
    # Initialize and store the ChatOpenAI and ConversationBufferMemory objects in session_state
    if 'llm' not in st.session_state:
        st.session_state.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Initialize FAQ content
    if "faq_content" not in st.session_state:
        st.session_state.faq_content = faq_content

    st.set_page_config(page_title="SOC-Call Ctr Chatbot :phone:", page_icon=":phone:")
    st.write(css, unsafe_allow_html=True)

    st.header("SOC-Call Ctr Chatbot :phone:")
    user_question = st.text_input("Have a query from a patient that you need to consult SOC Ops? This chatbot can help:")

    if user_question:
            handle_userinput(user_question)


if __name__ == "__main__":
    main()
