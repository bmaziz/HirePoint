import uuid
from django.db import models
from django.utils import timezone


class Certification(models.Model):
    titre = models.CharField(max_length=255)
    dateObtention = models.DateField()
    reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Référence unique du certificat"
    )
    fichier = models.FileField(upload_to='certifications/', blank=True, null=True)
    inscription = models.OneToOneField(
        'inscription.Inscription',
        on_delete=models.CASCADE,
        related_name='certification'
    )

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-dateObtention']

    def save(self, *args, **kwargs):
        if not self.reference:
            year = self.dateObtention.year if self.dateObtention else timezone.now().year
            self.reference = f"CERT-{year}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        ref = f" [{self.reference}]" if self.reference else ""
        return f"Certification: {self.titre} ({self.inscription.candidat}){ref}"
