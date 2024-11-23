from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import joblib
import numpy as np
from nltk.tokenize import word_tokenize

app = Flask(__name__)
CORS(app)

model = joblib.load('model/diabetes_model.pkl')
scaler = joblib.load('model/scaler.pkl')

knowledge_base = {
    "diabetes_definition": "Diabetes is a chronic condition that affects how your body processes blood sugar (glucose).",
    "diabetes_causes": "Common causes include genetic factors, obesity, physical inactivity, and poor diet.",
    "diabetes_symptoms": (
        "Symptoms of diabetes include frequent urination, excessive thirst, fatigue, blurred vision, "
        "slow-healing wounds, and unexpected weight loss."
    ),
    "diabetes_treatment": (
        "Diabetes can be managed with lifestyle changes like a healthy diet, regular exercise, and medication as prescribed. "
        "For Type 1 diabetes, insulin therapy is essential. For Type 2, managing weight and blood sugar levels is key."
    ),
    "general_health_tips": (
        "General tips for good health: Stay hydrated, eat a balanced diet, exercise regularly, get enough sleep, "
        "and avoid smoking or excessive alcohol consumption."
    ),
    "fun_fact": "Did you know? Walking for just 30 minutes a day can reduce your risk of chronic diseases like diabetes and heart disease!"
}

def get_intent(user_input):
    user_input = user_input.lower()
    tokens = word_tokenize(user_input)

    intents = {
        "greeting": ["hello", "hi", "hey"],
        "diabetes_definition": ["what is diabetes", "define diabetes", "diabetes meaning"],
        "diabetes_causes": ["causes of diabetes", "why diabetes", "diabetes reasons"],
        "diabetes_symptoms": ["symptoms of diabetes", "signs of diabetes", "diabetes symptoms"],
        "diabetes_treatment": ["treatment for diabetes", "manage diabetes", "cure for diabetes"],
        "general_health_tips": ["health tips", "stay healthy", "healthy life"],
        "fun_fact": ["tell me something interesting", "fun fact", "did you know"],
        "predict_request": ["predict", "diabetes", "check risk", "diabetes prediction"],
        "thanks": ["thank you", "thanks", "appreciate"],
    }

    for intent, keywords in intents.items():
        if any(keyword in user_input for keyword in keywords):
            return intent

    return "default"

def generate_response(intent):
    if intent in knowledge_base:
        return knowledge_base[intent]
    elif intent == "greeting":
        return "Hello! I'm here to help you with diabetes-related questions and health tips. How can I assist you today?"
    elif intent == "predict_request":
        return "Please provide your health details to predict your diabetes risk. Use the /predict endpoint with the necessary parameters."
    elif intent == "thanks":
        return "You're welcome! Stay healthy and feel free to ask more questions."
    else:
        return (
            "I'm sorry, I couldn't understand your question. Could you please rephrase it? "
            "I can assist with diabetes-related queries or general health advice."
        )

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")
    intent = get_intent(user_input)
    response = generate_response(intent)
    return jsonify({"response": response})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        features = [
            data['pregnancies'], data['glucose'], data['blood_pressure'],
            data['skin_thickness'], data['insulin'], data['bmi'],
            data['diabetes_pedigree'], data['age']
        ]

        input_data = scaler.transform([features])

        prediction = model.predict(input_data)
        result = "Diabetic" if prediction[0] == 1 else "Non-Diabetic"

        if prediction[0] == 1:
            response = {
                "prediction": result,
                "advice": (
                    "Based on your results, it seems you may be at risk of diabetes. Here are some tips to manage your health:\n"
                    "- Incorporate at least 30 minutes of exercise daily (e.g., walking, yoga, or cycling).\n"
                    "- Reduce sugar and refined carbohydrate intake.\n"
                    "- Eat more fiber-rich foods like vegetables and whole grains.\n"
                    "- Stay hydrated and drink plenty of water.\n"
                    "- Regularly monitor your blood glucose levels and consult a healthcare professional."
                )
            }
        else:
            response = {
                "prediction": result,
                "advice": (
                    "Great news! Based on your results, it seems you are not diabetic. "
                    "Keep maintaining a healthy lifestyle with regular exercise, a balanced diet, and proper sleep. "
                    "Stay proactive about your health!"
                )
            }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
