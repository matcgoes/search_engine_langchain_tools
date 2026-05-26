import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_classic.agents import initialize_agent, AgentType          
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from dotenv import load_dotenv

load_dotenv()                                                       

## Arxiv Tools
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=250)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)               

## Wikipedia Tools
api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

search = DuckDuckGoSearchRun(name="Search")

st.title("LangChain - Chat with search")
st.caption(                                                         
    "Using `StreamlitCallbackHandler` to display agent thoughts and actions. "
    "See more examples at [langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent)."
)

## Sidebar for settings
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Groq API Key", type="password")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is machine learning?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    
    if not api_key:
        st.warning("Please enter your Groq API Key in the sidebar to continue.")
        st.stop()

    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True)
    tools = [search, arxiv, wiki]                                   

    search_agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        max_iterations=3,
        max_execution_time=20,
        early_stopping_method="generate",
        verbose=True,
    )
    

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        try:
            response = search_agent.run(prompt, callbacks=[st_cb])  
        except Exception as e:                                      
            response = f"Sorry, I encountered an error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)