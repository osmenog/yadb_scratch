from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.views import APIView

User = get_user_model()


def send_email(*args, **kwargs):
    ...


def get_confirmation_code(*args, **kwargs):
    ...


class PrevSignupSerializer(serializers.ModelSerializer):

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


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        # Перед созданием пользователя, убеждаемся в том, что такого email нет у других пользователей.
        if User.objects.filter(Q(email=email) & ~Q(username=username)).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует'}
            )

        instance, created = User.objects.get_or_create(username=username, defaults={'email': email})

        if instance.email != email:
            raise serializers.ValidationError(
                {'email': 'Вам необходимо указать тот email, который был использован при регистрации!'}
            )

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
