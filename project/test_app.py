import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import after Django setup
from django.contrib.auth.models import User
from app.models import Transaction, Category, Asset, Investment

def test_create_transaction():
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()

    # Create a test category
    category, created = Category.objects.get_or_create(
        name='Office Supplies',
        category_type='expense'
    )

    # Create a transaction
    transaction = Transaction.objects.create(
        date='2023-01-15',
        amount=Decimal('150.00'),
        type='expense',
        category=category,
        description='Office supplies purchase',
        created_by=user
    )

    assert transaction.amount == Decimal('150.00')
    assert transaction.type == 'expense'
    assert transaction.description == 'Office supplies purchase'

    print("✓ Transaction creation test passed")
    transaction.delete()  # Cleanup


def test_create_asset():
    asset = Asset.objects.create(
        name='Laptop',
        asset_type='fixed',
        category='Equipment',
        purchase_date='2023-01-10',
        purchase_price=Decimal('1200.00'),
        current_value=Decimal('1200.00'),
        location='Office'
    )

    assert asset.name == 'Laptop'
    assert asset.asset_type == 'fixed'
    assert asset.current_book_value() == Decimal('1200.00')

    print("✓ Asset creation test passed")
    asset.delete()  # Cleanup


def test_create_investment():
    investment = Investment.objects.create(
        name='Stock Investment',
        investment_type='stocks',
        initial_amount=Decimal('5000.00'),
        current_value=Decimal('5500.00'),
        purchase_date='2023-01-01',
        expected_roi=10.0,
        risk_level=2
    )

    roi = investment.calculate_roi_percentage()
    profit = investment.calculate_profit_loss()

    assert roi == 10.00
    assert profit == Decimal('500.00')

    print("✓ Investment calculation test passed")
    investment.delete()  # Cleanup


def main():
    print("Running FinTrack application tests...")

    test_create_transaction()
    test_create_asset()
    test_create_investment()

    print("\nAll tests passed! The FinTrack application is working correctly.")

    # Show that superuser exists
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"Superuser account exists: {admin_user.username}")

    print("\nFinTrack application is fully set up and functional!")


if __name__ == '__main__':
    main()