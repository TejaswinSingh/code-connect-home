from django.contrib import admin

from home.models import SendEmailTask, Task

admin.site.register(Task)
admin.site.register(SendEmailTask)