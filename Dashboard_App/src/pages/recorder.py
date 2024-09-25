import streamlit as st
from ..utils import Page


class PageRecorder(Page):
    NAME = "Gaze Recorder"
    def __init__(self):
        pass

    def write(self):
        st.title(self.NAME)