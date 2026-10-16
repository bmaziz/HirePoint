from django.contrib import admin
from .models import Entreprise


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('nomEntreprise', 'secteur', 'adresse', 'siteWeb')
    search_fields = ('nomEntreprise', 'secteur')
