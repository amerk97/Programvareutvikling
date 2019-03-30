from django.contrib import admin
from .models import Item, ShoppingList, Comment, Reply

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(Item)
admin.site.register(Comment)
admin.site.register(Reply)
