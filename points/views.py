from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from datetime import timedelta
from .models import Point, PointCategory
from accounts.models import User


def is_admin(user):
    """管理者かどうかチェック"""
    return user.is_authenticated and user.is_admin


@login_required
def dashboard(request):
    """ダッシュボード画面"""
    user = request.user
    
    # ユーザーのポイント残高を取得
    points_summary = Point.get_user_points_summary(user)
    
    # 最近のポイント履歴（最新10件）
    recent_points = Point.objects.filter(user=user).order_by('-issued_at')[:10]
    
    # 期限間近のポイント（30日以内）
    expiring_points = Point.objects.expiring_soon(days=30).filter(user=user)
    
    context = {
        'points_summary': points_summary,
        'recent_points': recent_points,
        'expiring_points': expiring_points,
        'expiring_count': expiring_points.count(),
    }
    
    return render(request, 'points/dashboard.html', context)


@login_required
def point_history(request):
    """ポイント履歴画面"""
    user = request.user
    
    # フィルタリング
    category_filter = request.GET.get('category')
    transaction_type_filter = request.GET.get('transaction_type')
    
    # 取引履歴を取得
    try:
        from transactions.models import PointTransaction
        transactions_query = PointTransaction.objects.filter(user=user).order_by('-created_at')
        
        if category_filter:
            transactions_query = transactions_query.filter(category__name=category_filter)
        
        if transaction_type_filter:
            transactions_query = transactions_query.filter(transaction_type=transaction_type_filter)
        
        # ページネーション
        paginator = Paginator(transactions_query, 20)
        page_number = request.GET.get('page')
        transactions = paginator.get_page(page_number)
        
    except ImportError:
        # transactionsアプリがない場合は従来の方式
        points_query = Point.objects.filter(user=user).order_by('-issued_at')
        
        if category_filter:
            points_query = points_query.filter(category__name=category_filter)
        
        paginator = Paginator(points_query, 20)
        page_number = request.GET.get('page')
        transactions = paginator.get_page(page_number)
    
    # カテゴリ一覧（フィルタ用）
    categories = PointCategory.objects.filter(is_active=True)
    
    # 取引種別一覧
    transaction_types = [
        ('grant', 'ポイント付与'),
        ('exchange', '商品交換'),
        ('expire', 'ポイント失効'),
        ('adjustment', '調整'),
    ]
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'transaction_types': transaction_types,
        'current_category': category_filter,
        'current_transaction_type': transaction_type_filter,
    }
    
    return render(request, 'points/history.html', context)


@user_passes_test(is_admin)
def admin_dashboard(request):
    """管理者ダッシュボード"""
    # 全体統計
    total_users = User.objects.filter(is_admin=False).count()
    total_points_granted = Point.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_points_remaining = Point.objects.aggregate(Sum('remaining_amount'))['remaining_amount__sum'] or 0
    
    # カテゴリ別統計
    category_stats = Point.objects.values('category__name').annotate(
        total_granted=Sum('amount'),
        total_remaining=Sum('remaining_amount')
    ).order_by('category__name')
    
    # 最近のポイント付与（最新20件）
    recent_grants = Point.objects.order_by('-issued_at')[:20]
    
    context = {
        'total_users': total_users,
        'total_points_granted': total_points_granted,
        'total_points_remaining': total_points_remaining,
        'category_stats': category_stats,
        'recent_grants': recent_grants,
    }
    
    return render(request, 'points/admin_dashboard.html', context)


@user_passes_test(is_admin)
def grant_points(request):
    """ポイント付与画面"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        total_points = int(request.POST.get('total_points', 0))
        reason = request.POST.get('reason', '')
        
        if user_id and total_points > 0 and reason:
            try:
                user = User.objects.get(id=user_id, is_admin=False)
                points_created = Point.grant_points(user, total_points, reason)
                
                messages.success(
                    request, 
                    f'{user.full_name}さんに{total_points}ポイントを付与しました。'
                )
                return redirect('grant_points')
            except User.DoesNotExist:
                messages.error(request, 'ユーザーが見つかりません。')
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
        else:
            messages.error(request, '必要な情報を入力してください。')
    
    # 一般ユーザー一覧
    users = User.objects.filter(is_admin=False).order_by('full_name')
    
    context = {
        'users': users,
    }
    
    return render(request, 'points/grant_points.html', context)


@user_passes_test(is_admin)
def bulk_grant_points(request):
    """一括ポイント付与画面"""
    if request.method == 'POST':
        total_points = int(request.POST.get('total_points', 0))
        reason = request.POST.get('reason', '')
        user_ids = request.POST.getlist('user_ids')
        
        if total_points > 0 and reason and user_ids:
            try:
                users = User.objects.filter(id__in=user_ids, is_admin=False)
                success_count = 0
                
                for user in users:
                    Point.grant_points(user, total_points, reason)
                    success_count += 1
                
                messages.success(
                    request, 
                    f'{success_count}名のユーザーに{total_points}ポイントずつ付与しました。'
                )
                return redirect('bulk_grant_points')
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
        else:
            messages.error(request, '必要な情報を入力してください。')
    
    # 一般ユーザー一覧
    users = User.objects.filter(is_admin=False).order_by('full_name')
    
    context = {
        'users': users,
    }
    
    return render(request, 'points/bulk_grant_points.html', context)


@user_passes_test(is_admin)
def user_points_detail(request, user_id):
    """ユーザー別ポイント詳細"""
    user = get_object_or_404(User, id=user_id, is_admin=False)
    
    # ポイント残高
    points_summary = Point.get_user_points_summary(user)
    
    # ポイント履歴
    points_history = Point.objects.filter(user=user).order_by('-issued_at')
    
    # ページネーション
    paginator = Paginator(points_history, 20)
    page_number = request.GET.get('page')
    points = paginator.get_page(page_number)
    
    context = {
        'target_user': user,
        'points_summary': points_summary,
        'points': points,
    }
    
    return render(request, 'points/user_detail.html', context)


@require_POST
@login_required
def get_user_points_ajax(request):
    """AJAX: ユーザーのポイント残高を取得"""
    user_id = request.POST.get('user_id')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            points_summary = Point.get_user_points_summary(user)
            return JsonResponse({
                'success': True,
                'points_summary': points_summary
            })
        except User.DoesNotExist:
            pass
    
    return JsonResponse({'success': False})
