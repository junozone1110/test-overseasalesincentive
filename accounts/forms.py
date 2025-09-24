from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """ユーザー登録フォーム"""
    email = forms.EmailField(required=True, label='メールアドレス')
    full_name = forms.CharField(max_length=100, required=True, label='氏名')

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    class Meta:
        model = User
        fields = ('full_name', 'email')
        labels = {
            'full_name': '氏名',
            'email': 'メールアドレス',
        }