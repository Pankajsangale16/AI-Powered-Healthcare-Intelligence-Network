from rest_framework import serializers


class DrugSearchSerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        trim_whitespace=True,
        max_length=150
    )
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)


class DrugRecommendSerializer(serializers.Serializer):
    medicine = serializers.CharField(
        required=True,
        trim_whitespace=True,
        min_length=1,
        max_length=200,
        help_text="Name of the medicine to find alternatives for"
    )
