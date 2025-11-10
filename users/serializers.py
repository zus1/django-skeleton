from rest_framework import serializers
from users.enum import Gender
from users.models import User

def validate_confirm_password(data: dict):
    if data["password"] != data["confirm_password"]:
        raise serializers.ValidationError("Passwords don't match")

def validate_email_unique(email: str):
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email already registered")

class RegisterInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[validate_email_unique])
    gender = serializers.ChoiceField(choices=Gender.choices, required=False)
    dob = serializers.DateField(required=True)
    confirm_password = serializers.CharField(required=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = "__all__"


    def create(self, validated_data: dict) -> User:
        validated_data.pop("confirm_password")
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.username = user.email

        user.save()

        return user

    def validate(self, data: dict) -> dict:
        validate_confirm_password(data=data)

        return super().validate(data)

    def validate_email_unique(self, email: str):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")

class RegisterOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data: dict) -> dict:
        validate_confirm_password(data=data)

        user: User = self.context["user"]
        if user.check_password(data["password"]):
            raise serializers.ValidationError("New password can not be same as existing password")

        return super().validate(data)

class LoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'dob']

class MeAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']