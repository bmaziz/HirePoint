from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'message', 'dateCreation', 'lue')
    list_filter = ('lue', 'type', 'dateCreation')
