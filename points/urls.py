from django.urls import path
from . import views

urlpatterns = [
    # 一般ユーザー用
    path('', views.dashboard, name='dashboard'),
    path('history/', views.point_history, name='point_history'),
    
    # 管理者用
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/grant/', views.grant_points, name='grant_points'),
    path('admin/bulk-grant/', views.bulk_grant_points, name='bulk_grant_points'),
    path('admin/user/<int:user_id>/', views.user_points_detail, name='user_points_detail'),
    
    # AJAX API
    path('api/user-points/', views.get_user_points_ajax, name='get_user_points_ajax'),
]
