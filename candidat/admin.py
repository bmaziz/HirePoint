from django.contrib import admin
from .models import Candidat


@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'telephone', 'adresse')
    search_fields = ('nom', 'prenom', 'telephone')
    filter_horizontal = ('competences',)
