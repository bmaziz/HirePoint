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
    lieu = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="En ligne",
        help_text="Lieu ou mode en ligne / présentiel"
    )
    objectifs = models.TextField(
        blank=True,
        null=True,
        help_text="Objectifs pédagogiques de la formation"
    )
    prerequis = models.TextField(
        blank=True,
        null=True,
        help_text="Prérequis recommandés"
    )
    formateur = models.ForeignKey(
        'formateur.Formateur',
        on_delete=models.CASCADE,
        related_name='formations'
    )

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['-dateDebut']

    def __str__(self):
        return f"{self.titre} ({self.domaine})"

    @property
    def places_occupees(self):
        return self.inscriptions.filter(statut__in=['CONFIRMEE', 'TERMINEE']).count()

    @property
    def places_restantes(self):
        return max(0, self.nombrePlaces - self.places_occupees)

    @property
    def est_complete(self):
        return self.places_restantes <= 0
