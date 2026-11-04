import os
import hmac
import streamlit as st

st.set_page_config(page_title="Broadcast Viewership Agentic AI")

st.title("Broadcast Viewership Agentic AI")

password = st.text_input("Enter access password", type="password")

if st.button("Sign in"):
    expected = os.environ.get("APP_PASSWORD", "")

    if not expected:
        st.error("APP_PASSWORD is missing from the environment.")
    elif hmac.compare_digest(password, expected):
        st.success("Authentication successful!")
    else:
        st.error("Incorrect password")
