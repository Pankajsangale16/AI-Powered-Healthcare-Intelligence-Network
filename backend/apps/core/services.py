import os
import re
import ast
import logging
import pickle
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import pandas as pd
import numpy as np
from thefuzz import process

logger = logging.getLogger(__name__)

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent

MODELS_DIR = ROOT_DIR / "models"
DATA_DIR = ROOT_DIR / "data"
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"


def normalize_disease_name(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("diseae", "disease")
    return s


class DiseaseService:
    def __init__(self):
        self.symptoms_list: Dict[str, int] = {
            'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3,
            'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8,
            'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12,
            'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16,
            'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20,
            'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24,
            'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28,
            'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32,
            'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36,
            'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40,
            'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44,
            'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48,
            'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51,
            'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55,
            'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58,
            'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61,
            'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65,
            'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69,
            'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72,
            'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75,
            'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78,
            'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82,
            'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85,
            'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88,
            'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91,
            'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94,
            'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98,
            'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101,
            'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104,
            'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108,
            'lack_of_concentration': 109, 'visual_disturbances': 110,
            'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113,
            'stomach_bleeding': 114, 'distention_of_abdomen': 115,
            'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118,
            'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121,
            'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125,
            'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128,
            'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131
        }
        self.diseases_list: Dict[int, str] = {
            15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis',
            14: 'Drug Reaction', 33: 'Peptic ulcer disease', 1: 'AIDS', 12: 'Diabetes',
            17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension', 30: 'Migraine',
            7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice',
            29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
            19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E',
            3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia',
            13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins',
            26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia',
            31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal Positional Vertigo',
            2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'
        }
        self.symptoms_list_processed: Dict[str, int] = {
            symptom.replace('_', ' ').lower(): value
            for symptom, value in self.symptoms_list.items()
        }
        self._load_resources()

    def _load_resources(self):
        logger.info("Loading Disease Prediction models and datasets...")
        dataset_path = DATA_DIR / "Disease-Prediction-and-Medical dataset"
        self.precautions = pd.read_csv(dataset_path / "precautions_df.csv")
        self.workout = pd.read_csv(dataset_path / "workout_df.csv")
        self.description = pd.read_csv(dataset_path / "description.csv")
        self.medications = pd.read_csv(dataset_path / "medications.csv")
        self.diets = pd.read_csv(dataset_path / "diets.csv")

        with open(MODELS_DIR / "first_feature_models" / "RandomForest.pkl", "rb") as f:
            self.model = pickle.load(f)

        for df, col in [
            (self.precautions, "Disease"),
            (self.workout, "disease"),
            (self.description, "Disease"),
            (self.medications, "Disease"),
            (self.diets, "Disease"),
        ]:
            df["norm_disease"] = df[col].apply(normalize_disease_name)

        self.disease_names = sorted(list(self.description["Disease"].unique()))
        logger.info("Disease Prediction resources loaded successfully (%d diseases)", len(self.disease_names))

    def get_symptoms(self) -> List[Dict[str, str]]:
        """Return formatted symptoms for autocomplete."""
        return [
            {
                "id": raw_symptom,
                "label": raw_symptom.replace("_", " ").title(),
                "query_name": clean_name
            }
            for clean_name, idx in sorted(self.symptoms_list_processed.items(), key=lambda x: x[0])
            for raw_symptom, r_idx in self.symptoms_list.items() if r_idx == idx
        ]

    def correct_spelling(self, symptom: str) -> Optional[str]:
        cleaned = symptom.strip().lower()
        if cleaned in self.symptoms_list_processed:
            return cleaned
        closest_match, score = process.extractOne(cleaned, list(self.symptoms_list_processed.keys()))
        return closest_match if score >= 80 else None

    def get_information(self, disease_name: str) -> Dict[str, Any]:
        target_norm = normalize_disease_name(disease_name)

        desc_match = self.description.loc[self.description["norm_disease"] == target_norm]
        disease_description = desc_match["Description"].values[0] if not desc_match.empty else "Description not available"

        prec_match = self.precautions.loc[
            self.precautions["norm_disease"] == target_norm,
            ["Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]
        ]
        precautions_list = [
            str(item).strip() for item in prec_match.values.flatten().tolist()
            if pd.notna(item) and str(item).strip()
        ] if not prec_match.empty else []

        med_match = self.medications.loc[self.medications["norm_disease"] == target_norm]
        medications_list = []
        if not med_match.empty:
            try:
                medications_list = ast.literal_eval(med_match["Medication"].values[0])
            except Exception:
                medications_list = []

        diet_match = self.diets.loc[self.diets["norm_disease"] == target_norm]
        diet_list = []
        if not diet_match.empty:
            try:
                diet_list = ast.literal_eval(diet_match["Diet"].values[0])
            except Exception:
                diet_list = []

        workout_match = self.workout.loc[self.workout["norm_disease"] == target_norm]
        workout_list = [
            str(item).strip() for item in workout_match["workout"].values.tolist()
            if pd.notna(item) and str(item).strip()
        ] if not workout_match.empty else []

        return {
            "disease": disease_name,
            "description": disease_description,
            "precautions": precautions_list,
            "medications": medications_list,
            "diet": diet_list,
            "workout": workout_list,
        }

    def predict(self, raw_symptoms: List[str]) -> Dict[str, Any]:
        cleaned_symptoms = []
        for s in raw_symptoms:
            matched = self.correct_spelling(s)
            if matched and matched not in cleaned_symptoms:
                cleaned_symptoms.append(matched)

        if not cleaned_symptoms:
            return {
                "success": False,
                "error": "No recognizable symptoms found. Please check spelling or select from the list."
            }

        i_vector = np.zeros(len(self.symptoms_list_processed))
        for symptom in cleaned_symptoms:
            if symptom in self.symptoms_list_processed:
                i_vector[self.symptoms_list_processed[symptom]] = 1

        pred_index = self.model.predict([i_vector])[0]
        predicted_disease = self.diseases_list.get(pred_index, "Unknown Disease")

        # Compute top predictions with probabilities for confidence bars
        confidences = []
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba([i_vector])[0]
            top_indices = np.argsort(probs)[::-1][:5]
            for idx in top_indices:
                prob = float(probs[idx])
                if prob > 0:
                    dis_name = self.diseases_list.get(self.model.classes_[idx], "Unknown")
                    confidences.append({
                        "disease": dis_name,
                        "confidence": round(prob * 100, 2)
                    })

        details = self.get_information(predicted_disease)
        return {
            "success": True,
            "matched_symptoms": cleaned_symptoms,
            "predicted_disease": predicted_disease,
            "confidence_scores": confidences,
            **details
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []
        q = query.strip().lower()
        matches = [d for d in self.disease_names if d.lower().startswith(q)]
        if not matches:
            matches = [d for d in self.disease_names if q in d.lower()]

        results = []
        for d in matches[:10]:
            results.append(self.get_information(d))
        return results


class DrugService:
    def __init__(self):
        self._load_resources()

    def _load_resources(self):
        logger.info("Loading Drug Recommendation models and datasets...")
        with open(MODELS_DIR / "second_feature_models" / "medicine_dict.pkl", "rb") as f:
            medicine_dict = pickle.load(f)
        self.medicines = pd.DataFrame(medicine_dict)
        self.similarity = joblib.load(MODELS_DIR / "second_feature_models" / "similarity.joblib")
        self.description_data = pd.read_csv(DATA_DIR / "Drug reccomendation" / "medicine.csv")
        logger.info("Drug Recommendation resources loaded successfully (%d medicines)", len(self.medicines))

    def search_drugs(self, query: str = "", page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        q = (query or "").strip().lower()
        all_drugs = self.medicines["Drug_Name"].values

        if q:
            filtered = [name for name in all_drugs if q in name.lower()]
        else:
            filtered = list(all_drugs)

        total_count = len(filtered)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_drugs = filtered[start_idx:end_idx]

        return {
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if total_count > 0 else 1,
            "results": paginated_drugs
        }

    def recommend(self, medicine_name: str) -> Dict[str, Any]:
        try:
            cleaned = medicine_name.strip().lower()
            match = self.medicines[self.medicines["Drug_Name"].str.lower() == cleaned]
            if match.empty:
                # Fallback to first substring match if exact case-insensitive match isn't found
                contains_match = self.medicines[self.medicines["Drug_Name"].str.lower().str.contains(cleaned, regex=False)]
                if not contains_match.empty:
                    match = contains_match
                else:
                    return {"success": False, "error": f"Medicine '{medicine_name}' not found."}
            medicine_index = match.index[0]
            actual_name = match.iloc[0]["Drug_Name"]
        except (IndexError, KeyError):
            return {"success": False, "error": f"Medicine '{medicine_name}' not found."}

        distances = self.similarity[medicine_index]
        medicines_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]

        recommended_drugs = []
        for i, score in medicines_list:
            d_name = self.medicines.iloc[i]["Drug_Name"]
            desc_match = self.description_data.loc[
                self.description_data["Drug_Name"] == d_name, "Description"
            ]
            d_desc = desc_match.values[0] if not desc_match.empty else ""
            recommended_drugs.append({
                "name": d_name,
                "similarity_percent": round(float(score) * 100, 1),
                "description": d_desc,
                "buy_link": f"https://pharmeasy.in/search/all?name={d_name}"
            })

        # Selected drug description
        main_desc = self.description_data.loc[
            self.description_data["Drug_Name"] == actual_name, "Description"
        ]
        selected_description = main_desc.values[0] if not main_desc.empty else "Description not available."

        return {
            "success": True,
            "medicine": actual_name,
            "description": selected_description,
            "recommendations": recommended_drugs
        }


class HeartService:
    def __init__(self):
        self._load_resources()

    def _load_resources(self):
        logger.info("Loading Heart Disease Risk Assessment models...")
        with open(MODELS_DIR / "third_feature_models" / "best_model.pkl", "rb") as f:
            self.model = pickle.load(f)
        with open(MODELS_DIR / "third_feature_models" / "cbe_encoder.pkl", "rb") as f:
            self.encoder = pickle.load(f)

        # Pre-initialize SHAP TreeExplainer for the LGBMClassifier inside EasyEnsembleClassifier
        import shap
        self.lgbm_model = self.model.estimators_[0].steps[-1][1]
        self.explainer = shap.TreeExplainer(self.lgbm_model)
        logger.info("Heart Disease Risk Assessment models loaded successfully")

    def get_options_schema(self) -> Dict[str, Any]:
        """Provides human-readable labels, raw values, categories, and tooltips for all 22 inputs."""
        return {
            "demographics": [
                {
                    "name": "gender",
                    "label": "Gender",
                    "help": "Select your gender.",
                    "default": "male",
                    "options": [
                        {"value": "male", "label": "Male"},
                        {"value": "female", "label": "Female"},
                        {"value": "nonbinary", "label": "Non-binary / Other"}
                    ]
                },
                {
                    "name": "race",
                    "label": "Race / Ethnicity",
                    "help": "Select your race or ethnic background.",
                    "default": "white_only_non_hispanic",
                    "options": [
                        {"value": "white_only_non_hispanic", "label": "White (non-Hispanic)"},
                        {"value": "black_only_non_hispanic", "label": "Black / African American (non-Hispanic)"},
                        {"value": "asian_only_non_hispanic", "label": "Asian (non-Hispanic)"},
                        {"value": "hispanic", "label": "Hispanic / Latino"},
                        {"value": "american_indian_or_alaskan_native_only_non_hispanic", "label": "American Indian / Alaska Native"},
                        {"value": "native_hawaiian_or_other_pacific_islander_only_non_hispanic", "label": "Native Hawaiian / Pacific Islander"},
                        {"value": "multiracial_non_hispanic", "label": "Multiracial (non-Hispanic)"}
                    ]
                },
                {
                    "name": "age_category",
                    "label": "Age Group",
                    "help": "Select your current age bracket.",
                    "default": "Age_40_to_44",
                    "options": [
                        {"value": "Age_18_to_24", "label": "18 to 24"},
                        {"value": "Age_25_to_29", "label": "25 to 29"},
                        {"value": "Age_30_to_34", "label": "30 to 34"},
                        {"value": "Age_35_to_39", "label": "35 to 39"},
                        {"value": "Age_40_to_44", "label": "40 to 44"},
                        {"value": "Age_45_to_49", "label": "45 to 49"},
                        {"value": "Age_50_to_54", "label": "50 to 54"},
                        {"value": "Age_55_to_59", "label": "55 to 59"},
                        {"value": "Age_60_to_64", "label": "60 to 64"},
                        {"value": "Age_65_to_69", "label": "65 to 69"},
                        {"value": "Age_70_to_74", "label": "70 to 74"},
                        {"value": "Age_75_to_79", "label": "75 to 79"},
                        {"value": "Age_80_or_older", "label": "80 or older"}
                    ]
                }
            ],
            "medical_history": [
                {
                    "name": "general_health",
                    "label": "Overall Health Rating",
                    "help": "How would you rate your general health in day-to-day life?",
                    "default": "excellent",
                    "options": [
                        {"value": "excellent", "label": "Excellent"},
                        {"value": "very_good", "label": "Very Good"},
                        {"value": "good", "label": "Good"},
                        {"value": "fair", "label": "Fair"},
                        {"value": "poor", "label": "Poor"}
                    ]
                },
                {
                    "name": "ever_diagnosed_with_heart_attack",
                    "label": "History of Heart Attack",
                    "help": "A heart attack occurs when blood flow to part of the heart is blocked.",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                },
                {
                    "name": "ever_diagnosed_with_a_stroke",
                    "label": "History of Stroke",
                    "help": "A stroke happens when blood supply to part of the brain is interrupted or reduced.",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                },
                {
                    "name": "ever_told_you_had_diabetes",
                    "label": "Diabetes Diagnosis",
                    "help": "Has a doctor or health professional ever told you that you have diabetes?",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"},
                        {"value": "no_prediabetes", "label": "No, pre-diabetes / borderline"},
                        {"value": "yes_during_pregnancy", "label": "Yes, only during pregnancy"}
                    ]
                },
                {
                    "name": "ever_told_you_have_kidney_disease",
                    "label": "Kidney Disease Diagnosis",
                    "help": "Has a doctor or health professional ever told you that you have kidney disease?",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                },
                {
                    "name": "asthma_Status",
                    "label": "Asthma Status",
                    "help": "Have you ever been diagnosed with asthma?",
                    "default": "never_asthma",
                    "options": [
                        {"value": "never_asthma", "label": "Never had asthma"},
                        {"value": "current_asthma", "label": "Current asthma"},
                        {"value": "former_asthma", "label": "Former asthma"}
                    ]
                },
                {
                    "name": "ever_told_you_had_a_depressive_disorder",
                    "label": "Depressive Disorder",
                    "help": "A medical condition characterized by persistent feelings of sadness and loss of interest.",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                },
                {
                    "name": "BMI",
                    "label": "Body Mass Index (BMI)",
                    "help": "BMI measures body fat based on height and weight.",
                    "default": "normal_weight_bmi_18_5_to_24_9",
                    "options": [
                        {"value": "underweight_bmi_less_than_18_5", "label": "Underweight (< 18.5)"},
                        {"value": "normal_weight_bmi_18_5_to_24_9", "label": "Normal weight (18.5 - 24.9)"},
                        {"value": "overweight_bmi_25_to_29_9", "label": "Overweight (25.0 - 29.9)"},
                        {"value": "obese_bmi_30_or_more", "label": "Obese (30.0 or more)"}
                    ]
                },
                {
                    "name": "physical_health_status",
                    "label": "Physical Illness Days (Past 30 Days)",
                    "help": "How many days in the past 30 days was your physical health not good?",
                    "default": "zero_days_not_good",
                    "options": [
                        {"value": "zero_days_not_good", "label": "0 days"},
                        {"value": "1_to_13_days_not_good", "label": "1 to 13 days"},
                        {"value": "14_plus_days_not_good", "label": "14 or more days"}
                    ]
                },
                {
                    "name": "mental_health_status",
                    "label": "Mental Health Days (Past 30 Days)",
                    "help": "How many days in the past 30 days was your mental health not good?",
                    "default": "zero_days_not_good",
                    "options": [
                        {"value": "zero_days_not_good", "label": "0 days"},
                        {"value": "1_to_13_days_not_good", "label": "1 to 13 days"},
                        {"value": "14_plus_days_not_good", "label": "14 or more days"}
                    ]
                },
                {
                    "name": "difficulty_walking_or_climbing_stairs",
                    "label": "Difficulty Walking / Climbing Stairs",
                    "help": "Do you have serious difficulty walking or climbing stairs?",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                },
                {
                    "name": "health_care_provider",
                    "label": "Primary Health Care Provider",
                    "help": "Do you have one person you think of as your personal doctor or health care provider?",
                    "default": "yes_only_one",
                    "options": [
                        {"value": "yes_only_one", "label": "Yes, only one"},
                        {"value": "more_than_one", "label": "More than one"},
                        {"value": "no", "label": "No"}
                    ]
                },
                {
                    "name": "length_of_time_since_last_routine_checkup",
                    "label": "Last Routine Checkup",
                    "help": "How long has it been since you last visited a doctor for a routine checkup?",
                    "default": "past_year",
                    "options": [
                        {"value": "past_year", "label": "Past year"},
                        {"value": "past_2_years", "label": "Past 2 years"},
                        {"value": "past_5_years", "label": "Past 5 years"},
                        {"value": "5+_years_ago", "label": "5 or more years ago"},
                        {"value": "never", "label": "Never"}
                    ]
                },
                {
                    "name": "could_not_afford_to_see_doctor",
                    "label": "Doctor Unaffordable Due to Cost",
                    "help": "Was there a time in the past 12 months when you needed to see a doctor but could not because of cost?",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                }
            ],
            "lifestyle": [
                {
                    "name": "smoking_status",
                    "label": "Smoking Status",
                    "help": "Select your current tobacco smoking status.",
                    "default": "never_smoked",
                    "options": [
                        {"value": "never_smoked", "label": "Never smoked"},
                        {"value": "former_smoker", "label": "Former smoker"},
                        {"value": "current_smoker_some_days", "label": "Current smoker (some days)"},
                        {"value": "current_smoker_every_day", "label": "Current smoker (every day)"}
                    ]
                },
                {
                    "name": "exercise_status_in_past_30_Days",
                    "label": "Physical Exercise in Past 30 Days",
                    "help": "During the past month, did you participate in any physical activities or exercises?",
                    "default": "yes",
                    "options": [
                        {"value": "yes", "label": "Yes"},
                        {"value": "no", "label": "No"}
                    ]
                },
                {
                    "name": "sleep_category",
                    "label": "Average Nightly Sleep",
                    "help": "On average, how many hours of sleep do you get in a 24-hour period?",
                    "default": "normal_sleep_6_to_8_hours",
                    "options": [
                        {"value": "very_short_sleep_0_to_3_hours", "label": "0 to 3 hours (very short)"},
                        {"value": "short_sleep_4_to_5_hours", "label": "4 to 5 hours (short)"},
                        {"value": "normal_sleep_6_to_8_hours", "label": "6 to 8 hours (normal)"},
                        {"value": "long_sleep_9_to_10_hours", "label": "9 to 10 hours (long)"},
                        {"value": "very_long_sleep_11_or_more_hours", "label": "11+ hours (very long)"}
                    ]
                },
                {
                    "name": "drinks_category",
                    "label": "Alcohol Drinks per Week",
                    "help": "Number of alcoholic beverages consumed in an average week.",
                    "default": "did_not_drink",
                    "options": [
                        {"value": "did_not_drink", "label": "None (did not drink)"},
                        {"value": "very_low_consumption_0.01_to_1_drinks", "label": "0.01 to 1 drink/week"},
                        {"value": "low_consumption_1.01_to_5_drinks", "label": "1.01 to 5 drinks/week"},
                        {"value": "moderate_consumption_5.01_to_10_drinks", "label": "5.01 to 10 drinks/week"},
                        {"value": "high_consumption_10.01_to_20_drinks", "label": "10.01 to 20 drinks/week"},
                        {"value": "very_high_consumption_more_than_20_drinks", "label": "More than 20 drinks/week"}
                    ]
                },
                {
                    "name": "binge_drinking_status",
                    "label": "Binge Drinking in Past 30 Days",
                    "help": "Consuming 5+ drinks (men) or 4+ drinks (women) in about 2 hours.",
                    "default": "no",
                    "options": [
                        {"value": "no", "label": "No"},
                        {"value": "yes", "label": "Yes"}
                    ]
                }
            ]
        }

    def assess_risk(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Runs heart disease assessment identically to the Streamlit code."""
        # Support both model keys and friendly keys
        mapping = {
            "heart_attack": "ever_diagnosed_with_heart_attack",
            "stroke": "ever_diagnosed_with_a_stroke",
            "depressive_disorder": "ever_told_you_had_a_depressive_disorder",
            "kidney_disease": "ever_told_you_have_kidney_disease",
            "diabetes": "ever_told_you_had_diabetes",
            "bmi": "BMI",
            "walking": "difficulty_walking_or_climbing_stairs",
            "physical_health": "physical_health_status",
            "mental_health": "mental_health_status",
            "asthma": "asthma_Status",
            "exercise_status": "exercise_status_in_past_30_Days"
        }

        input_data = {}
        for k, v in raw_input.items():
            target_key = mapping.get(k, k)
            input_data[target_key] = v

        input_df = pd.DataFrame([input_data])
        input_encoded = pd.DataFrame(
            self.encoder.transform(input_df),
            columns=self.encoder.get_feature_names_out()
        )
        expected_features = self.encoder.get_feature_names_out()
        input_encoded = input_encoded.reindex(columns=expected_features, fill_value=0)

        # Risk probability percentage
        risk = float(self.model.predict_proba(input_encoded)[:, 1][0] * 100)

        # SHAP TreeExplainer calculation
        shap_values = self.explainer.shap_values(input_encoded)
        shap_matrix = np.array(shap_values)

        # Handle different dimensions that shap_values may return
        if len(shap_matrix.shape) == 3:  # (2, 1, 22) or (1, 22, 2)
            if shap_matrix.shape[0] == 2:  # [class_0, class_1]
                shap_matrix = shap_matrix[1]  # positive class (1, 22)
            elif shap_matrix.shape[2] == 2:
                shap_matrix = shap_matrix[:, :, 1]
        elif len(shap_matrix.shape) == 1:
            shap_matrix = np.expand_dims(shap_matrix, axis=0)

        feature_importances = np.abs(shap_matrix).mean(axis=0)
        total_importance = feature_importances.sum()

        if total_importance == 0 or np.isnan(total_importance):
            feature_importances = np.ones_like(feature_importances) / len(feature_importances) * 100
        else:
            feature_importances = (feature_importances / total_importance) * 100
        feature_importances = np.round(feature_importances, 2)

        feature_importance_df = pd.DataFrame({
            'Feature': input_encoded.columns,
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)

        # Risk Level
        if risk > 70:
            risk_level = "Very High"
            risk_summary = "Your risk of heart disease is very high."
        elif risk > 40:
            risk_level = "High"
            risk_summary = "Your risk of heart disease is high."
        elif risk > 25:
            risk_level = "Moderate"
            risk_summary = "Your risk of heart disease is moderate."
        else:
            risk_level = "Low"
            risk_summary = "Your risk of heart disease is low."

        recommendations: List[str] = []
        final_features: List[str] = []
        feature_to_recommendation: Dict[str, str] = {}

        feature_name_mapping = {
            'ever_diagnosed_with_heart_attack': 'Heart Attack',
            'general_health': 'General Health',
            'ever_diagnosed_with_a_stroke': 'Stroke',
            'ever_told_you_have_kidney_disease': 'Kidney Disease',
            'ever_told_you_had_diabetes': 'Diabetes',
            'physical_health_status': 'Physical Health',
            'ever_told_you_had_a_depressive_disorder': 'Depression',
            'sleep_category': 'Sleep',
            'age_category': 'Age',
            'length_of_time_since_last_routine_checkup': 'Checkup Time',
            'BMI': 'BMI',
            'smoking_status': 'Smoking',
            'exercise_status_in_past_30_Days': 'Exercise',
            'binge_drinking_status': 'Binge Drinking',
            'drinks_category': 'Alcohol',
            'could_not_afford_to_see_doctor': 'Doctor Access',
            'health_care_provider': 'Healthcare Provider',
            'asthma_Status': 'Asthma',
            'difficulty_walking_or_climbing_stairs': 'Mobility',
            'mental_health_status': 'Mental Health',
        }

        if risk > 25:
            cumulative_importance = 0
            important_features = set()
            for _, row in feature_importance_df.iterrows():
                cumulative_importance += row['Importance']
                important_features.add(row['Feature'])
                if cumulative_importance >= 50:
                    break

            additional_features = [
                ('ever_told_you_had_diabetes', input_data.get('ever_told_you_had_diabetes') == "yes"),
                ('ever_diagnosed_with_heart_attack', input_data.get('ever_diagnosed_with_heart_attack') == "yes"),
                ('ever_told_you_had_a_depressive_disorder', input_data.get('ever_told_you_had_a_depressive_disorder') == "yes"),
                ('ever_diagnosed_with_a_stroke', input_data.get('ever_diagnosed_with_a_stroke') == "yes"),
                ('age_category', input_data.get('age_category') in ["Age_55_to_59", "Age_60_to_64", "Age_65_to_69", "Age_70_to_74", "Age_75_to_79", "Age_80_or_older"]),
                ('general_health', input_data.get('general_health') in ["fair", "poor"]),
                ('BMI', input_data.get('BMI') in ["overweight_bmi_25_to_29_9", "obese_bmi_30_or_more"]),
                ('smoking_status', input_data.get('smoking_status') != "never_smoked"),
                ('exercise_status_in_past_30_Days', input_data.get('exercise_status_in_past_30_Days') == "no"),
                ('binge_drinking_status', input_data.get('binge_drinking_status') == "yes"),
                ('drinks_category', input_data.get('drinks_category') in ["high_consumption_10.01_to_20_drinks", "very_high_consumption_more_than_20_drinks"]),
                ('sleep_category', input_data.get('sleep_category') in ["short_sleep_4_to_5_hours", "very_short_sleep_0_to_3_hours"]),
                ('physical_health_status', input_data.get('physical_health_status') in ["1_to_13_days_not_good", "14_plus_days_not_good"]),
                ('mental_health_status', input_data.get('mental_health_status') in ["1_to_13_days_not_good", "14_plus_days_not_good"]),
                ('asthma_Status', input_data.get('asthma_Status') in ["current_asthma", "former_asthma"]),
                ('difficulty_walking_or_climbing_stairs', input_data.get('difficulty_walking_or_climbing_stairs') == "yes"),
                ('length_of_time_since_last_routine_checkup', input_data.get('length_of_time_since_last_routine_checkup') != "past_year"),
                ('could_not_afford_to_see_doctor', input_data.get('could_not_afford_to_see_doctor') == "yes"),
                ('health_care_provider', input_data.get('health_care_provider') == "no"),
                ('ever_told_you_have_kidney_disease', input_data.get('ever_told_you_have_kidney_disease') == "yes")
            ]

            for feature, condition in additional_features:
                if condition:
                    important_features.add(feature)

            for feature in important_features:
                imp_match = feature_importance_df.loc[feature_importance_df['Feature'] == feature, 'Importance']
                if imp_match.empty:
                    continue
                importance = imp_match.values[0]

                if feature == 'ever_diagnosed_with_heart_attack' and input_data.get('ever_diagnosed_with_heart_attack') == "yes":
                    feature_to_recommendation[feature] = f"History of heart attack contributed {importance:.2f}% to your risk. Regularly visit your cardiologist and adhere to prescribed medications. Monitor any new or worsening symptoms and seek immediate medical attention if needed."
                    final_features.append(feature)
                if feature == 'ever_diagnosed_with_a_stroke' and input_data.get('ever_diagnosed_with_a_stroke') == "yes":
                    feature_to_recommendation[feature] = f"History of stroke contributed {importance:.2f}% to your risk. Follow your neurologist's recommendations and take prescribed medications consistently. Engage in approved physical therapy or exercises to regain strength and mobility."
                    final_features.append(feature)
                if feature == 'age_category' and input_data.get('age_category') in ["Age_55_to_59", "Age_60_to_64", "Age_65_to_69", "Age_70_to_74", "Age_75_to_79", "Age_80_or_older"]:
                    feature_to_recommendation[feature] = f"Age category contributed {importance:.2f}% to your risk. While you cannot change your age, maintaining a healthy lifestyle can mitigate risks associated with aging. Ensure regular check-ups, eat a balanced diet, stay active, and avoid smoking."
                    final_features.append(feature)
                if feature == 'general_health' and input_data.get('general_health') in ["fair", "poor"]:
                    feature_to_recommendation[feature] = f"General health contributed {importance:.2f}% to your risk. Focus on improving your overall health through a balanced diet and regular check-ups."
                    final_features.append(feature)
                if feature == 'ever_told_you_have_kidney_disease' and input_data.get('ever_told_you_have_kidney_disease') == "yes":
                    feature_to_recommendation[feature] = f"Kidney disease contributed {importance:.2f}% to your risk. Regularly monitor your kidney function and follow your doctor's advice to manage your condition. Stay hydrated and maintain a kidney-friendly diet."
                    final_features.append(feature)
                if feature == 'ever_told_you_had_diabetes' and input_data.get('ever_told_you_had_diabetes') == "yes":
                    feature_to_recommendation[feature] = f"Diabetes contributed {importance:.2f}% to your risk. Manage your diabetes through diet, exercise, and medication as prescribed by your doctor."
                    final_features.append(feature)
                if feature == 'smoking_status' and input_data.get('smoking_status') != "never_smoked":
                    feature_to_recommendation[feature] = f"Smoking status contributed {importance:.2f}% to your risk. Quit smoking to significantly reduce your risk of heart disease."
                    final_features.append(feature)
                if feature == 'exercise_status_in_past_30_Days' and input_data.get('exercise_status_in_past_30_Days') == "no":
                    feature_to_recommendation[feature] = f"Lack of exercise contributed {importance:.2f}% to your risk. Engage in regular physical activity to improve your heart health."
                    final_features.append(feature)
                if feature == 'binge_drinking_status' and input_data.get('binge_drinking_status') == "yes":
                    feature_to_recommendation[feature] = f"Binge drinking contributed {importance:.2f}% to your risk. Reducing or eliminating alcohol consumption can significantly lower your risk of heart disease. Consider seeking support for alcohol moderation or cessation if needed."
                    final_features.append(feature)
                if feature == 'drinks_category' and input_data.get('drinks_category') in ["high_consumption_10.01_to_20_drinks", "very_high_consumption_more_than_20_drinks"]:
                    feature_to_recommendation[feature] = f"Alcohol consumption contributed {importance:.2f}% to your risk. Limit alcohol consumption to lower your risk."
                    final_features.append(feature)
                if feature == 'sleep_category' and input_data.get('sleep_category') in ["short_sleep_4_to_5_hours", "very_short_sleep_0_to_3_hours"]:
                    feature_to_recommendation[feature] = f"Sleep category contributed {importance:.2f}% to your risk. Consider aiming for 7-9 hours of quality sleep each night. Adequate sleep is crucial for maintaining heart health."
                    final_features.append(feature)
                if feature == 'physical_health_status' and input_data.get('physical_health_status') in ["1_to_13_days_not_good", "14_plus_days_not_good"]:
                    feature_to_recommendation[feature] = f"Physical health contributed {importance:.2f}% to your risk. Engage in regular physical activity and consult a healthcare provider if you have persistent physical health issues."
                    final_features.append(feature)
                if feature == 'mental_health_status' and input_data.get('mental_health_status') in ["1_to_13_days_not_good", "14_plus_days_not_good"]:
                    feature_to_recommendation[feature] = f"Mental health contributed {importance:.2f}% to your risk. Consider seeking support from a mental health professional and practice stress-reducing activities."
                    final_features.append(feature)
                if feature == 'asthma_Status' and input_data.get('asthma_Status') in ["current_asthma", "former_asthma"]:
                    feature_to_recommendation[feature] = f"Asthma contributed {importance:.2f}% to your risk. Manage your asthma by following your treatment plan, avoiding asthma triggers, and using your medications as prescribed."
                    final_features.append(feature)
                if feature == 'ever_told_you_had_a_depressive_disorder' and input_data.get('ever_told_you_had_a_depressive_disorder') == "yes":
                    feature_to_recommendation[feature] = f"Depressive disorder contributed {importance:.2f}% to your risk. Consider seeking support from a mental health professional, practicing stress-reducing activities, and maintaining a healthy lifestyle to manage depressive symptoms."
                    final_features.append(feature)
                if feature == 'difficulty_walking_or_climbing_stairs' and input_data.get('difficulty_walking_or_climbing_stairs') == "yes":
                    feature_to_recommendation[feature] = f"Difficulty walking or climbing stairs contributed {importance:.2f}% to your risk. Consider consulting with a healthcare provider for appropriate interventions and exercises to improve mobility and strength."
                    final_features.append(feature)
                if feature == 'length_of_time_since_last_routine_checkup' and input_data.get('length_of_time_since_last_routine_checkup') != "past_year":
                    feature_to_recommendation[feature] = f"Time since last routine checkup contributed {importance:.2f}% to your risk. Regular health checkups are important for early detection and management of health conditions. Schedule regular appointments with your healthcare provider to monitor and maintain your heart health."
                    final_features.append(feature)
                if feature == 'could_not_afford_to_see_doctor' and input_data.get('could_not_afford_to_see_doctor') == "yes":
                    feature_to_recommendation[feature] = f"Difficulty affording to see a doctor contributed {importance:.2f}% to your risk. Explore community health services, sliding scale clinics, or health insurance options to ensure you have access to necessary medical care."
                    final_features.append(feature)
                if feature == 'health_care_provider' and input_data.get('health_care_provider') == "no":
                    feature_to_recommendation[feature] = f"Not having a primary health care provider contributed {importance:.2f}% to your risk. Establishing a relationship with a primary care provider can help manage and prevent health issues. Consider finding a primary health care provider to ensure regular check-ups and consistent medical advice."
                    final_features.append(feature)
                if feature == 'BMI' and input_data.get('BMI') in ["overweight_bmi_25_to_29_9", "obese_bmi_30_or_more"]:
                    feature_to_recommendation[feature] = f"BMI contributed {importance:.2f}% to your risk. Maintaining a healthy weight through a balanced diet and regular exercise can help reduce your risk of heart disease. Consider consulting a healthcare provider for personalized advice."
                    final_features.append(feature)

            if final_features:
                sorted_recs = sorted(
                    [(f, feature_to_recommendation[f]) for f in final_features],
                    key=lambda x: feature_importance_df.loc[feature_importance_df['Feature'] == x[0], 'Importance'].values[0],
                    reverse=True
                )
                recommendations = [r[1] for r in sorted_recs]
            else:
                recommendations = [
                    "No specific high-risk lifestyle factors were flagged. Maintain regular medical checkups, balanced diet, and active routine."
                ]
        else:
            recommendations = [
                "Your risk of heart disease is low. Keep up the good work and continue to maintain a healthy lifestyle."
            ]

        # Pie chart / factor breakdown data
        final_features_set = set(final_features)
        pie_data = []
        total_chart_imp = 0.0

        for feat in final_features:
            imp_val = float(feature_importance_df.loc[feature_importance_df['Feature'] == feat, 'Importance'].values[0])
            total_chart_imp += imp_val
            pie_data.append({
                "feature": feature_name_mapping.get(feat, feat),
                "raw_feature": feat,
                "importance": round(imp_val, 2)
            })

        other_factors = max(0.0, round(100.0 - total_chart_imp, 2))
        if other_factors > 0 or not pie_data:
            pie_data.append({
                "feature": "Other Factors",
                "raw_feature": "other_factors",
                "importance": other_factors if pie_data else 100.0
            })

        # All 22 factors with importances
        all_factor_importances = [
            {
                "feature": feat,
                "label": feature_name_mapping.get(feat, feat),
                "importance": round(float(imp), 2)
            }
            for feat, imp in zip(feature_importance_df['Feature'], feature_importance_df['Importance'])
        ]

        return {
            "success": True,
            "risk_score": round(risk, 2),
            "risk_level": risk_level,
            "risk_summary": risk_summary,
            "recommendations": recommendations,
            "pie_chart_data": pie_data,
            "factor_importances": all_factor_importances,
            "disclaimer": "This app is not a replacement for professional medical advice, diagnosis, or treatment. Always consult your doctor or a qualified healthcare provider with any questions you may have regarding your health."
        }


class ChatbotService:
    def __init__(self):
        self.vectorstore = None
        self.llm = None
        self._load_resources()

    def _load_resources(self):
        logger.info("Loading Medibot vector store and LLM configurations...")
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
            embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vectorstore = FAISS.load_local(
                str(VECTORSTORE_DIR / "db_faiss"),
                embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info("Medibot vector store loaded successfully")
        except Exception as e:
            logger.error("Failed to load vector store: %s", e)

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if groq_api_key:
            from langchain_groq import ChatGroq
            groq_model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
            self.llm = ChatGroq(
                temperature=0.3,
                model=groq_model,
                api_key=groq_api_key
            )
            logger.info("ChatGroq LLM initialized with model %s", groq_model)
        else:
            logger.warning("GROQ_API_KEY is not configured.")

    @staticmethod
    def expand_query(question: str) -> str:
        cleaned = " ".join(question.strip().split())
        return (
            f"{cleaned} {cleaned.replace(' ', '')} "
            "symptoms causes diagnosis treatment home care remedies "
            "medication tablets pain relief doctor specialist physiotherapy "
            "when to see a doctor emergency warning signs"
        )

    @staticmethod
    def get_prompt_text() -> str:
        return """You are Medibot, a careful health-education assistant (not a doctor).
The user wants practical help: what the problem may be, what they can do, typical medicines, and which doctor to see.

Use the retrieved context when it is relevant. If the context is a dictionary snippet or is incomplete,
still answer using widely accepted general medical knowledge for common conditions.
Do NOT reply with only "I don't know" for everyday symptoms such as pain, fever, cough, cold, acidity, or infection.

Always include this disclaimer at the top:
"Educational information only — not a diagnosis or a personal prescription. Consult a licensed clinician before taking any medicine."

Write a clear answer with these headings:

1. **What it may be** — likely common causes (2–5), in plain language.
2. **What you can do now** — home care, rest, posture, heat/ice, diet, or first-aid steps.
3. **Typical medicines** — commonly used OTC and prescription *classes or well-known examples* (for example paracetamol, ibuprofen) with usual purpose. Say dose must be confirmed by a doctor/pharmacist. Flag who should avoid them (ulcers, kidney disease, pregnancy, children).
4. **Which doctor to see** — GP vs specialist (orthopedic, neurologist, physiotherapist, gastroenterologist, ENT, dermatologist, emergency, etc.) and when.
5. **See a doctor urgently if** — red-flag symptoms.

Keep the tone helpful and specific. Do not invent rare diagnoses. Do not claim a definite diagnosis.

**Retrieved notes (may be incomplete):**
{context}

**User question:**
{question}
"""

    def generate_response(self, question: str) -> Dict[str, Any]:
        if not self.llm:
            raise ValueError("Chatbot service is not configured with an active GROQ_API_KEY.")

        context_text = ""
        source_docs = []
        if self.vectorstore:
            expanded = self.expand_query(question)
            docs = self.vectorstore.similarity_search(expanded, k=8)
            source_docs = [
                doc.metadata.get("source", "Medical Reference")
                for doc in docs if hasattr(doc, "metadata")
            ]
            context_text = "\n\n".join([doc.page_content for doc in docs])

        prompt = self.get_prompt_text().format(context=context_text, question=question)
        response = self.llm.invoke(prompt)

        sources_unique = list(dict.fromkeys(source_docs))
        return {
            "content": response.content,
            "sources": sources_unique
        }

    def stream_response(self, question: str):
        """Yields chunks of text for SSE streaming."""
        if not self.llm:
            yield "data: {\"error\": \"Chatbot service is not configured with an active GROQ_API_KEY.\"}\n\n"
            return

        context_text = ""
        source_docs = []
        if self.vectorstore:
            expanded = self.expand_query(question)
            docs = self.vectorstore.similarity_search(expanded, k=8)
            source_docs = [
                doc.metadata.get("source", "Medical Reference")
                for doc in docs if hasattr(doc, "metadata")
            ]
            context_text = "\n\n".join([doc.page_content for doc in docs])

        prompt = self.get_prompt_text().format(context=context_text, question=question)
        sources_unique = list(dict.fromkeys(source_docs))

        # Yield sources first or with start
        import json
        yield f"event: meta\ndata: {json.dumps({'sources': sources_unique})}\n\n"

        for chunk in self.llm.stream(prompt):
            content = getattr(chunk, "content", "")
            if content:
                yield f"event: token\ndata: {json.dumps({'token': content})}\n\n"

        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"


# Singleton instances loaded once at startup
class ServiceRegistry:
    _disease_service: Optional[DiseaseService] = None
    _drug_service: Optional[DrugService] = None
    _heart_service: Optional[HeartService] = None
    _chatbot_service: Optional[ChatbotService] = None

    @classmethod
    def get_disease_service(cls) -> DiseaseService:
        if cls._disease_service is None:
            cls._disease_service = DiseaseService()
        return cls._disease_service

    @classmethod
    def get_drug_service(cls) -> DrugService:
        if cls._drug_service is None:
            cls._drug_service = DrugService()
        return cls._drug_service

    @classmethod
    def get_heart_service(cls) -> HeartService:
        if cls._heart_service is None:
            cls._heart_service = HeartService()
        return cls._heart_service

    @classmethod
    def get_chatbot_service(cls) -> ChatbotService:
        if cls._chatbot_service is None:
            cls._chatbot_service = ChatbotService()
        return cls._chatbot_service
