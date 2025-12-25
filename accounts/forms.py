from django import forms
from django.contrib.auth import get_user_model, authenticate


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use')
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('confirm_password')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('Passwords do not match')

        return cleaned


class LoginForm(forms.Form):
    username_or_email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean(self):
        cleaned = super().clean()
        username_or_email = cleaned.get('username_or_email')
        password = cleaned.get('password')

        if not username_or_email or not password:
            raise forms.ValidationError('Both fields are required')

        User = get_user_model()
        user_obj = User.objects.filter(email=username_or_email).first()
        username = user_obj.username if user_obj else username_or_email

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Invalid username/email or password')

        cleaned['user'] = user
        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match')
        return cleaned
