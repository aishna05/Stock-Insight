from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)
    metrics = models.JSONField()
    plot1 = models.FilePathField(path="media/", null=True, blank=True)
    plot2 = models.FilePathField(path="media/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} @ {self.created_at.date()}"