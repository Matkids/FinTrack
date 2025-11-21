import os
import django
from decimal import Decimal
import random
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from app.models import Category, Transaction, Asset, Investment, Budget

def create_sample_data():
    print("Creating sample data for FinTrack application...")
    
    # Create sample users
    print("Creating sample users...")
    admin_user = User.objects.get(username='admin')
    
    # Create sample categories
    print("Creating sample categories...")
    income_categories = []
    expense_categories = []
    
    income_names = ['Sales Revenue', 'Investment Income', 'Consulting', 'Rental Income', 'Dividends']
    for name in income_names:
        category, created = Category.objects.get_or_create(
            name=name,
            category_type='income',
            defaults={'description': f'Income from {name.lower()}'}
        )
        income_categories.append(category)
        if created:
            print(f"  Created income category: {name}")
    
    expense_names = ['Office Supplies', 'Salaries', 'Rent', 'Utilities', 'Marketing', 'Insurance', 'Travel']
    for name in expense_names:
        category, created = Category.objects.get_or_create(
            name=name,
            category_type='expense',
            defaults={'description': f'Expense for {name.lower()}'}
        )
        expense_categories.append(category)
        if created:
            print(f"  Created expense category: {name}")
    
    # Create sample transactions
    print("Creating sample transactions...")
    for i in range(20):  # Create 20 sample transactions
        if i % 3 == 0:  # Every 3rd transaction is income
            category = random.choice(income_categories)
            amount = Decimal(str(round(random.uniform(1000, 10000), 2)))
            trans_type = 'income'
        else:  # Others are expenses
            category = random.choice(expense_categories)
            amount = Decimal(str(round(random.uniform(100, 2000), 2)))
            trans_type = 'expense'
        
        # Random date within the last 6 months
        days_ago = random.randint(1, 180)
        date = datetime.now() - timedelta(days=days_ago)
        
        transaction = Transaction.objects.create(
            date=date.date(),
            amount=amount,
            type=trans_type,
            category=category,
            description=f'Sample {trans_type} transaction for {category.name}',
            created_by=admin_user
        )
        print(f"  Created {trans_type}: {category.name} - ${amount}")
    
    # Create sample assets
    print("Creating sample assets...")
    asset_types = [
        ('Laptop Computer', 'fixed', 'Equipment', '2023-01-15', 1200.00, 1000.00),
        ('Office Desk', 'fixed', 'Furniture', '2022-06-20', 300.00, 250.00),
        ('Company Vehicle', 'fixed', 'Vehicle', '2021-03-10', 25000.00, 18000.00),
        ('Cash on Hand', 'current', 'Cash', '2023-01-01', 5000.00, 5000.00),
        ('Inventory', 'current', 'Inventory', '2023-01-01', 8000.00, 8000.00),
    ]
    
    for name, asset_type, category, purchase_date, purchase_price, current_value in asset_types:
        asset = Asset.objects.create(
            name=name,
            asset_type=asset_type,
            category=category,
            purchase_date=purchase_date,
            purchase_price=Decimal(str(purchase_price)),
            current_value=Decimal(str(current_value)),
            location='Main Office',
            description=f'{name} asset for business operations'
        )
        print(f"  Created asset: {name} - ${current_value}")
    
    # Create sample investments
    print("Creating sample investments...")
    investment_types = ['stocks', 'bonds', 'real_estate', 'business', 'mutual_funds']
    risk_levels = [1, 2, 3]  # Low, Medium, High
    
    for i in range(5):
        inv_type = random.choice(investment_types)
        risk_level = random.choice(risk_levels)
        
        initial_amount = Decimal(str(round(random.uniform(5000, 50000), 2)))
        # Current value could be higher or lower than initial
        variation = Decimal(str(round(random.uniform(0.8, 1.3), 2)))  # 80% to 130% of initial
        current_value = Decimal(str(round(initial_amount * variation, 2)))
        
        investment = Investment.objects.create(
            name=f'{inv_type.title()} Investment {i+1}',
            investment_type=inv_type,
            initial_amount=initial_amount,
            current_value=current_value,
            purchase_date='2023-01-01',
            expected_roi=random.uniform(5, 15),  # 5% to 15%
            risk_level=risk_level,
            description=f'Investment in {inv_type}'
        )
        print(f"  Created investment: {investment.name} - ${initial_amount} -> ${current_value}")
    
    # Create sample budgets
    print("Creating sample budgets...")
    all_categories = income_categories + expense_categories
    for category in all_categories[:10]:  # Budget for first 10 categories
        budget_amount = Decimal(str(round(random.uniform(1000, 5000), 2)))
        # Simulate some spending (0 to budget amount)
        spent_amount = Decimal(str(round(random.uniform(0, float(budget_amount)), 2)))
        
        budget = Budget.objects.create(
            category=category,
            amount=budget_amount,
            month=datetime.now().month,
            year=datetime.now().year,
            spent_amount=spent_amount
        )
        print(f"  Created budget: {category.name} - ${budget_amount} (spent: ${spent_amount})")
    
    print("\nSample data creation completed successfully!")
    print("You can now log in to the application and see sample data.")
    print("\nLogin credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    create_sample_data()