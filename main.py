from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Judy Chatbot is running! (Basic Version)"

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "")
    if not user_question:
        return jsonify({"error": "Please provide a question"}), 400

    # Temporary dummy response for testing
    return jsonify({"answer": f"You asked: {user_question}. Judy is live!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
