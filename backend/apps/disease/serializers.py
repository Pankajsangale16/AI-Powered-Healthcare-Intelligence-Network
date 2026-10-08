from rest_framework import serializers


class DiseasePredictSerializer(serializers.Serializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(trim_whitespace=True, max_length=150),
        allow_empty=False,
        help_text="List of symptoms experienced by the patient (e.g. ['headache', 'vomiting'])"
    )

    def validate_symptoms(self, value):
        cleaned = [s.strip() for s in value if s and s.strip()]
        if not cleaned:
            raise serializers.ValidationError("At least one valid symptom must be provided.")
        return cleaned


class DiseaseSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=True,
        trim_whitespace=True,
        min_length=1,
        max_length=100,
        help_text="Search query for disease name"
    )
