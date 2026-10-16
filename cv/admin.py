from django.contrib import admin
from .models import CV


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'dateCreation', 'fichier')
    list_filter = ('dateCreation',)
