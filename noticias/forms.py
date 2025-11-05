# noticias/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import authenticate
from .models import UserProfile

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "avatar"]
        widgets = {
            "display_name": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2",
                "placeholder": "Seu nome de exibição"
            }),
            "avatar": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-gray-700"
            }),
        }
        
class UsernameChangeForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Novo usuário",
        validators=[UnicodeUsernameValidator()],
        widget=forms.TextInput(attrs={
            "placeholder": "Novo usuário",
            "class": "w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-red-500"
        })
    )
    current_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Senha atual",
            "class": "w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-red-500"
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        new_username = self.cleaned_data["username"].strip()
        if new_username.lower() == self.user.username.lower():
            raise forms.ValidationError("Esse já é o seu usuário atual.")
        if User.objects.filter(username__iexact=new_username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este usuário já está em uso.")
        return new_username

    def clean_current_password(self):
        pwd = self.cleaned_data["current_password"]
        if not self.user.check_password(pwd):
            raise forms.ValidationError("Senha atual incorreta.")
        return pwd

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.save(update_fields=["username"])
        return self.user
