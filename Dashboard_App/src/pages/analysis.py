import streamlit as st
from ..utils import Page


class PageAnalysis(Page):
    NAME = "Analysis"
    def __init__(self):
        pass

    def write(self):
        st.title(self.NAME)