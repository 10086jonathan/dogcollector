from django.db import models
from django.urls import reverse
from datetime import date

# Create your models here.

class Dog(models.Model):
    name = models.CharField(max_length=250)
    breed = models.CharField(max_length=250)
    description = models.TextField(max_length=250)
    age = models.IntegerField()

    def __str__(self):
        return self.name