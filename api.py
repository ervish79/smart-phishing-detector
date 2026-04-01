from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)

# ✅ VERY IMPORTANT (FULL FIX)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():

    # ✅ Handle preflight request properly
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    try:
        data = request.json
        text = data.get("text", "")

        # ✅ LIMIT TEXT (important)
        if len(text) > 2000:
            text = text[:2000]

        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)[0]
        prob = model.predict_proba(text_vec)[0]

        phishing_prob = float(prob[1]) * 100

        response = jsonify({
            "prediction": int(prediction),
            "phishing_prob": phishing_prob
        })

        # ✅ ADD HEADERS TO ACTUAL RESPONSE TOO
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
