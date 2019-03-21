from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


User = get_user_model()
default_shopping_list_ID = 1


class ShoppingList(models.Model):
    title = models.CharField(max_length=25)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='owner')
    participants = models.ManyToManyField(User, related_name='participants')
    admins = models.ManyToManyField(User, related_name='admins')

    def __str__(self):
        return self.title

    # Return the user's shopping lists
    @staticmethod
    def get_user_shopping_lists(user):
        owned_shopping_lists = ShoppingList.objects.filter(owner=user)
        other_shopping_lists = ShoppingList.objects.filter(participants=user)
        other2_shopping_lists = ShoppingList.objects.filter(admins=user)
        my_shopping_lists = other_shopping_lists | owned_shopping_lists | other2_shopping_lists
        return my_shopping_lists.distinct().order_by('id')

    # Check if user is a member of shopping list
    def user_is_member(self, user):
        return user == self.owner or user in self.participants.all() or user in self.admins.all()

    # Check if user has admin rights
    def user_has_admin_rights(self, user):
        return user in self.admins.all() or user == self.owner


class Item(models.Model):
    name = models.CharField(max_length=80)
    amount = models.CharField(max_length=20)
    bought = models.BooleanField(default=False)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, default=default_shopping_list_ID)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, default=1, null=True)

    def __str__(self):
        return self.name
