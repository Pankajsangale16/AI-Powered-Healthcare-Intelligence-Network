from rest_framework import serializers

GENDER_CHOICES = ["female", "male", "nonbinary"]

RACE_CHOICES = [
    "white_only_non_hispanic", "black_only_non_hispanic", "asian_only_non_hispanic",
    "american_indian_or_alaskan_native_only_non_hispanic", "multiracial_non_hispanic",
    "hispanic", "native_hawaiian_or_other_pacific_islander_only_non_hispanic"
]

AGE_CHOICES = [
    "Age_18_to_24", "Age_25_to_29", "Age_30_to_34", "Age_35_to_39",
    "Age_40_to_44", "Age_45_to_49", "Age_50_to_54", "Age_55_to_59",
    "Age_60_to_64", "Age_65_to_69", "Age_70_to_74", "Age_75_to_79",
    "Age_80_or_older"
]

GENERAL_HEALTH_CHOICES = ["excellent", "very_good", "good", "fair", "poor"]
YES_NO_CHOICES = ["yes", "no"]
DIABETES_CHOICES = ["yes", "no", "no_prediabetes", "yes_during_pregnancy"]
BMI_CHOICES = [
    "underweight_bmi_less_than_18_5", "normal_weight_bmi_18_5_to_24_9",
    "overweight_bmi_25_to_29_9", "obese_bmi_30_or_more"
]
CHECKUP_CHOICES = ["past_year", "past_2_years", "past_5_years", "5+_years_ago", "never"]
HEALTH_DAYS_CHOICES = ["zero_days_not_good", "1_to_13_days_not_good", "14_plus_days_not_good"]
ASTHMA_CHOICES = ["never_asthma", "current_asthma", "former_asthma"]
PROVIDER_CHOICES = ["yes_only_one", "more_than_one", "no"]
SMOKING_CHOICES = ["never_smoked", "former_smoker", "current_smoker_some_days", "current_smoker_every_day"]
SLEEP_CHOICES = [
    "very_short_sleep_0_to_3_hours", "short_sleep_4_to_5_hours", "normal_sleep_6_to_8_hours",
    "long_sleep_9_to_10_hours", "very_long_sleep_11_or_more_hours"
]
DRINKS_CHOICES = [
    "did_not_drink", "very_low_consumption_0.01_to_1_drinks", "low_consumption_1.01_to_5_drinks",
    "moderate_consumption_5.01_to_10_drinks", "high_consumption_10.01_to_20_drinks",
    "very_high_consumption_more_than_20_drinks"
]


class HeartAssessmentSerializer(serializers.Serializer):
    # Demographics
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    race = serializers.ChoiceField(choices=RACE_CHOICES)
    age_category = serializers.ChoiceField(choices=AGE_CHOICES)

    # Medical History
    general_health = serializers.ChoiceField(choices=GENERAL_HEALTH_CHOICES)
    ever_diagnosed_with_heart_attack = serializers.ChoiceField(choices=YES_NO_CHOICES)
    ever_diagnosed_with_a_stroke = serializers.ChoiceField(choices=YES_NO_CHOICES)
    ever_told_you_had_a_depressive_disorder = serializers.ChoiceField(choices=YES_NO_CHOICES)
    ever_told_you_have_kidney_disease = serializers.ChoiceField(choices=YES_NO_CHOICES)
    ever_told_you_had_diabetes = serializers.ChoiceField(choices=DIABETES_CHOICES)
    BMI = serializers.ChoiceField(choices=BMI_CHOICES)
    difficulty_walking_or_climbing_stairs = serializers.ChoiceField(choices=YES_NO_CHOICES)
    physical_health_status = serializers.ChoiceField(choices=HEALTH_DAYS_CHOICES)
    mental_health_status = serializers.ChoiceField(choices=HEALTH_DAYS_CHOICES)
    asthma_Status = serializers.ChoiceField(choices=ASTHMA_CHOICES)
    health_care_provider = serializers.ChoiceField(choices=PROVIDER_CHOICES)
    length_of_time_since_last_routine_checkup = serializers.ChoiceField(choices=CHECKUP_CHOICES)
    could_not_afford_to_see_doctor = serializers.ChoiceField(choices=YES_NO_CHOICES)

    # Lifestyle
    smoking_status = serializers.ChoiceField(choices=SMOKING_CHOICES)
    exercise_status_in_past_30_Days = serializers.ChoiceField(choices=YES_NO_CHOICES)
    sleep_category = serializers.ChoiceField(choices=SLEEP_CHOICES)
    drinks_category = serializers.ChoiceField(choices=DRINKS_CHOICES)
    binge_drinking_status = serializers.ChoiceField(choices=YES_NO_CHOICES)

    def to_internal_value(self, data):
        """Map alias keys if shorter form is provided, and fill defaults for any missing fields."""
        mutable_data = dict(data)
        alias_map = {
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
            "exercise_status": "exercise_status_in_past_30_Days",
        }
        for short_k, full_k in alias_map.items():
            if short_k in mutable_data and full_k not in mutable_data:
                mutable_data[full_k] = mutable_data[short_k]

        # Clinical baseline defaults for any omitted fields
        defaults = {
            "gender": "female",
            "race": "white_only_non_hispanic",
            "age_category": "Age_40_to_44",
            "general_health": "excellent",
            "ever_diagnosed_with_heart_attack": "no",
            "ever_diagnosed_with_a_stroke": "no",
            "ever_told_you_had_a_depressive_disorder": "no",
            "ever_told_you_have_kidney_disease": "no",
            "ever_told_you_had_diabetes": "no",
            "BMI": "normal_weight_bmi_18_5_to_24_9",
            "difficulty_walking_or_climbing_stairs": "no",
            "physical_health_status": "zero_days_not_good",
            "mental_health_status": "zero_days_not_good",
            "asthma_Status": "never_asthma",
            "health_care_provider": "yes_only_one",
            "length_of_time_since_last_routine_checkup": "past_year",
            "could_not_afford_to_see_doctor": "no",
            "smoking_status": "never_smoked",
            "exercise_status_in_past_30_Days": "yes",
            "sleep_category": "normal_sleep_6_to_8_hours",
            "drinks_category": "did_not_drink",
            "binge_drinking_status": "no",
        }
        for k, v in defaults.items():
            if k not in mutable_data or not mutable_data[k]:
                mutable_data[k] = v

        return super().to_internal_value(mutable_data)
