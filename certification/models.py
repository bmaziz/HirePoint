from django.db import models


class Certification(models.Model):
    titre = models.CharField(max_length=255)
    dateObtention = models.DateField()
    fichier = models.FileField(upload_to='certifications/', blank=True, null=True)
    inscription = models.OneToOneField(
        'inscription.Inscription',
        on_delete=models.CASCADE,
        related_name='certification'
    )

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return f"Certification: {self.titre} ({self.inscription.candidat})"
