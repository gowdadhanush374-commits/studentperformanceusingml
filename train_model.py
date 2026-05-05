import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

# ---------------- LOAD DATA ----------------
if not os.path.exists("dataset.csv"):
    print("❌ dataset.csv not found!")
    exit()

data = pd.read_csv("dataset.csv")

print("✅ Dataset Loaded Successfully!")
print("Shape:", data.shape)

# ---------------- FEATURES ----------------
X = data.drop("performance", axis=1)
y = data["performance"]

# ---------------- SCALING ----------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------------- SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# ---------------- MODEL ----------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    class_weight='balanced',   # 🔥 IMPORTANT FIX
    random_state=42
)

# ✅ MUST TRAIN MODEL BEFORE PREDICT
model.fit(X_train, y_train)

print("✅ Model training completed!")

# ---------------- PREDICT ----------------
y_pred = model.predict(X_test)

# ---------------- ACCURACY ----------------
acc = accuracy_score(y_test, y_pred)
print(f"🎯 Accuracy: {round(acc * 100, 2)}%")

# Save accuracy
pickle.dump(acc, open("accuracy.pkl", "wb"))

# ---------------- CONFUSION MATRIX ----------------
cm = confusion_matrix(y_test, y_pred)
print("📊 Confusion Matrix:")
print(cm)

# ---------------- FEATURE IMPORTANCE ----------------
features = X.columns
importance = model.feature_importances_

print("\n📌 Feature Importance:")
for f, imp in zip(features, importance):
    print(f"{f}: {round(imp, 3)}")

# ---------------- SAVE MODEL ----------------
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("\n✅ Model & Scaler saved successfully!")