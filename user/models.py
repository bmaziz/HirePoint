from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    CANDIDAT = 'CANDIDAT', 'Candidat'
    ENTREPRISE = 'ENTREPRISE', 'Entreprise'
    FORMATEUR = 'FORMATEUR', 'Formateur'
    ADMINISTRATEUR = 'ADMINISTRATEUR', 'Administrateur'


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDAT
    )
    dateInscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
