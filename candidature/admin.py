from django.contrib import admin
from .models import Candidature


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'offre', 'statut', 'dateCandidature')
    list_filter = ('statut', 'dateCandidature')
    search_fields = ('candidat__nom', 'candidat__prenom', 'offre__titre')
