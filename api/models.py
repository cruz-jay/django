from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    major = models.CharField(max_length=100)
    campus = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('staff', 'Staff')])
    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Location(models.Model):
    campus = models.CharField(max_length=50)
    building = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.campus} - {self.building} Room {self.room_number}"

class Exam(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()  # Added to track exam time separately
    duration = models.DurationField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    proctored_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proctored_exams')
    capacity = models.IntegerField(default=20)
    current_booked = models.IntegerField(default=0)

    def is_full(self):
        return self.current_booked >= self.capacity

    def __str__(self):
        return f"{self.title} - {self.date}"

class ExamRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_registrations')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('REGISTERED', 'Registered'),
            ('CANCELLED', 'Cancelled')
        ],
        default='REGISTERED'
    )

    class Meta:
        unique_together = ('user', 'exam')

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"