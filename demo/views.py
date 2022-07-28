from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.views import APIView


def send_email(*args, **kwargs):
    ...


def get_confirmation_code(*args, **kwargs):
    ...


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message="AAAA"
            )
        ]
        extra_kwargs = {
            'username': {'validators': []},
        }

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' запрещено, используйте другое."
            )
        return username


class ALTSignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        instance, created = User.objects.get_or_create(username=username, email=email)
        return instance

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' запрещено, используйте другое."
            )
        return username


class SignupView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = get_confirmation_code()
        user = serializer.save()
        send_email(user.username, user.email, confirmation_code)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)