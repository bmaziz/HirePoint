from django.contrib import admin
from .models import Diplome


@admin.register(Diplome)
class DiplomeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etablissement', 'dateObtention', 'candidat')
    search_fields = ('titre', 'etablissement')
