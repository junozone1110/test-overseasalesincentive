from django.db import models
from django.conf import settings
from points.models import PointCategory


class TransactionManager(models.Manager):
    """取引履歴マネージャー"""
    
    def for_user(self, user):
        """ユーザーの取引履歴を取得"""
        return self.filter(user=user)
    
    def grants(self):
        """付与取引のみを取得"""
        return self.filter(transaction_type='grant')
    
    def exchanges(self):
        """交換取引のみを取得"""
        return self.filter(transaction_type='exchange')
    
    def by_category(self, category):
        """カテゴリ別の取引履歴を取得"""
        return self.filter(category=category)
    
    def recent(self, days=30):
        """最近の取引履歴を取得"""
        from django.utils import timezone
        from datetime import timedelta
        
        threshold = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=threshold)


class PointTransaction(models.Model):
    """ポイント取引履歴"""
    TRANSACTION_TYPES = [
        ('grant', 'ポイント付与'),
        ('exchange', '商品交換'),
        ('expire', 'ポイント失効'),
        ('adjustment', '調整'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='point_transactions'
    )
    transaction_type = models.CharField('取引種別', max_length=20, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(
        PointCategory,
        on_delete=models.CASCADE,
        verbose_name='カテゴリ'
    )
    amount = models.IntegerField('ポイント数')  # 負の値も許可（消費時）
    balance_after = models.PositiveIntegerField('取引後残高')
    reason = models.CharField('理由・説明', max_length=200)
    
    # 関連オブジェクト（オプション）
    related_point_id = models.PositiveIntegerField('関連ポイントID', null=True, blank=True)
    related_product_id = models.PositiveIntegerField('関連商品ID', null=True, blank=True)
    related_exchange_id = models.PositiveIntegerField('関連交換ID', null=True, blank=True)
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='作成者',
        related_name='created_transactions'
    )
    
    objects = TransactionManager()

    class Meta:
        verbose_name = 'ポイント取引履歴'
        verbose_name_plural = 'ポイント取引履歴'
        db_table = 'point_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['category', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.get_transaction_type_display()} - {self.amount}pt"

    @property
    def is_positive(self):
        """正の取引（付与）かどうか"""
        return self.amount > 0

    @property
    def is_negative(self):
        """負の取引（消費）かどうか"""
        return self.amount < 0

    @classmethod
    def create_grant_transaction(cls, user, category, amount, reason, point_id=None, created_by=None):
        """ポイント付与の取引履歴を作成"""
        from points.models import Point
        
        # 現在の残高を計算
        current_balance = Point.get_user_points_summary(user).get(category.name, 0)
        
        return cls.objects.create(
            user=user,
            transaction_type='grant',
            category=category,
            amount=amount,
            balance_after=current_balance,
            reason=reason,
            related_point_id=point_id,
            created_by=created_by
        )

    @classmethod
    def create_exchange_transaction(cls, user, category, amount, reason, product_id=None, exchange_id=None):
        """商品交換の取引履歴を作成"""
        from points.models import Point
        
        # 現在の残高を計算
        current_balance = Point.get_user_points_summary(user).get(category.name, 0)
        
        return cls.objects.create(
            user=user,
            transaction_type='exchange',
            category=category,
            amount=-amount,  # 消費は負の値
            balance_after=current_balance,
            reason=reason,
            related_product_id=product_id,
            related_exchange_id=exchange_id
        )

    @classmethod
    def create_expire_transaction(cls, user, category, amount, reason, point_id=None):
        """ポイント失効の取引履歴を作成"""
        from points.models import Point
        
        # 現在の残高を計算
        current_balance = Point.get_user_points_summary(user).get(category.name, 0)
        
        return cls.objects.create(
            user=user,
            transaction_type='expire',
            category=category,
            amount=-amount,  # 失効は負の値
            balance_after=current_balance,
            reason=reason,
            related_point_id=point_id
        )

