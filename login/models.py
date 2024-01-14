from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Iot(models.Model):
    code = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code
    
class Plants(models.Model):
    crop = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.crop
    
