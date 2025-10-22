# userdata_server.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/questions")
def get_questions():
    """Stub user profile returned to the MCP tool."""
    return jsonify({
        "preferences": ["Prefrences from the backend"],
        "bio": "I love exploring nature and trying new recipes."
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)