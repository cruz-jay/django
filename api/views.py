# views.py
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, NoteSerializer, ExamSerializer, ExamRegistrationSerializer
from .models import Note, Exam, ExamRegistration, UserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile does not exist."}, status=400)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the profile
            serializer.save(profile_completed=True)
            
            # Create new token with profile_completed status
            refresh = RefreshToken.for_user(request.user)
            refresh['profile_completed'] = True
            
            # Log token contents for debugging
            print("Token payload:", refresh.payload)
            
            return Response({
                "message": "Profile updated successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "debug_token_payload": refresh.payload
            })
        return Response(serializer.errors, status=400)

class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'major': profile.major,
                'campus': profile.campus,
                'role': profile.role
            }
            return Response(data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)

class ExamListView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Exam.objects.all()

class ExamRegistrationListView(generics.ListCreateAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamRegistration.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if user has less than 3 registrations
        user_registrations = ExamRegistration.objects.filter(user=self.request.user).count()
        if user_registrations >= 3:
            raise serializers.ValidationError("Maximum of 3 exam registrations allowed")
        serializer.save(user=self.request.user)

class ExamRegistrationDeleteView(generics.DestroyAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamRegistration.objects.filter(user=self.request.user)

class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)

class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]



class FacultyExamListView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only allow faculty to access this
        if self.request.user.profile.role != 'staff':
            return Exam.objects.none()
        return Exam.objects.all()

class FacultyStudentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.profile.role != 'staff':
            return Response({"error": "Not authorized"}, status=403)
            
        students = UserProfile.objects.filter(role='student')
        data = [{
            'id': profile.user.id,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': profile.user.email,
            'major': profile.major,
            'campus': profile.campus
        } for profile in students]
        return Response(data)

class FacultyRegistrationListView(generics.ListAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.profile.role != 'staff':
            return ExamRegistration.objects.none()
            
        # Allow filtering by exam, student, date range
        exam_id = self.request.query_params.get('exam_id')
        student_id = self.request.query_params.get('student_id')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        queryset = ExamRegistration.objects.all()
        
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        if student_id:
            queryset = queryset.filter(user_id=student_id)
        if date_from:
            queryset = queryset.filter(exam__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(exam__date__lte=date_to)
            
        return queryset