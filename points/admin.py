from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum
from .models import PointCategory, Point


@admin.register(PointCategory)
class PointCategoryAdmin(admin.ModelAdmin):
    """ポイントカテゴリ管理画面"""
    list_display = ('name', 'get_ratio_display', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at',)
    
    def get_ratio_display(self, obj):
        """比率を%表示"""
        return f"{float(obj.ratio) * 100:.0f}%"
    get_ratio_display.short_description = '比率'


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    """ポイント管理画面"""
    list_display = (
        'user', 'category', 'amount', 'remaining_amount', 
        'get_status_display', 'reason', 'issued_at', 'expires_at'
    )
    list_filter = (
        'category', 'is_expired', 'issued_at', 'expires_at',
        ('user', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('user__username', 'user__full_name', 'reason')
    ordering = ('-issued_at',)
    readonly_fields = ('issued_at', 'created_at', 'updated_at', 'calculate_expiry_date')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'category', 'amount', 'remaining_amount', 'reason')
        }),
        ('日時情報', {
            'fields': ('issued_at', 'expires_at', 'is_expired')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display(self, obj):
        """ステータス表示"""
        if obj.is_expired or obj.expires_at <= timezone.now():
            return format_html('<span style="color: red;">期限切れ</span>')
        elif obj.remaining_amount == 0:
            return format_html('<span style="color: gray;">使用済み</span>')
        elif obj.expires_at <= timezone.now() + timezone.timedelta(days=30):
            return format_html('<span style="color: orange;">期限間近</span>')
        else:
            return format_html('<span style="color: green;">有効</span>')
    get_status_display.short_description = 'ステータス'
    
    def get_queryset(self, request):
        """クエリセット最適化"""
        return super().get_queryset(request).select_related('user', 'category')
    
    actions = ['mark_as_expired', 'bulk_grant_points']
    
    def mark_as_expired(self, request, queryset):
        """選択したポイントを期限切れにする"""
        updated = queryset.update(is_expired=True)
        self.message_user(request, f'{updated}件のポイントを期限切れにしました。')
    mark_as_expired.short_description = '選択したポイントを期限切れにする'


# カスタム管理画面の追加
class PointGrantForm(admin.ModelAdmin):
    """ポイント付与専用フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['user', 'total_points', 'reason']


# 管理画面のタイトルカスタマイズ
from django.conf import settings
admin.site.site_header = f'{settings.COMPANY_SETTINGS["SYSTEM_NAME"]} 管理画面'
admin.site.site_title = f'{settings.COMPANY_SETTINGS["SYSTEM_SHORT_NAME"]}管理'
admin.site.index_title = 'システム管理'
