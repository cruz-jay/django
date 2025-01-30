# api/urls
from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list"),
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="delete-note"),
    path("complete-profile/", views.CompleteProfileView.as_view(), name="complete-profile"),
    path('user-profile/', views.GetUserProfileView.as_view(), name='get-user-profile'),
    path('exams/', views.ExamListView.as_view(), name='exam-list'),
    path('exam-registrations/', views.ExamRegistrationListView.as_view(), name='exam-registration-list'),
    path('exam-registrations/<int:pk>/', views.ExamRegistrationDeleteView.as_view(), name='exam-registration-delete'),
    path('faculty/exams/', views.FacultyExamListView.as_view(), name='faculty-exams'),
    path('faculty/students/', views.FacultyStudentListView.as_view(), name='faculty-students'),
    path('faculty/registrations/', views.FacultyRegistrationListView.as_view(), name='faculty-registrations'),
]
