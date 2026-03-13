import pickle
import numpy as np
import pandas as pd

# Load trained model
model = pickle.load(open("model/model.pkl", "rb"))

# Get feature names used during training
feature_names = model.feature_names_in_

def predict_disease(symptom_string):

    input_symptoms = [s.strip().lower() for s in symptom_string.split(",")]

    input_dict = {feature: 0 for feature in feature_names}

    for symptom in input_symptoms:
        # remove spaces and lowercase
        symptom = symptom.replace(" ", "").lower()

        # match with dataset feature names
        for feature in feature_names:
            if symptom == feature.replace("_", "").lower():
                input_dict[feature] = 1
                break

    input_df = pd.DataFrame([input_dict])

    probs = model.predict_proba(input_df)[0]
    max_index = probs.argmax()
    confidence = probs[max_index] * 100
    disease = model.classes_[max_index]

    return f"{disease} ({round(confidence,2)}% confidence)"