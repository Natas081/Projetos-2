from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class EmailChangeForm(forms.ModelForm):
    current_password = forms.CharField(label="Senha atual", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean_current_password(self):
        pwd = self.cleaned_data["current_password"]
        if not self.user.check_password(pwd):
            raise forms.ValidationError("Senha atual incorreta.")
        return pwd


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "avatar"]
