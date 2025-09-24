#!/bin/bash
set -e

echo "🚀 Starting Django application..."

if [ "$USE_POSTGRESQL" = "True" ]; then
    echo "⏳ Waiting for PostgreSQL..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
    echo "✅ PostgreSQL started"
    
    echo "🔍 Checking database connection..."
    python manage.py check --database default
fi

if [ "$USE_REDIS" = "True" ]; then
    echo "⏳ Waiting for Redis..."
    while ! nc -z redis 6379; do
        sleep 0.1
    done
    echo "✅ Redis started"
fi

echo "�� Running migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗃️ Loading initial data..."
python manage.py shell << 'PYTHON_EOF'
from points.models import PointCategory
from django.contrib.auth import get_user_model

if not PointCategory.objects.exists():
    PointCategory.objects.create(
        name='digital_gift',
        ratio=0.60,
        description='Amazonギフト券などのデジタルギフト'
    )
    PointCategory.objects.create(
        name='corporate_product',
        ratio=0.40,
        description='企業オリジナル商品'
    )
    print("✅ Initial point categories created")
else:
    print("ℹ️  Point categories already exist")

User = get_user_model()
admin_count = User.objects.filter(is_admin=True).count()
if admin_count == 0:
    print("⚠️  No admin users found. Create one using:")
    print("   docker-compose exec web python manage.py createsuperuser")
else:
    print(f"ℹ️  {admin_count} admin user(s) exist")
PYTHON_EOF

echo "🎉 Application ready!"

exec "$@"
