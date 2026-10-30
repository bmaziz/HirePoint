from django.db import models
from user.models import User, Role


class Formateur(User):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    experience = models.CharField(max_length=100, blank=True, null=True, help_text="Années ou niveau d'expérience")
    bio = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.role or self.role == Role.CANDIDAT:
            self.role = Role.FORMATEUR
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.specialite}"
