from django.db import models


class Offre(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    localisation = models.CharField(max_length=255)
    typeContrat = models.CharField(max_length=100)
    niveauExperience = models.CharField(max_length=100)
    salaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    datePublication = models.DateField(auto_now_add=True)
    dateExpiration = models.DateField()
    statut = models.CharField(max_length=50, default='ACTIVE')
    entreprise = models.ForeignKey(
        'entreprise.Entreprise',
        on_delete=models.CASCADE,
        related_name='offres'
    )
    competences = models.ManyToManyField(
        'competence.Competence',
        related_name='offres',
        blank=True
    )

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

    def __str__(self):
        return f"{self.titre} - {self.entreprise.nomEntreprise}"
