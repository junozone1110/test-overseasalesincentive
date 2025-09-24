from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductExchange


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """商品管理画面"""
    list_display = (
        'name', 'category', 'required_points', 'get_image_preview', 
        'is_active', 'sort_order', 'created_at'
    )
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'category', 'description', 'required_points')
        }),
        ('画像・表示設定', {
            'fields': ('image', 'is_active', 'sort_order')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_image_preview(self, obj):
        """画像プレビュー"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '画像なし'
    get_image_preview.short_description = '画像'
    
    def get_queryset(self, request):
        """クエリセット最適化"""
        return super().get_queryset(request).select_related('category')


@admin.register(ProductExchange)
class ProductExchangeAdmin(admin.ModelAdmin):
    """商品交換履歴管理画面"""
    list_display = (
        'user', 'product', 'points_used', 'get_status_display', 
        'exchange_date'
    )
    list_filter = ('status', 'exchange_date', 'product__category')
    search_fields = ('user__username', 'user__full_name', 'product__name')
    ordering = ('-exchange_date',)
    readonly_fields = ('exchange_date', 'points_used')
    
    fieldsets = (
        ('交換情報', {
            'fields': ('user', 'product', 'points_used', 'exchange_date')
        }),
        ('状態管理', {
            'fields': ('status', 'notes')
        }),
    )
    
    def get_status_display(self, obj):
        """ステータス表示"""
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'cancelled': 'red',
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display.short_description = '状態'
    
    def get_queryset(self, request):
        """クエリセット最適化"""
        return super().get_queryset(request).select_related('user', 'product', 'product__category')
    
    actions = ['mark_as_completed', 'mark_as_processing']
    
    def mark_as_completed(self, request, queryset):
        """選択した交換を完了にする"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated}件の交換を完了にしました。')
    mark_as_completed.short_description = '選択した交換を完了にする'
    
    def mark_as_processing(self, request, queryset):
        """選択した交換を処理中にする"""
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated}件の交換を処理中にしました。')
    mark_as_processing.short_description = '選択した交換を処理中にする'
