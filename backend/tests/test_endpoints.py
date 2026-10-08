import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from apps.core.services import ServiceRegistry, normalize_disease_name


@pytest.mark.django_db
class TestHealthEndpoint:
    def test_health_check(self, api_client):
        response = api_client.get('/api/v1/health/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'groq_configured' in data


@pytest.mark.django_db
class TestDiseaseEndpoints:
    @pytest.mark.parametrize("symptoms_input", [
        ['itching', 'skin_rash', 'nodal_skin_eruptions'],
        ['continuous_sneezing', 'shivering', 'chills'],
        ['joint_pain', 'vomiting', 'fatigue', 'high_fever']
    ])
    def test_disease_predict_parity_with_streamlit(self, api_client, symptoms_input):
        service = ServiceRegistry.get_disease_service()

        # Direct Streamlit logic calculation (with correct_spelling)
        cleaned_symptoms = [service.correct_spelling(s) for s in symptoms_input]
        cleaned_symptoms = [s for s in cleaned_symptoms if s]
        i_vec = np.zeros(len(service.symptoms_list_processed))
        for s in cleaned_symptoms:
            if s in service.symptoms_list_processed:
                i_vec[service.symptoms_list_processed[s]] = 1
        expected_idx = service.model.predict([i_vec])[0]
        expected_disease = service.diseases_list.get(expected_idx, "Unknown Disease")

        # API call
        response = api_client.post('/api/v1/disease/predict/', {'symptoms': symptoms_input}, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['predicted_disease'] == expected_disease
        assert 'description' in data
        assert 'precautions' in data
        assert 'medications' in data
        assert 'diet' in data
        assert 'workout' in data
        assert len(data['confidence_scores']) > 0
        assert data['confidence_scores'][0]['disease'] == expected_disease

    def test_disease_symptoms_list(self, api_client):
        response = api_client.get('/api/v1/disease/symptoms/')
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 132
        assert len(data['results']) == 132

    @pytest.mark.parametrize("query", [
        "Fungal infection",
        "Malaria",
        "Diabetes"
    ])
    def test_disease_search_parity(self, api_client, query):
        service = ServiceRegistry.get_disease_service()
        expected = service.get_information(query)

        response = api_client.get(f'/api/v1/disease/search/?q={query}')
        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        first_match = data['results'][0]
        assert first_match['disease'].lower() == query.lower()
        assert first_match['description'] == expected['description']
        assert first_match['precautions'] == expected['precautions']


@pytest.mark.django_db
class TestDrugEndpoints:
    def test_drugs_autocomplete(self, api_client):
        response = api_client.get('/api/v1/drugs/?q=paracetamol&page=1&page_size=10')
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert data['page'] == 1
        assert data['page_size'] == 10
        assert data['count'] > 0
        for name in data['results']:
            assert 'paracetamol' in name.lower()

    @pytest.mark.parametrize("index_pos", [0, 100, 500])
    def test_drug_recommend_parity_with_streamlit(self, api_client, index_pos):
        service = ServiceRegistry.get_drug_service()
        test_drug = service.medicines.iloc[index_pos]['Drug_Name']

        # Original Streamlit logic
        med_idx = service.medicines[service.medicines['Drug_Name'] == test_drug].index[0]
        distances = service.similarity[med_idx]
        sorted_top = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]
        expected_drugs = [service.medicines.iloc[i[0]].Drug_Name for i in sorted_top]

        response = api_client.post('/api/v1/drugs/recommend/', {'medicine': test_drug}, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['medicine'] == test_drug
        actual_rec_names = [r['name'] for r in data['recommendations']]
        assert actual_rec_names == expected_drugs


@pytest.mark.django_db
class TestHeartEndpoints:
    def test_heart_options(self, api_client):
        response = api_client.get('/api/v1/heart/options/')
        assert response.status_code == 200
        data = response.json()
        assert 'demographics' in data
        assert 'medical_history' in data
        assert 'lifestyle' in data
        total_fields = len(data['demographics']) + len(data['medical_history']) + len(data['lifestyle'])
        assert total_fields == 22

    @pytest.mark.parametrize("profile", [
        # Profile 1: Healthy young adult
        {
            'gender': 'male',
            'race': 'white_only_non_hispanic',
            'general_health': 'excellent',
            'health_care_provider': 'yes_only_one',
            'could_not_afford_to_see_doctor': 'no',
            'length_of_time_since_last_routine_checkup': 'past_year',
            'ever_diagnosed_with_heart_attack': 'no',
            'ever_diagnosed_with_a_stroke': 'no',
            'ever_told_you_had_a_depressive_disorder': 'no',
            'ever_told_you_have_kidney_disease': 'no',
            'ever_told_you_had_diabetes': 'no',
            'BMI': 'normal_weight_bmi_18_5_to_24_9',
            'difficulty_walking_or_climbing_stairs': 'no',
            'physical_health_status': 'zero_days_not_good',
            'mental_health_status': 'zero_days_not_good',
            'asthma_Status': 'never_asthma',
            'smoking_status': 'never_smoked',
            'binge_drinking_status': 'no',
            'exercise_status_in_past_30_Days': 'yes',
            'age_category': 'Age_25_to_29',
            'sleep_category': 'normal_sleep_6_to_8_hours',
            'drinks_category': 'did_not_drink'
        },
        # Profile 2: Senior with multiple risk factors
        {
            'gender': 'male',
            'race': 'white_only_non_hispanic',
            'general_health': 'fair',
            'health_care_provider': 'yes_only_one',
            'could_not_afford_to_see_doctor': 'no',
            'length_of_time_since_last_routine_checkup': 'past_year',
            'ever_diagnosed_with_heart_attack': 'yes',
            'ever_diagnosed_with_a_stroke': 'yes',
            'ever_told_you_had_a_depressive_disorder': 'no',
            'ever_told_you_have_kidney_disease': 'yes',
            'ever_told_you_had_diabetes': 'yes',
            'BMI': 'obese_bmi_30_or_more',
            'difficulty_walking_or_climbing_stairs': 'yes',
            'physical_health_status': '14_plus_days_not_good',
            'mental_health_status': 'zero_days_not_good',
            'asthma_Status': 'never_asthma',
            'smoking_status': 'current_smoker_every_day',
            'binge_drinking_status': 'no',
            'exercise_status_in_past_30_Days': 'no',
            'age_category': 'Age_75_to_79',
            'sleep_category': 'short_sleep_4_to_5_hours',
            'drinks_category': 'moderate_consumption_5.01_to_10_drinks'
        },
        # Profile 3: Middle-aged with obesity and high alcohol
        {
            'gender': 'female',
            'race': 'hispanic',
            'general_health': 'poor',
            'health_care_provider': 'no',
            'could_not_afford_to_see_doctor': 'yes',
            'length_of_time_since_last_routine_checkup': '5+_years_ago',
            'ever_diagnosed_with_heart_attack': 'no',
            'ever_diagnosed_with_a_stroke': 'no',
            'ever_told_you_had_a_depressive_disorder': 'yes',
            'ever_told_you_have_kidney_disease': 'no',
            'ever_told_you_had_diabetes': 'yes',
            'BMI': 'obese_bmi_30_or_more',
            'difficulty_walking_or_climbing_stairs': 'yes',
            'physical_health_status': '14_plus_days_not_good',
            'mental_health_status': '14_plus_days_not_good',
            'asthma_Status': 'current_asthma',
            'smoking_status': 'former_smoker',
            'binge_drinking_status': 'yes',
            'exercise_status_in_past_30_Days': 'no',
            'age_category': 'Age_55_to_59',
            'sleep_category': 'very_short_sleep_0_to_3_hours',
            'drinks_category': 'very_high_consumption_more_than_20_drinks'
        }
    ])
    def test_heart_assess_parity_with_streamlit(self, api_client, profile):
        service = ServiceRegistry.get_heart_service()

        # Direct Streamlit function calculation
        input_df = pd.DataFrame([profile])
        input_encoded = pd.DataFrame(service.encoder.transform(input_df), columns=service.encoder.get_feature_names_out())
        expected_features = service.encoder.get_feature_names_out()
        input_encoded = input_encoded.reindex(columns=expected_features, fill_value=0)
        expected_risk = float(service.model.predict_proba(input_encoded)[:, 1][0] * 100)

        response = api_client.post('/api/v1/heart/assess/', profile, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # Verify identical risk calculation rounded to 2 decimals
        assert data['risk_score'] == round(expected_risk, 2)
        assert data['risk_level'] in ['Low', 'Moderate', 'High', 'Very High']
        assert len(data['recommendations']) > 0
        assert len(data['pie_chart_data']) > 0


@pytest.mark.django_db
class TestChatbotEndpoint:
    def test_chat_response_json(self, api_client):
        response = api_client.post('/api/v1/chat/', {'query': 'What are common home remedies for mild fever?'}, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data['role'] == 'assistant'
        assert len(data['content']) > 20
        assert 'sources' in data
