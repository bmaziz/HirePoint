from django.contrib import admin
from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('poste', 'entreprise', 'candidat', 'dateDebut', 'dateFin')
    search_fields = ('poste', 'entreprise', 'candidat__nom')
