from django.db import models


class Diplome(models.Model):
    titre = models.CharField(max_length=255)
    etablissement = models.CharField(max_length=255)
    dateObtention = models.DateField()
    candidat = models.ForeignKey(
        'candidat.Candidat',
        on_delete=models.CASCADE,
        related_name='diplomes'
    )

    class Meta:
        verbose_name = "Diplôme"
        verbose_name_plural = "Diplômes"

    def __str__(self):
        return f"{self.titre} - {self.etablissement} ({self.candidat})"
