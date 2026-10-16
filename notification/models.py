from django.db import models
from django.conf import settings


class Notification(models.Model):
    message = models.TextField()
    type = models.CharField(max_length=50)
    dateCreation = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-dateCreation']

    def __str__(self):
        return f"[{self.type}] Notification pour {self.user.username}: {self.message[:30]}"
