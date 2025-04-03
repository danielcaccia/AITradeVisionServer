from flask import Flask, request, jsonify
from model.sentiment_analyzer import SentimentAnalyzer

app = Flask(__name__)
analyzer = SentimentAnalyzer()

@app.route("/", methods=["GET"])
def home():
    return "FinBERT Sentiment Analysis API is running!"

@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Missing text/Text not provided."}), 400

        sentiment = analyzer.analyze(text)
        return jsonify({"sentiment": sentiment})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
