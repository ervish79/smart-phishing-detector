import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB

# Load dataset
df = pd.read_csv("dataset.csv")

print(df.columns)

# Clean data
df["Email Text"] = df["Email Text"].astype(str)
df = df[
    (df["Email Text"].str.strip() != "") &
    (df["Email Type"].notna())
]

# Features & labels
X = df["Email Text"]
y = df["Email Type"]

# Normalize labels
y = y.str.lower().str.strip()

# Convert labels
y = y.replace({
    "phishing email": 1,
    "safe email": 0,
    "phishing": 1,
    "spam": 1,
    "fraud": 1,
    "legitimate": 0,
    "safe": 0,
    "ham": 0
}).astype(int)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model (better for text)
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Evaluation
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model trained successfully!")