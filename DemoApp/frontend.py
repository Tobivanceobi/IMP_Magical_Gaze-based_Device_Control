import streamlit as st
import requests
import time
import matplotlib.pyplot as plt

# API Base URL
API_BASE_URL = "http://127.0.0.1:5000"

def get_stick_figure_state():
    """Get the current state of the stick figure from the backend."""
    response = requests.get(f"{API_BASE_URL}/state")
    return response.json()

def plot_stick_figure(state):
    """Visualize the stick figure."""
    position = state["position"]
    toggled_on = state["toggled_on"]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.grid(True)

    # Draw stick figure (head, body, arms, legs)
    x, y = position["x"], position["y"]
    color = "green" if toggled_on else "black"

    # Head
    head = plt.Circle((x, y + 0.5), 0.3, color=color, fill=True)
    ax.add_artist(head)

    # Body
    ax.plot([x, x], [y - 1, y + 0.5], color=color, linewidth=2)

    # Arms
    ax.plot([x - 0.5, x + 0.5], [y, y], color=color, linewidth=2)

    # Legs
    ax.plot([x, x - 0.5], [y - 1, y - 1.5], color=color, linewidth=2)
    ax.plot([x, x + 0.5], [y - 1, y - 1.5], color=color, linewidth=2)

    ax.set_aspect("equal")
    return fig

st.title("Stick Figure Controller")

placeholder = st.empty()

# Refresh the stick figure state periodically
while True:
    state = get_stick_figure_state()

    with placeholder.container():
        st.pyplot(plot_stick_figure(state))

    time.sleep(1)