from django.db import models


class StatutCandidature(models.TextChoices):
    EN_ATTENTE = 'EN ATTENTE', 'En attente'
    ACCEPTEE = 'ACCEPTEE', 'Acceptée'
    REFUSEE = 'REFUSEE', 'Refusée'


class Candidature(models.Model):
    lettreMotivation = models.TextField(blank=True, null=True)
    dateCandidature = models.DateField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutCandidature.choices,
        default=StatutCandidature.EN_ATTENTE
    )
    candidat = models.ForeignKey(
        'candidat.Candidat',
        on_delete=models.CASCADE,
        related_name='candidatures'
    )
    offre = models.ForeignKey(
        'offre.Offre',
        on_delete=models.CASCADE,
        related_name='candidatures'
    )

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = ('candidat', 'offre')

    def __str__(self):
        return f"Candidature de {self.candidat} pour {self.offre} [{self.get_statut_display()}]"
