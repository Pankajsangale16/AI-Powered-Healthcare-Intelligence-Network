from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant", "system"], default="user")
    content = serializers.CharField(trim_whitespace=True, max_length=2000)


class ChatRequestSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False,
        trim_whitespace=True,
        max_length=2000,
        help_text="Single prompt string"
    )
    messages = serializers.ListField(
        child=ChatMessageSerializer(),
        required=False,
        help_text="Conversation history array"
    )
    stream = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        query = attrs.get("query")
        messages = attrs.get("messages")

        if not query and not messages:
            raise serializers.ValidationError("Either 'query' or 'messages' must be provided.")

        if not query and messages:
            # Pick last user message as query
            user_messages = [m for m in messages if m.get("role") == "user"]
            if not user_messages:
                raise serializers.ValidationError("No user message found in 'messages' array.")
            attrs["query"] = user_messages[-1]["content"]

        return attrs
