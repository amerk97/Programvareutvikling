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


class Item(models.Model):
    name = models.CharField(max_length=80)
    amount = models.CharField(max_length=20)
    bought = models.BooleanField(default=False)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, default=default_shopping_list_ID)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, default=1, null=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=150)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    def replies(self):
        return Reply.objects.filter(parent_comment=self)


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=150)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
