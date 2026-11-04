
import streamlit as st
from agent import investigate

st.set_page_config(
    page_title="Agentic AI: for Broadcast Viewership Data Analysis",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agentic AI: for Broadcast Viewership Data Analysis")

st.caption(
    "Agentic AI Created by Jomin: on top of "
    "Azure Databricks SQL and Delta Lake"
)

st.divider()

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input(
    "Ask a question about TV ratings or ETL pipelines..."
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(
            "Investigating data in Azure Databricks..."
        ):
            try:
                answer = investigate(question)
                st.markdown(answer)
            except Exception as error:
                st.error(
                    "Investigation failed. "
                    "Check the application terminal for details."
                )
                raise

    if "answer" in locals():
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
