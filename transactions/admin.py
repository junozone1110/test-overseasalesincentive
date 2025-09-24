from django.contrib import admin
from django.utils.html import format_html
from .models import PointTransaction


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """ポイント取引履歴管理画面"""
    list_display = (
        'created_at', 'user', 'get_transaction_type_display', 'category',
        'get_amount_display', 'balance_after', 'reason'
    )
    list_filter = (
        'transaction_type', 'category', 'created_at',
        ('user', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('user__username', 'user__full_name', 'reason')
    ordering = ('-created_at',)
    readonly_fields = (
        'user', 'transaction_type', 'category', 'amount', 'balance_after',
        'reason', 'related_point_id', 'related_product_id', 'related_exchange_id',
        'created_at', 'created_by'
    )
    
    fieldsets = (
        ('取引情報', {
            'fields': ('user', 'transaction_type', 'category', 'amount', 'balance_after', 'reason')
        }),
        ('関連情報', {
            'fields': ('related_point_id', 'related_product_id', 'related_exchange_id'),
            'classes': ('collapse',)
        }),
        ('システム情報', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_amount_display(self, obj):
        """ポイント数の表示"""
        if obj.amount > 0:
            return format_html('<span style="color: green;">+{}</span>', obj.amount)
        else:
            return format_html('<span style="color: red;">{}</span>', obj.amount)
    get_amount_display.short_description = 'ポイント数'
    
    def get_queryset(self, request):
        """クエリセット最適化"""
        return super().get_queryset(request).select_related('user', 'category', 'created_by')
    
    def has_add_permission(self, request):
        """追加権限なし（システムが自動作成）"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """変更権限なし（履歴は変更不可）"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """削除権限なし（履歴は削除不可）"""
        return False
