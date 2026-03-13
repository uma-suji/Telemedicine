import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# --------------------------
# 1️⃣ Load datasets
# --------------------------
train = pd.read_csv("training.csv")
test = pd.read_csv("testing.csv")

# --------------------------
# 2️⃣ Drop unnamed / empty columns safely
# --------------------------
train = train.loc[:, ~train.columns.str.contains("^Unnamed", case=False)]
test = test.loc[:, ~test.columns.str.contains("^Unnamed", case=False)]

# --------------------------
# 3️⃣ Clean column names and disease names
# --------------------------
train.columns = [c.strip().lower().replace(" ", "_") for c in train.columns]
test.columns = [c.strip().lower().replace(" ", "_") for c in test.columns]

train['prognosis'] = train['prognosis'].str.lower().str.strip()
test['prognosis'] = test['prognosis'].str.lower().str.strip()

# --------------------------
# 4️⃣ Optional: Keep only common diseases
# --------------------------


# --------------------------
# 5️⃣ Make sure test has same feature columns as train
# --------------------------
feature_columns = train.drop("prognosis", axis=1).columns
test = test[feature_columns.tolist() + ["prognosis"]]  # keep prognosis column

# --------------------------
# 6️⃣ Split features and target
# --------------------------
X_train = train.drop("prognosis", axis=1)
y_train = train["prognosis"]

X_test = test.drop("prognosis", axis=1)
y_test = test["prognosis"]

# --------------------------
# 7️⃣ Train RandomForest model
# --------------------------
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    class_weight="balanced",
    random_state=42)
model.fit(X_train, y_train)

# --------------------------
# 8️⃣ Save trained model
# --------------------------
pickle.dump(model, open("model/model.pkl", "wb"))
print("✅ Model trained and saved as model/model.pkl")

# --------------------------
# 9️⃣ Optional: Check test accuracy
# --------------------------
y_pred = model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, y_pred))