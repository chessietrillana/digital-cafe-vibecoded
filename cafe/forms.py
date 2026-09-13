from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)


class SearchForm(forms.Form):
    q = forms.CharField(required=False)


class SignupForm(UserCreationForm):
    first_name = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name")
