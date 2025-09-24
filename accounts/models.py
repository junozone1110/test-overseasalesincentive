from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """カスタムユーザーモデル"""
    email = models.EmailField('メールアドレス', unique=True)
    full_name = models.CharField('氏名', max_length=100)
    is_admin = models.BooleanField('管理者権限', default=False)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.username})"

    def save(self, *args, **kwargs):
        # is_adminがTrueの場合、is_staffとis_superuserも自動的にTrueに設定
        if self.is_admin:
            super(User, self).__setattr__('is_staff', True)
            super(User, self).__setattr__('is_superuser', True)
        super().save(*args, **kwargs)

    @property
    def is_staff(self):
        """管理者権限があればDjango管理画面にアクセス可能"""
        return self.is_admin or super().is_staff

    @is_staff.setter
    def is_staff(self, value):
        """is_staffの設定"""
        super(User, self).__setattr__('is_staff', value)

    @property
    def is_superuser(self):
        """管理者権限があればスーパーユーザー扱い"""
        return self.is_admin or super().is_superuser

    @is_superuser.setter
    def is_superuser(self, value):
        """is_superuserの設定"""
        super(User, self).__setattr__('is_superuser', value)