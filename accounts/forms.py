from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile, TokenTransaction, AvailableToken


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'name', 'probability']


class TokenTransactionForm(forms.ModelForm):
    class Meta:
        model = TokenTransaction
        fields = ['username', 'session', 'token_amount',
                  'is_token_purchased', 'is_token_granted']
