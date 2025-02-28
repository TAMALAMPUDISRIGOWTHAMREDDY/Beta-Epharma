'''import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pickle

# Load dataset
data = pd.read_csv('model/data.csv')

# Check for missing values
print("Checking for missing values:")
print(data.isna().sum())

# Drop rows where 'medicine' column is missing (alternative: you can fill missing values using fillna)
data = data.dropna(subset=['medicine'])

# Prepare feature and target variables
# We will use 'symptom1', 'symptom2', 'symptom3' as features
# and 'medicine' as the target variable
features = data[['symptom1', 'symptom2', 'symptom3']].apply(lambda x: ' '.join(x), axis=1)
target = data['medicine']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Create a pipeline with a CountVectorizer and a Naive Bayes classifier
model = make_pipeline(CountVectorizer(), MultinomialNB())

# Train the model
print("Training the model...")
model.fit(X_train, y_train)

# Test the model's accuracy
accuracy = model.score(X_test, y_test)
print(f'Model accuracy: {accuracy * 100:.2f}%')

# Save the trained model to a file
with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

# Optionally save the trained model to a separate file if you want
with open('train_model.pkl', 'wb') as train_model_file:
    pickle.dump(model, train_model_file)

print("Model training complete and saved.")'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load dataset
data = pd.read_csv('model/data.csv')

# Clean and preprocess data
data = data.dropna(subset=['medicine'])

# Combine symptoms into a single feature
def combine_symptoms(row):
    symptoms = [str(row['symptom1']), str(row['symptom2']), str(row['symptom3'])]
    return ' '.join([sym for sym in symptoms if sym.lower() != 'nan'])

data['combined_symptoms'] = data.apply(combine_symptoms, axis=1)

# Prepare features and target
X = data['combined_symptoms']
y = data['medicine']

# Split data with no stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipeline with TF-IDF and Logistic Regression
model = make_pipeline(
    TfidfVectorizer(stop_words='english', ngram_range=(1,2)),
    LogisticRegression(multi_class='ovr', max_iter=1000)
)

# Train the model
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model accuracy: {accuracy * 100:.2f}%')

# Detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the model
joblib.dump(model, 'model.pkl')
print("Model training complete and saved.")