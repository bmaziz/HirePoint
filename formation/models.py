from django.db import models


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    domaine = models.CharField(max_length=255)
    niveau = models.CharField(max_length=100)
    duree = models.IntegerField(help_text="Durée en heures")
    dateDebut = models.DateField()
    dateFin = models.DateField()
    nombrePlaces = models.IntegerField()
    formateur = models.ForeignKey(
        'formateur.Formateur',
        on_delete=models.CASCADE,
        related_name='formations'
    )

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"

    def __str__(self):
        return f"{self.titre} ({self.domaine})"
