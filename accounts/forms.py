from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    """Registrierung mit E-Mail als Benutzername."""

    email = forms.EmailField(label="E-Mail")
    phone = forms.CharField(label="Telefon (optional)", max_length=30, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        # Reihenfolge: Telefon vor die Passwortfelder
        self.order_fields(["first_name", "last_name", "email", "phone"])

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Zu dieser E-Mail gibt es schon ein Konto.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
            Profile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="E-Mail", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean_username(self):
        return self.cleaned_data["username"].lower()
