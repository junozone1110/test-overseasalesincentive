from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, ProductExchange
from points.models import Point, PointCategory


def is_admin(user):
    """管理者かどうかチェック"""
    return user.is_authenticated and user.is_admin


@login_required
def product_list(request):
    """商品一覧画面"""
    # カテゴリフィルター
    category_filter = request.GET.get('category')
    
    # 商品取得
    products_query = Product.get_available_products()
    
    if category_filter:
        products_query = products_query.filter(category__name=category_filter)
    
    # ページネーション
    paginator = Paginator(products_query, 12)  # 12商品ずつ表示
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # ユーザーのポイント残高
    points_summary = Point.get_user_points_summary(request.user)
    
    # カテゴリ一覧
    categories = PointCategory.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_filter,
        'points_summary': points_summary,
    }
    
    return render(request, 'products/product_list.html', context)


@login_required
def product_detail(request, product_id):
    """商品詳細画面"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # ユーザーのポイント残高
    points_summary = Point.get_user_points_summary(request.user)
    
    # 該当カテゴリのポイント残高
    category_points = points_summary.get(product.category.name, 0)
    
    # 交換可能かチェック
    can_exchange = category_points >= product.required_points
    
    context = {
        'product': product,
        'points_summary': points_summary,
        'category_points': category_points,
        'can_exchange': can_exchange,
    }
    
    return render(request, 'products/product_detail.html', context)


@login_required
@require_POST
def exchange_product(request, product_id):
    """商品交換処理"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    user = request.user
    
    try:
        with transaction.atomic():
            # ユーザーのポイント残高確認
            points_summary = Point.get_user_points_summary(user)
            category_points = points_summary.get(product.category.name, 0)
            
            if category_points < product.required_points:
                messages.error(request, 'ポイントが不足しています。')
                return redirect('product_detail', product_id=product.id)
            
            # ポイント消費（FIFO）
            consumed_points = Point.consume_points(
                user=user,
                category=product.category,
                required_points=product.required_points
            )
            
            # 商品交換履歴作成
            exchange = ProductExchange.objects.create(
                user=user,
                product=product,
                points_used=product.required_points,
                status='pending'
            )
            
            # 取引履歴作成
            try:
                from transactions.models import PointTransaction
                PointTransaction.create_exchange_transaction(
                    user=user,
                    category=product.category,
                    amount=product.required_points,
                    reason=f'商品交換: {product.name}',
                    product_id=product.id,
                    exchange_id=exchange.id
                )
            except ImportError:
                pass  # transactionsアプリがない場合は無視
            
            messages.success(
                request, 
                f'{product.name}の交換申請を受け付けました。管理者による確認後、交換が完了します。'
            )
            
            return redirect('exchange_history')
            
    except ValueError as e:
        messages.error(request, f'交換エラー: {str(e)}')
        return redirect('product_detail', product_id=product.id)
    except Exception as e:
        messages.error(request, 'システムエラーが発生しました。時間をおいて再度お試しください。')
        return redirect('product_detail', product_id=product.id)


@login_required
def exchange_history(request):
    """交換履歴画面"""
    user = request.user
    
    # ステータスフィルター
    status_filter = request.GET.get('status')
    
    exchanges_query = ProductExchange.objects.filter(user=user).select_related('product', 'product__category')
    
    if status_filter:
        exchanges_query = exchanges_query.filter(status=status_filter)
    
    # ページネーション
    paginator = Paginator(exchanges_query, 20)
    page_number = request.GET.get('page')
    exchanges = paginator.get_page(page_number)
    
    # ステータス選択肢
    status_choices = ProductExchange._meta.get_field('status').choices
    
    context = {
        'exchanges': exchanges,
        'status_choices': status_choices,
        'current_status': status_filter,
    }
    
    return render(request, 'products/exchange_history.html', context)


@user_passes_test(is_admin)
def admin_exchange_list(request):
    """管理者用交換一覧"""
    # ステータスフィルター
    status_filter = request.GET.get('status', 'pending')
    
    exchanges_query = ProductExchange.objects.select_related(
        'user', 'product', 'product__category'
    ).order_by('-exchange_date')
    
    if status_filter:
        exchanges_query = exchanges_query.filter(status=status_filter)
    
    # ページネーション
    paginator = Paginator(exchanges_query, 20)
    page_number = request.GET.get('page')
    exchanges = paginator.get_page(page_number)
    
    # ステータス選択肢
    status_choices = ProductExchange._meta.get_field('status').choices
    
    # 統計情報
    stats = {
        'pending': ProductExchange.objects.filter(status='pending').count(),
        'processing': ProductExchange.objects.filter(status='processing').count(),
        'completed': ProductExchange.objects.filter(status='completed').count(),
        'cancelled': ProductExchange.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'exchanges': exchanges,
        'status_choices': status_choices,
        'current_status': status_filter,
        'stats': stats,
    }
    
    return render(request, 'products/admin_exchange_list.html', context)


@user_passes_test(is_admin)
@require_POST
def update_exchange_status(request, exchange_id):
    """交換ステータス更新"""
    exchange = get_object_or_404(ProductExchange, id=exchange_id)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if new_status in dict(ProductExchange._meta.get_field('status').choices):
        exchange.status = new_status
        if notes:
            exchange.notes = notes
        exchange.save()
        
        messages.success(request, f'{exchange.user.full_name}さんの交換ステータスを更新しました。')
    else:
        messages.error(request, '無効なステータスです。')
    
    return redirect('admin_exchange_list')


@require_POST
@login_required
def get_product_info_ajax(request):
    """AJAX: 商品情報取得"""
    product_id = request.POST.get('product_id')
    
    if product_id:
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            points_summary = Point.get_user_points_summary(request.user)
            category_points = points_summary.get(product.category.name, 0)
            
            return JsonResponse({
                'success': True,
                'product': {
                    'name': product.name,
                    'description': product.description,
                    'required_points': product.required_points,
                    'category': product.category.get_name_display(),
                },
                'user_points': category_points,
                'can_exchange': category_points >= product.required_points
            })
        except Product.DoesNotExist:
            pass
    
    return JsonResponse({'success': False})
