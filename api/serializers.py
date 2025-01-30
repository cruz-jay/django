# serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, UserProfile, Location, Exam, ExamRegistration
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        try:
            token['profile_completed'] = user.profile.profile_completed
        except:
            token['profile_completed'] = False

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ["major", "campus", "role", "profile_completed", "first_name", "last_name", "email"]

    def update(self, instance, validated_data):
        # Extract user data correctly
        user = instance.user
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Update remaining profile fields
        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "author"]
        extra_kwargs = {"author": {"read_only": True}}

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    current_booked = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'date', 'start_time', 'duration', 'capacity', 'current_booked', 'location']

    def get_current_booked(self, obj):
        return ExamRegistration.objects.filter(exam=obj).count()
class ExamRegistrationSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(), 
        source='exam',
        write_only=True
    )

    class Meta:
        model = ExamRegistration
        fields = ['id', 'exam', 'exam_id', 'registration_date', 'status']
        read_only_fields = ['registration_date', 'status']

    def validate(self, data):
        exam = data['exam']
        user = self.context['request'].user

        # Check if exam is full
        if exam.is_full():
            raise serializers.ValidationError("This exam is full")

        # Check if user is already registered for this exam
        if ExamRegistration.objects.filter(user=user, exam=exam).exists():
            raise serializers.ValidationError("You are already registered for this exam")

        return data