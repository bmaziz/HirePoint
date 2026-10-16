from django.db import models


class CV(models.Model):
    fichier = models.FileField(upload_to='cvs/')
    dateCreation = models.DateField(auto_now_add=True)
    candidat = models.OneToOneField(
        'candidat.Candidat',
        on_delete=models.CASCADE,
        related_name='cv'
    )

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"

    def __str__(self):
        return f"CV de {self.candidat}"
