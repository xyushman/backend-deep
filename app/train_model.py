import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "crop_data.csv")

# Load data
data = pd.read_csv(data_path)

X = data.drop("label", axis=1)
y = data["label"]

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save model
model_path = os.path.join(BASE_DIR, "crop_model.pkl")
joblib.dump(model, model_path)

print("Model trained and saved as crop_model.pkl")
