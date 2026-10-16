from django.db import models


class Experience(models.Model):
    poste = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255)
    description = models.TextField()
    dateDebut = models.DateField()
    dateFin = models.DateField(null=True, blank=True)
    candidat = models.ForeignKey(
        'candidat.Candidat',
        on_delete=models.CASCADE,
        related_name='experiences'
    )

    class Meta:
        verbose_name = "Expérience"
        verbose_name_plural = "Expériences"

    def __str__(self):
        return f"{self.poste} chez {self.entreprise} ({self.candidat})"
