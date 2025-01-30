from django.contrib import admin

from .models import Note
from .models import UserProfile
from .models import Location
from .models import Exam
from .models import ExamRegistration


admin.site.register(Note)
admin.site.register(UserProfile)

admin.site.register(Location)
admin.site.register(Exam)
admin.site.register(ExamRegistration)