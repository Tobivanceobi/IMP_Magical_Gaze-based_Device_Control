from flask import Flask, request, jsonify

app = Flask(__name__)

# Initial state of the stick figure
stick_figure_state = {
    "position": {"x": 5, "y": 5},
    "toggled_on": False 
}


@app.route("/move", methods=["POST"])
def move_stick_figure():
    """Move the stick figure in a specific direction."""
    data = request.json
    direction = data.get("direction")

    if not direction or direction not in ["up", "down", "left", "right"]:
        return jsonify({"error": "Invalid direction"}), 400

    # Update position based on direction
    if direction == "up" and stick_figure_state["position"]["y"] < 10:
        stick_figure_state["position"]["y"] += 1
    elif direction == "down" and stick_figure_state["position"]["y"] > 0:
        stick_figure_state["position"]["y"] -= 1
    elif direction == "left" and stick_figure_state["position"]["x"] > 0:
        stick_figure_state["position"]["x"] -= 1
    elif direction == "right" and stick_figure_state["position"]["x"] < 10:
        stick_figure_state["position"]["x"] += 1

    return jsonify(stick_figure_state)


@app.route("/toggle", methods=["POST"])
def toggle_stick_figure():
    """Toggle the stick figure's 'on/off' state."""
    stick_figure_state["toggled_on"] = not stick_figure_state["toggled_on"]
    return jsonify(stick_figure_state)


@app.route("/state", methods=["GET"])
def get_stick_figure_state():
    """Get the current state of the stick figure."""
    return jsonify(stick_figure_state)


if __name__ == "__main__":
    app.run(debug=True)