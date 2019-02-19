from django.contrib import admin
from .models import Item, ShoppingList

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(Item)
