from django.db import models
from user.models import User, Role


class Candidat(User):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    competences = models.ManyToManyField(
        'competence.Competence',
        related_name='candidats',
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.role:
            self.role = Role.CANDIDAT
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
