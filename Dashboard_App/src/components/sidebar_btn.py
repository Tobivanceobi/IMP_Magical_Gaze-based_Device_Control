import streamlit as st


def sidebar_button(label):
    key = "sidebar_btn_" + label
    return st.sidebar.button(label, key=key, use_container_width=True)