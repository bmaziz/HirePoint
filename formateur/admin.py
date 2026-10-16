from django.contrib import admin
from .models import Formateur


@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'specialite')
    search_fields = ('nom', 'prenom', 'specialite')
