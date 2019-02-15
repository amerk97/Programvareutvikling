from django.db import models


class CreateNewList(models.Model):                  # this is not working yet, connects to views.py
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

