from django.db import models


class Inscription(models.Model):
    dateInscription = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default='EN ATTENTE')
    candidat = models.ForeignKey(
        'candidat.Candidat',
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    formation = models.ForeignKey(
        'formation.Formation',
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('candidat', 'formation')

    def __str__(self):
        return f"Inscription de {self.candidat} à {self.formation} ({self.statut})"
