import streamlit as st
import pickle
import pandas as pd
import numpy as np
from thefuzz import process
import ast

st.set_page_config(page_title="AI-Powered Healthcare Intelligence Network", page_icon="🩺", layout='wide')

st.sidebar.markdown("<h2 style='color: #ffffff;'>📌 Description</h2>", unsafe_allow_html=True)
st.sidebar.image("utils/ph3.png", use_container_width=True)
st.sidebar.markdown("<p class='sidebar-text'>The Disease Prediction & Medical Recommendation system uses AI to analyze symptoms, predict diseases, assess health risks, and suggest personalized treatments—enhancing early diagnosis and improving healthcare decisions for better patient outcomes.</p>", unsafe_allow_html=True)



import re

def normalize_disease_name(s):
    if not isinstance(s, str):
        return ''
    s = s.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('diseae', 'disease')
    return s

@st.cache_resource
def load_data():
    try:
        sym_des = pd.read_csv("data/Disease-Prediction-and-Medical dataset/symptoms_df.csv")
        precautions = pd.read_csv("data/Disease-Prediction-and-Medical dataset/precautions_df.csv")
        workout = pd.read_csv("data/Disease-Prediction-and-Medical dataset/workout_df.csv")
        description = pd.read_csv("data/Disease-Prediction-and-Medical dataset/description.csv")
        medications = pd.read_csv("data/Disease-Prediction-and-Medical dataset/medications.csv")
        diets = pd.read_csv("data/Disease-Prediction-and-Medical dataset/diets.csv")
        model = pickle.load(open('models/first_feature_models/RandomForest.pkl', 'rb'))

        for df, col in [(precautions, 'Disease'), (workout, 'disease'), (description, 'Disease'), (medications, 'Disease'), (diets, 'Disease')]:
            df['norm_disease'] = df[col].apply(normalize_disease_name)

        return sym_des, precautions, workout, description, medications, diets, model
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None, None

sym_des, precautions, workout, description, medications, diets, model = load_data()

disease_names = sorted(list(description['Disease'].unique())) if description is not None else []

symptoms_list = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer disease', 1: 'AIDS', 12: 'Diabetes', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

symptoms_list_processed = {symptom.replace('_', ' ').lower(): value for symptom, value in symptoms_list.items()}

def information(predicted_dis):
    try:
        target_norm = normalize_disease_name(predicted_dis)

        desc_match = description.loc[description['norm_disease'] == target_norm]
        disease_description = desc_match['Description'].values[0] if not desc_match.empty else "Description not available"

        prec_match = precautions.loc[precautions['norm_disease'] == target_norm, ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
        disease_precautions = prec_match.values.flatten().tolist() if not prec_match.empty else []

        med_match = medications.loc[medications['norm_disease'] == target_norm]
        disease_medications = ast.literal_eval(med_match['Medication'].values[0]) if not med_match.empty else []

        diet_match = diets.loc[diets['norm_disease'] == target_norm]
        disease_diet = ast.literal_eval(diet_match['Diet'].values[0]) if not diet_match.empty else []

        workout_match = workout.loc[workout['norm_disease'] == target_norm]
        disease_workout = workout_match['workout'].values.tolist() if not workout_match.empty else []

        return disease_description, disease_precautions, disease_medications, disease_diet, disease_workout
    except Exception:
        return "Description not available", [], [], [], []

def predicted_value(patient_symptoms):
    try:
        i_vector = np.zeros(len(symptoms_list_processed))
        for symptom in patient_symptoms:
            if symptom in symptoms_list_processed:
                i_vector[symptoms_list_processed[symptom]] = 1
        prediction_index = model.predict([i_vector])[0]
        return diseases_list.get(prediction_index, "Unknown Disease")
    except Exception:
        return "Prediction Error"

def correct_spelling(symptom):
    closest_match, score = process.extractOne(symptom, symptoms_list_processed.keys())
    return closest_match if score >= 80 else None

st.title("🩺 Disease Prediction & Medical Recommendation")

# Disease Prediction Section
st.markdown("### Disease Prediction Based on Symptoms")
st.markdown("_To get the best and most accurate results, provide as many symptoms as possible._")
user_input = st.text_area("Enter symptoms (comma-separated):", placeholder="e.g., headache, constipation, nausea")

if st.button("Predict Disease"):
    if user_input:
        patient_symptoms = [s.strip() for s in user_input.split(',')]
        patient_symptoms = [correct_spelling(symptom) for symptom in patient_symptoms if correct_spelling(symptom)]
        if patient_symptoms:
            predicted_disease = predicted_value(patient_symptoms)
            dis_des, precs, meds, rec_diet, works = information(predicted_disease)
            
            st.success(f"**Predicted Disease:** {predicted_disease}")
            st.write(f"**Description:** {dis_des}")
            st.write("**Precautions:**", ', '.join(str(item) for item in precs if item and pd.notna(item)))
            st.write("**Medications:**", ', '.join(str(item) for item in meds if item and pd.notna(item)))
            st.write("**Recommended Diet:**", ', '.join(str(item) for item in rec_diet if item and pd.notna(item)))
            st.write("**Recommended Workout:**", ', '.join(str(item) for item in works if item and pd.notna(item)))
        else:
            st.error("Invalid symptoms detected. Please check and try again.")
    else:
        st.warning("Please enter at least one symptom.")

st.markdown("---")

# Disease Recommendations Section
st.markdown("### Search for Disease Description")
disease_query = st.text_input("Type a disease name to get recommendations:", placeholder="Start typing...")

if disease_query:
    q = disease_query.strip().lower()
    matches = [d for d in disease_names if d.lower().startswith(q)]
    if not matches:
        matches = [d for d in disease_names if q in d.lower()]
    if matches:
        selected_disease = matches[0]
        dis_des, precs, meds, rec_diet, works = information(selected_disease)
        st.subheader(f"Recommendations for {selected_disease}")
        st.write(f"**Description:** {dis_des}")
        st.write("**Precautions:**", ', '.join(str(item) for item in precs if item and pd.notna(item)))
        st.write("**Medications:**", ', '.join(str(item) for item in meds if item and pd.notna(item)))
        st.write("**Recommended Diet:**", ', '.join(str(item) for item in rec_diet if item and pd.notna(item)))
        st.write("**Recommended Workout:**", ', '.join(str(item) for item in works if item and pd.notna(item)))
    else:
        st.warning("No matching disease found. Try a different name.")