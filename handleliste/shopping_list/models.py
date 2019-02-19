from django.db import models

# Create your models here.

default_shopping_list_ID = 1


class ShoppingList(models.Model):
    title = models.CharField(max_length=100)
    # slug = models.SlugField(default=default_shopping_list_ID)     # for more readable urls, should be set automatically

    def __str__(self):
        return self.title


class Item(models.Model):
    name = models.CharField(max_length=80)
    amount = models.CharField(max_length=20)
    bought = models.BooleanField(default=False)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, default=default_shopping_list_ID)

    def __str__(self):
        return self.name
