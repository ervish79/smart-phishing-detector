from flask import Flask, request, jsonify
from flask_cors import CORS   # 👈 ADD THIS
import pickle

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 👈 ADD THIS (CRITICAL)


@app.after_request
def after_request(response):
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS'
    response.headers.add('Access-Control-Allow-Private-Network', 'true')
    return response
# Load model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    if request.method =="OPTIONS":
        return jsonify({"status": "ok"})
    try:
        data = request.json
        text = data.get("text", "")

        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)[0]
        prob = model.predict_proba(text_vec)[0]

        phishing_prob = float(prob[1]) * 100

        return jsonify({
            "prediction": int(prediction),
            "phishing_prob": phishing_prob
       })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
