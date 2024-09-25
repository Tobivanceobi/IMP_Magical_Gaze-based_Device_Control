import streamlit as st
from abc import ABC, abstractmethod


class Page(ABC):
    @abstractmethod
    def write(self):
        pass


def add_custom_css():
    sidebar_button_style = """
            <style>
            /* Remove rounded corners from sidebar buttons */
            div[data-testid="stSidebarContent"] button[kind="secondary"] {
                border-radius: 0 !important;
            }
            </style>
        """
    # Apply CSS style for square corners
    st.sidebar.markdown(sidebar_button_style, unsafe_allow_html=True)