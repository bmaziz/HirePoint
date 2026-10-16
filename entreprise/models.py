from django.db import models
from user.models import User, Role


class Entreprise(User):
    nomEntreprise = models.CharField(max_length=255)
    secteur = models.CharField(max_length=255)
    description = models.TextField()
    adresse = models.CharField(max_length=255)
    siteWeb = models.URLField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.role or self.role == Role.CANDIDAT:
            self.role = Role.ENTREPRISE
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nomEntreprise
