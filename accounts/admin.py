from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """カスタムユーザー作成フォーム"""
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name')


class CustomUserChangeForm(UserChangeForm):
    """カスタムユーザー変更フォーム"""
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'is_admin', 'is_active')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """カスタムユーザー管理画面"""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'full_name', 'email', 'is_admin', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_active', 'created_at')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人情報', {'fields': ('full_name', 'email')}),
        ('権限', {'fields': ('is_admin', 'is_active')}),
        ('重要な日付', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2', 'is_admin'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')