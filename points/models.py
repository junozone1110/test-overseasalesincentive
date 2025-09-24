from django.db import models
from django.conf import settings
from django.utils import timezone
import calendar
from datetime import datetime, timedelta


class PointCategory(models.Model):
    """ポイントカテゴリ"""
    DIGITAL_GIFT = 'digital_gift'
    CORPORATE_PRODUCT = 'corporate_product'
    
    CATEGORY_CHOICES = [
        (DIGITAL_GIFT, 'デジタルギフト'),
        (CORPORATE_PRODUCT, '企業商品'),
    ]
    
    name = models.CharField('カテゴリ名', max_length=50, choices=CATEGORY_CHOICES, unique=True)
    ratio = models.DecimalField('比率', max_digits=3, decimal_places=2, help_text='0.60 = 60%')
    description = models.TextField('説明', blank=True, null=True)
    is_active = models.BooleanField('有効', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    
    class Meta:
        verbose_name = 'ポイントカテゴリ'
        verbose_name_plural = 'ポイントカテゴリ'
        db_table = 'point_categories'
        
    def __str__(self):
        return self.get_name_display()
    
    @classmethod
    def get_digital_category(cls):
        """デジタルギフトカテゴリを取得"""
        category, created = cls.objects.get_or_create(
            name=cls.DIGITAL_GIFT,
            defaults={'ratio': 0.60, 'description': 'Amazonギフト券など'}
        )
        return category
    
    @classmethod
    def get_corporate_category(cls):
        """企業商品カテゴリを取得"""
        category, created = cls.objects.get_or_create(
            name=cls.CORPORATE_PRODUCT,
            defaults={'ratio': 0.40, 'description': '企業オリジナル商品'}
        )
        return category


class PointManager(models.Manager):
    """ポイントマネージャー"""
    
    def available_points(self, user=None, category=None):
        """利用可能なポイントを取得"""
        queryset = self.filter(
            remaining_amount__gt=0,
            is_expired=False,
            expires_at__gt=timezone.now()
        )
        
        if user:
            queryset = queryset.filter(user=user)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset
    
    def expired_points(self):
        """期限切れのポイントを取得"""
        return self.filter(
            models.Q(expires_at__lte=timezone.now()) | models.Q(is_expired=True)
        )
    
    def expiring_soon(self, days=30):
        """もうすぐ期限切れのポイントを取得"""
        threshold = timezone.now() + timedelta(days=days)
        return self.available_points().filter(expires_at__lte=threshold)


class Point(models.Model):
    """ポイント"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='points'
    )
    category = models.ForeignKey(
        PointCategory,
        on_delete=models.CASCADE,
        verbose_name='カテゴリ'
    )
    amount = models.PositiveIntegerField('付与ポイント数')
    remaining_amount = models.PositiveIntegerField('残りポイント数')
    reason = models.CharField('付与理由', max_length=200)
    issued_at = models.DateTimeField('付与日時', auto_now_add=True)
    expires_at = models.DateTimeField('有効期限')
    is_expired = models.BooleanField('期限切れ', default=False)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    objects = PointManager()
    
    class Meta:
        verbose_name = 'ポイント'
        verbose_name_plural = 'ポイント'
        db_table = 'points'
        ordering = ['expires_at']
        indexes = [
            models.Index(fields=['user', 'category', 'expires_at']),
            models.Index(fields=['expires_at', 'is_expired']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.category} - {self.remaining_amount}pt"
    
    def save(self, *args, **kwargs):
        # 初回保存時に remaining_amount を設定
        if not self.pk:
            self.remaining_amount = self.amount
            # 有効期限が設定されていない場合は自動計算
            if not self.expires_at:
                self.expires_at = self.calculate_expiry_date()
        super().save(*args, **kwargs)
    
    def calculate_expiry_date(self):
        """有効期限を計算（付与から6ヶ月後の月末）"""
        issued_date = self.issued_at or timezone.now()
        
        # 6ヶ月後の月を計算
        expiry_month = issued_date.month + 6
        expiry_year = issued_date.year
        if expiry_month > 12:
            expiry_year += 1
            expiry_month -= 12
        
        # 月末日を取得
        last_day = calendar.monthrange(expiry_year, expiry_month)[1]
        return timezone.make_aware(
            datetime(expiry_year, expiry_month, last_day, 23, 59, 59)
        )
    
    def is_available(self):
        """利用可能かどうか"""
        return (
            self.remaining_amount > 0 
            and not self.is_expired 
            and self.expires_at > timezone.now()
        )
    
    def consume(self, amount):
        """ポイントを消費"""
        if amount > self.remaining_amount:
            raise ValueError('消費ポイント数が残りポイント数を超えています')
        
        self.remaining_amount -= amount
        self.save()
        return amount
    
    @classmethod
    def grant_points(cls, user, total_points, reason, created_by=None):
        """ポイントを付与（6:4の比率で分割）"""
        # デジタルギフトポイント（60%）
        digital_points = int(total_points * 0.6)
        # 企業商品ポイント（40% + 端数）
        corporate_points = total_points - digital_points
        
        digital_category = PointCategory.get_digital_category()
        corporate_category = PointCategory.get_corporate_category()
        
        points_created = []
        
        # デジタルギフトポイント付与
        if digital_points > 0:
            digital_point = cls.objects.create(
                user=user,
                category=digital_category,
                amount=digital_points,
                reason=reason
            )
            points_created.append(digital_point)
            
            # 取引履歴作成
            try:
                from transactions.models import PointTransaction
                PointTransaction.create_grant_transaction(
                    user=user,
                    category=digital_category,
                    amount=digital_points,
                    reason=reason,
                    point_id=digital_point.id,
                    created_by=created_by
                )
            except ImportError:
                pass  # transactionsアプリがない場合は無視
        
        # 企業商品ポイント付与
        if corporate_points > 0:
            corporate_point = cls.objects.create(
                user=user,
                category=corporate_category,
                amount=corporate_points,
                reason=reason
            )
            points_created.append(corporate_point)
            
            # 取引履歴作成
            try:
                from transactions.models import PointTransaction
                PointTransaction.create_grant_transaction(
                    user=user,
                    category=corporate_category,
                    amount=corporate_points,
                    reason=reason,
                    point_id=corporate_point.id,
                    created_by=created_by
                )
            except ImportError:
                pass  # transactionsアプリがない場合は無視
        
        return points_created
    
    @classmethod
    def get_user_points_summary(cls, user):
        """ユーザーのポイント残高を取得"""
        from django.db.models import Sum
        
        # 有効なポイントのみ集計
        valid_points = cls.objects.filter(
            user=user,
            remaining_amount__gt=0,
            is_expired=False,
            expires_at__gt=timezone.now()
        )
        
        summary = valid_points.values('category__name').annotate(
            total_remaining=Sum('remaining_amount')
        )
        
        result = {
            'digital_gift': 0,
            'corporate_product': 0,
            'total': 0
        }
        
        for item in summary:
            category_name = item['category__name']
            total = item['total_remaining'] or 0
            result[category_name] = total
            result['total'] += total
        
        return result
    
    @classmethod
    def consume_points(cls, user, category, required_points):
        """ポイントを消費（FIFO: 有効期限が近い順）"""
        available_points = cls.objects.filter(
            user=user,
            category=category,
            remaining_amount__gt=0,
            is_expired=False,
            expires_at__gt=timezone.now()
        ).order_by('expires_at')
        
        total_available = sum(point.remaining_amount for point in available_points)
        if total_available < required_points:
            raise ValueError('利用可能ポイントが不足しています')
        
        consumed_points = []
        remaining_required = required_points
        
        for point in available_points:
            if remaining_required <= 0:
                break
            
            consume_amount = min(remaining_required, point.remaining_amount)
            point.consume(consume_amount)
            consumed_points.append({
                'point_id': point.id,
                'consumed_amount': consume_amount
            })
            remaining_required -= consume_amount
        
        return consumed_points

