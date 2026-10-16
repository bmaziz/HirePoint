from django.contrib import admin
from .models import Formation


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'formateur', 'domaine', 'niveau', 'duree', 'dateDebut', 'dateFin', 'nombrePlaces')
    list_filter = ('domaine', 'niveau')
    search_fields = ('titre', 'domaine')
