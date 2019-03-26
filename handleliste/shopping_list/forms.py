from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

class ItemForm(forms.Form):
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter name of item',
            }
        )
    )
    amount = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter amount of item',
            }
        )
    )


class ShoppingListForm(forms.Form):
    title = forms.CharField(
        max_length=13,
        widget=forms.TextInput(
            attrs={
                'color': 'red',
                'placeholder': 'Enter title of new list'
            }
        )
    )


class ShareForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter username'
            }
        )
    )

    def clean_username(self, *args, **kwargs):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count() == 0:
            raise forms.ValidationError('User does not exist. Please enter the username of an existing user.')
        return username


class CommentForm(forms.Form):
    content = forms.TextField(widget=forms.Textarea, max_length=150)


class ReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=150)
