from django.db import models
from django.contrib.auth.models import User
from predictions.models import tgUser
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_pro = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username