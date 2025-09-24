from django.urls import path
from . import views

urlpatterns = [
    # 一般ユーザー用
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/exchange/', views.exchange_product, name='exchange_product'),
    path('history/', views.exchange_history, name='exchange_history'),
    
    # 管理者用
    path('admin/exchanges/', views.admin_exchange_list, name='admin_exchange_list'),
    path('admin/exchanges/<int:exchange_id>/update/', views.update_exchange_status, name='update_exchange_status'),
    
    # AJAX API
    path('api/product-info/', views.get_product_info_ajax, name='get_product_info_ajax'),
]
