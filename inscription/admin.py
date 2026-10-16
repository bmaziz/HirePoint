from django.contrib import admin
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'formation', 'dateInscription', 'statut')
    list_filter = ('statut', 'dateInscription')
    search_fields = ('candidat__nom', 'candidat__prenom', 'formation__titre')
