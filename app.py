
import os
import hmac
import streamlit as st

# --------------------------------------------------
# Streamlit page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Agentic AI: for Broadcast Viewership Data Analysis",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Password authentication
# --------------------------------------------------
def check_password():
    if st.session_state.get("authenticated", False):
        return True

    st.title("Broadcast Viewership Agentic AI")

    password = st.text_input(
        "Enter access password",
        type="password"
    )

    if st.button("Sign in"):
        expected = os.environ.get("APP_PASSWORD", "")

        if not expected:
            st.error(
                "APP_PASSWORD is not configured. "
                "Check your Streamlit Cloud Secrets."
            )
        elif hmac.compare_digest(password, expected):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    return False


# --------------------------------------------------
# Stop execution until authenticated
# --------------------------------------------------
if not check_password():
    st.stop()


# --------------------------------------------------
# Main application
# --------------------------------------------------
st.title("🤖 Agentic AI: for Broadcast Viewership Data Analysis")

st.caption(
    "Agentic AI Created by Jomin: on top of "
    "Azure Databricks SQL and Delta Lake"
)

st.divider()


# --------------------------------------------------
# Initialize conversation history
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Display previous messages
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# Chat input
# --------------------------------------------------
question = st.chat_input(
    "Ask a question about TV ratings or ETL pipelines..."
)


# --------------------------------------------------
# Process question using Agentic AI
# --------------------------------------------------
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
                # Lazy import:
                # Load the agent only after a question is submitted.
                from agent import investigate

                answer = investigate(question)

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(
                    "Investigation failed. "
                    "Check the Streamlit Cloud logs for details."
                )
                raise
