import streamlit as st
import pickle
import re
import time

# =========================
# LOAD MODEL
# =========================
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Phishing Detector", layout="centered")

# =========================
# CUSTOM CSS (MODERN UI)
# =========================
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: white;
}
.stTextArea textarea {
    background-color: #1e293b;
    color: white;
}
.stButton>button {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    color: white;
    border-radius: 10px;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
}
.result-box {
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("AI Phishing Detection System")
st.write("Advanced AI + Cybersecurity based email analyzer")

# =========================
# FUNCTIONS
# =========================
suspicious_words = [
    "urgent", "verify", "password", "click", "login",
    "bank", "account", "suspended", "limited",
    "confirm", "update", "security", "alert"
]

suspicious_phrases = [
    "confirm your account",
    "verify your identity",
    "confirm your transaction",
    "update your details",
    "secure your account",
    "click the link below",
    "proceed using the link",
    "take immediate action",
    "unauthorized activity",
    "your account will be closed"
]

def extract_urls(text):
    return re.findall(r"(https?://\S+|www\.\S+)", text)

def find_suspicious_words(text):
    return [word for word in suspicious_words if word in text.lower()]

def find_suspicious_phrases(text):
    text = text.lower()
    return [phrase for phrase in suspicious_phrases if phrase in text]

def detect_generic_phishing(text):
    text = text.lower()

    triggers = [
        "please review",
        "review your",
        "please confirm",
        "confirm your",
        "please proceed",
        "action required",
        "take action",
        "required to continue",
        "to continue",
        "continue using",
        "needs attention",
        "account needs",
        "verify",
        "confirm",
        "update"
    ]

    count = sum(1 for t in triggers if t in text)
    return count

def find_suspicious_urls(urls):
    keywords = ["login", "verify", "secure", "update", "account"]
    return [url for url in urls if any(k in url.lower() for k in keywords)]

def detect_contextual_phishing(text):
    text = text.lower()

    score = 0

    # Action verbs
    actions = ["access", "proceed", "complete", "review", "continue"]

    # Objects (what user interacts with)
    objects = ["page", "step", "process", "request", "details"]

    # Context words (hidden references)
    context = ["earlier", "previous", "above", "provided", "shared"]

    if any(a in text for a in actions) and any(o in text for o in objects):
        score += 1

    if any(c in text for c in context):
        score += 1

    return score

def detect_behavior_patterns(text):
    text = text.lower()

    score = 0

    # Action + Process pattern
    if any(x in text for x in ["complete", "review", "proceed"]) and \
       any(x in text for x in ["process", "step", "request"]):
        score += 1

    # Authority + maintenance pattern
    if any(x in text for x in ["routine", "policy", "process"]) and \
       any(x in text for x in ["account", "information", "access"]):
        score += 1

    # Soft pressure pattern
    if any(x in text for x in ["pending", "remaining", "required"]):
        score += 1

    return score

def predict(text):
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    prob = model.predict_proba(text_vec)[0]
    return prediction, prob

# =========================
# INPUT
# =========================
user_input = st.text_area("Paste Email Content Here")

# =========================
# ANALYZE BUTTON
# =========================
if st.button("Analyze Email"):

    if user_input.strip() == "":
        st.warning("Please enter email content")
    else:
        # Loading animation
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        # =========================
        # AI PREDICTION
        # =========================
        prediction, prob = predict(user_input)

        phishing_prob = prob[1] * 100
        safe_prob = prob[0] * 100

        # =========================
        # SECURITY ANALYSIS
        # =========================
        urls = extract_urls(user_input)
        words = find_suspicious_words(user_input)
        suspicious_urls = find_suspicious_urls(urls)
        phrases = find_suspicious_phrases(user_input)
        generic_score = detect_generic_phishing(user_input)
        context_score = detect_contextual_phishing(user_input)
        behavior_score = detect_behavior_patterns(user_input)

        # =========================
        # HYBRID RISK SCORE
        # =========================
        risk_score = phishing_prob *0.6

        if urls:
            risk_score += 10

        if suspicious_urls:
            risk_score += 15

        risk_score += len(words) * 2
        risk_score += len(phrases) * 6
        risk_score += generic_score * 6
        risk_score += context_score * 10
        risk_score += behavior_score * 9
        

        

        # If multiple weak signals exist → treat as suspicious
        if (behavior_score + context_score + generic_score) >= 2 and phishing_prob < 50:
            risk_score += 20

        # Detect implicit link behavior
        if context_score >= 2 and not urls:
            risk_score += 15


        # Detect hidden link intent (no URL but mentions link)
        if "link" in user_input.lower() and not urls:
            risk_score += 12

        # Force suspicion for clean phishing
        if phishing_prob < 40 and (generic_score > 0 or phrases):
            risk_score += 8

        intent_signals = generic_score + context_score + behavior_score
        if intent_signals >= 2:
            risk_score = max(risk_score,55)

        if intent_signals >=3:
            risk_score = max(risk_score, 65)


        if phishing_prob < 50 and generic_score >= 1:
            risk_score = max(risk_score, 60)

        risk_score =max(0, min(risk_score, 100))
        risk_score = round(risk_score, 2)

        if phishing_prob < 50 and (generic_score >= 1 or behavior_score >= 1):
            risk_score = min(risk_score, 75)

        # =========================
        # RESULT SECTION
        # =========================
        st.markdown("## Analysis Result")

        if risk_score > 75:
            st.markdown(f"""
            <div class="result-box" style="background-color:#7f1d1d;">
            <h3>High Risk: Phishing Email</h3>
            <p>Risk Score: {risk_score:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

        elif risk_score > 50:
            st.markdown(f"""
            <div class="result-box" style="background-color:#78350f;">
            <h3>Suspicious Email</h3>
            <p>Risk Score: {risk_score:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="result-box" style="background-color:#064e3b;">
            <h3>Safe Email</h3>
            <p>Risk Score: {risk_score:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # CONFIDENCE BARS
        # =========================
        st.subheader("AI Confidence")
        st.write("Phishing Probability")
        st.progress(int(phishing_prob))

        st.write("Safe Probability")
        st.progress(int(safe_prob))

        # =========================
        # SECURITY DETAILS
        # =========================
        st.subheader("Security Analysis")

        col1, col2, col3, col4= st.columns(4)

        with col1:
            st.write("Detected Links")
            if urls:
                st.error(urls)
            else:
                st.success("No links found")

        with col2:
            st.write("Suspicious Keywords")
            if words:
                st.warning(words)
            else:
                st.success("None detected")

        with col3:
            st.write("Suspicious Phrases")
            if phrases:
                st.warning(phrases)
            else:
                st.success("None detected")

        with col4:
            st.write("Generic Suspicion Score")
            if generic_score > 0:
                st.warning(f"Detected {generic_score} suspicious patterns")
            else:
                st.success("None detected")    

        # =========================
        # EXPLANATION
        # =========================
        st.subheader("Explanation")

        if risk_score > 75:
            st.write("This email is highly likely to be phishing due to:")

        elif risk_score > 50:
            st.write("This email is suspicious due to:")

        else:
            st.write("This email appears safe because:")

        if urls:
            st.write("- Contains links (common phishing method)")

        if suspicious_urls:
            st.write("- Contains high-risk URLs (login/verify keywords)")

        if words:
            st.write("- Uses urgency or security-related language")

        st.write("- AI model prediction contributes to final score")