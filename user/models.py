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

    @property
    def is_candidat(self):
        return self.role == Role.CANDIDAT

    @property
    def is_entreprise(self):
        return self.role == Role.ENTREPRISE

    @property
    def is_formateur(self):
        return self.role == Role.FORMATEUR

    @property
    def is_admin(self):
        return self.role == Role.ADMINISTRATEUR or self.is_superuser or self.is_staff

    @property
    def display_name(self):
        if self.is_entreprise and hasattr(self, 'entreprise'):
            return self.entreprise.nomEntreprise
        if self.is_candidat and hasattr(self, 'candidat'):
            prenom = getattr(self.candidat, 'prenom', '')
            nom = getattr(self.candidat, 'nom', '')
            if prenom or nom:
                return f"{prenom} {nom}".strip()
        if self.is_formateur and hasattr(self, 'formateur'):
            prenom = getattr(self.formateur, 'prenom', '')
            nom = getattr(self.formateur, 'nom', '')
            if prenom or nom:
                return f"{prenom} {nom}".strip()
        full = self.get_full_name()
        return full if full else self.username

    @property
    def profile_object(self):
        if self.is_candidat and hasattr(self, 'candidat'):
            return self.candidat
        if self.is_entreprise and hasattr(self, 'entreprise'):
            return self.entreprise
        if self.is_formateur and hasattr(self, 'formateur'):
            return self.formateur
        return self

