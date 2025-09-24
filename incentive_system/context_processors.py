from django.conf import settings


def company_settings(request):
    """
    ホワイトレーベル設定をテンプレートで使用できるようにするコンテキストプロセッサ
    """
    return {
        'COMPANY_SETTINGS': getattr(settings, 'COMPANY_SETTINGS', {})
    }
