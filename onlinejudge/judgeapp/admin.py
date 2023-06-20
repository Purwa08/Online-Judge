from django.contrib import admin

# Register your models here.

from .models import User

admin.site.register(User)

from .models import Problem

admin.site.register(Problem)

from .models import Submission

admin.site.register(Submission)

from .models import TestCase

admin.site.register(TestCase)

from .models import Result

admin.site.register(Result)