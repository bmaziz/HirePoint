from django.contrib import admin
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'entreprise', 'localisation', 'typeContrat', 'salaire', 'datePublication', 'statut')
    list_filter = ('typeContrat', 'statut', 'localisation')
    search_fields = ('titre', 'description', 'entreprise__nomEntreprise')
    filter_horizontal = ('competences',)
