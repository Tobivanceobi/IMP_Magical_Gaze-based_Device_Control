import streamlit as st
from ..utils import Page


class PageGazeCls(Page):
    NAME = "Gaze Classification"
    def __init__(self):
        pass

    def write(self):
        st.title(self.NAME)