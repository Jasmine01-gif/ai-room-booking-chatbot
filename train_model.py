import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sentences = [
"book a room",
"I want to book a room",
"reserve meeting room",
"cancel booking",
"delete my booking",
"is room available",
"check room availability"
]

labels = [
"book",
"book",
"book",
"cancel",
"cancel",
"check",
"check"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sentences)

model = LogisticRegression()
model.fit(X, labels)

pickle.dump(model, open("model.pkl","wb"))
pickle.dump(vectorizer, open("vectorizer.pkl","wb"))

print("Model trained successfully")