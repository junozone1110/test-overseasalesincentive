from django.db import models
from django.conf import settings
from points.models import PointCategory


class Product(models.Model):
    """商品"""
    category = models.ForeignKey(
        PointCategory,
        on_delete=models.CASCADE,
        verbose_name='カテゴリ'
    )
    name = models.CharField('商品名', max_length=200)
    description = models.TextField('商品説明', blank=True)
    required_points = models.PositiveIntegerField('必要ポイント数')
    image = models.ImageField('商品画像', upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField('販売中', default=True)
    sort_order = models.PositiveIntegerField('表示順', default=0)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        db_table = 'products'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.required_points}pt)"

    @property
    def category_name(self):
        """カテゴリ名を取得"""
        return self.category.get_name_display()

    @classmethod
    def get_available_products(cls, category=None):
        """利用可能な商品を取得"""
        queryset = cls.objects.filter(is_active=True)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('sort_order', 'created_at')


class ProductExchange(models.Model):
    """商品交換履歴"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='ユーザー',
        related_name='product_exchanges'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品'
    )
    points_used = models.PositiveIntegerField('使用ポイント数')
    exchange_date = models.DateTimeField('交換日時', auto_now_add=True)
    status = models.CharField(
        '状態',
        max_length=20,
        choices=[
            ('pending', '交換申請中'),
            ('processing', '処理中'),
            ('completed', '交換完了'),
            ('cancelled', 'キャンセル'),
        ],
        default='pending'
    )
    notes = models.TextField('備考', blank=True)

    class Meta:
        verbose_name = '商品交換履歴'
        verbose_name_plural = '商品交換履歴'
        db_table = 'product_exchanges'
        ordering = ['-exchange_date']

    def __str__(self):
        return f"{self.user.full_name} - {self.product.name} ({self.exchange_date.strftime('%Y/%m/%d')})"