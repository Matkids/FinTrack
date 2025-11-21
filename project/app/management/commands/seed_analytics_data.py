from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta, date
from app.models import (
    Category, Transaction, Asset, Investment, Budget, 
    CompanyInfo, UserProfile
)
from analytics.models import (
    FinancialForecast, AnomalyDetection, Recommendation, 
    PredictiveModel, ScenarioAnalysis
)
import random


class Command(BaseCommand):
    help = 'Create fresh seed data for all analytics features'

    def handle(self, *args, **options):
        self.stdout.write('Creating fresh seed data for FinTrack...')
        
        # Create a superuser
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fintack.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('adminpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
        
        # Create company info
        company_info, created = CompanyInfo.objects.get_or_create(
            company_name='FinTrack Solutions Inc.',
            defaults={
                'company_address': '123 Financial St, Business District, NY 10001',
                'fiscal_year_start': timezone.now().date(),
                'currency': 'USD',
                'timezone': 'UTC'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created company info'))
        
        # Create user profile
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'super_admin',
                'department': 'Finance',
                'phone_number': '+1234567890'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created user profile'))
        
        # Create categories
        categories_data = [
            ('Sales Revenue', 'income'),
            ('Investment Income', 'income'),
            ('Loan Interest', 'income'),
            ('Rent', 'expense'),
            ('Salaries', 'expense'),
            ('Office Supplies', 'expense'),
            ('Utilities', 'expense'),
            ('Marketing', 'expense'),
            ('Insurance', 'expense'),
            ('Equipment Purchase', 'expense'),
            ('Travel', 'expense'),
            ('Professional Services', 'expense'),
            ('Software Licenses', 'expense'),
            ('Taxes', 'expense'),
        ]
        
        categories = []
        for name, cat_type in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                category_type=cat_type,
                defaults={'description': f'{name} category'}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')
        
        # Create 12 months of transaction data
        start_month = timezone.now().date() - timedelta(days=365)  # 1 year ago
        for month_offset in range(12):
            month_date = start_month + timedelta(days=30*month_offset)

            # Generate income transactions
            for day in range(1, 28, 7):  # Every week
                trans_date = month_date.replace(day=min(day, 28))  # Ensure valid date

                # Create income transactions
                Transaction.objects.create(
                    date=trans_date,
                    amount=Decimal(str(random.uniform(10000, 15000))),
                    type='income',
                    category=random.choice([cat for cat in categories if cat.category_type == 'income'] or [categories[0]]),
                    description=f'Weekly income from {random.choice(["Client A", "Client B", "Client C"])}',
                    created_by=user
                )

            # Create expense transactions
            for day in range(5, 28, 5):  # Every 5 days
                trans_date = month_date.replace(day=min(day, 28))  # Ensure valid date

                # Create expense transactions
                Transaction.objects.create(
                    date=trans_date,
                    amount=Decimal(str(random.uniform(2000, 8000))),
                    type='expense',
                    category=random.choice([cat for cat in categories if cat.category_type == 'expense'] or [categories[0]]),
                    description=f'Expense for {random.choice(["Office", "Marketing", "Operations", "Supplies"])}',
                    created_by=user
                )
        
        self.stdout.write(self.style.SUCCESS('Created 12 months of transaction data'))
        
        # Create assets
        asset_types = ['fixed', 'current']
        asset_categories = ['Equipment', 'Vehicle', 'Building', 'Inventory', 'Cash']
        
        for i in range(10):
            Asset.objects.create(
                name=f'Asset {i+1}',
                asset_type=random.choice(asset_types),
                category=random.choice(asset_categories),
                purchase_date=timezone.now().date() - timedelta(days=random.randint(30, 730)),  # 1-2 years ago
                purchase_price=Decimal(str(random.uniform(5000, 50000))),
                current_value=Decimal(str(random.uniform(1000, 45000))),
                depreciation_rate=Decimal(str(random.uniform(5, 20))),  # 5-20% annual
                depreciation_method='straight_line',
                useful_life_years=random.randint(3, 10),
                location=f'Location {i+1}',
                description=f'Description for asset {i+1}',
                created_by=user,
                # Add analytics fields
                predicted_maintenance_date=timezone.now().date() + timedelta(days=random.randint(30, 180)),
                maintenance_cost_forecast=Decimal(str(random.uniform(500, 2000)))
            )
        
        self.stdout.write(self.style.SUCCESS('Created asset data'))
        
        # Create investments
        investment_types = ['stocks', 'bonds', 'real_estate', 'business', 'mutual_funds']
        
        for i in range(5):
            purchase_date = timezone.now().date() - timedelta(days=random.randint(30, 365))
            initial_amount = Decimal(str(random.uniform(10000, 100000)))
            current_value = initial_amount * Decimal(str(random.uniform(0.9, 1.3)))  # 90-130% of initial
            
            Investment.objects.create(
                name=f'Investment {i+1}',
                investment_type=random.choice(investment_types),
                initial_amount=initial_amount,
                current_value=current_value,
                purchase_date=purchase_date,
                expected_roi=Decimal(str(random.uniform(5, 15))),
                actual_roi=Decimal(str(((current_value/initial_amount - 1) * 100).quantize(Decimal('0.01')))),
                risk_level=random.randint(1, 3),
                description=f'Description for investment {i+1}',
                created_by=user,
                # Add analytics fields
                predicted_roi=Decimal(str(random.uniform(5, 15))),
                predicted_value_12m=current_value * Decimal(str(random.uniform(1.05, 1.15))),
                risk_assessment_updated=timezone.now()
            )
        
        self.stdout.write(self.style.SUCCESS('Created investment data'))
        
        # Create budgets for the current year
        for month in range(1, 13):
            for category in [cat for cat in categories if cat.category_type == 'expense']:  # Only create budgets for expenses
                amount = Decimal(str(random.uniform(2000, 8000)))
                month_start = date(timezone.now().year, month, 1)
                
                # Calculate spent amount based on transactions in this category for this month
                spent = Transaction.objects.filter(
                    type='expense',
                    category=category,
                    date__month=month,
                    date__year=timezone.now().year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                Budget.objects.create(
                    category=category,
                    amount=amount,
                    month=month,
                    year=timezone.now().year,
                    spent_amount=spent,
                    created_by=user
                )
        
        self.stdout.write(self.style.SUCCESS('Created budget data'))
        
        # Create predictive models
        PredictiveModel.objects.create(
            model_name='Cash Flow Forecast Model',
            model_type='cash_flow_forecast',
            version='1.0',
            description='Linear regression model for cash flow forecasting',
            training_data_start=start_month,
            training_data_end=timezone.now().date(),
            accuracy_score=Decimal('0.85'),
            feature_columns=['month_number', 'trend'],
            algorithm_used='LinearRegression'
        )
        
        PredictiveModel.objects.create(
            model_name='Expense Anomaly Detection Model',
            model_type='expense_anomaly',
            version='1.0',
            description='Isolation Forest model for detecting unusual expenses',
            training_data_start=start_month,
            training_data_end=timezone.now().date(),
            accuracy_score=Decimal('0.78'),
            feature_columns=['amount', 'frequency'],
            algorithm_used='IsolationForest'
        )
        
        self.stdout.write(self.style.SUCCESS('Created predictive models'))
        
        # Create some financial forecasts
        for i in range(6):
            future_date = (timezone.now().date().replace(day=1) + timedelta(days=32*(i+1))).replace(day=1)
            predicted_value = Decimal(str(random.uniform(20000, 50000)))
            
            FinancialForecast.objects.create(
                forecast_type='cash_flow',
                predicted_value=predicted_value,
                prediction_date=future_date,
                generated_by=user,
                model_used='Linear Regression',
                training_period_start=start_month,
                training_period_end=timezone.now().date(),
                notes=f'Cash flow forecast for month {i+1}'
            )
        
        self.stdout.write(self.style.SUCCESS('Created financial forecasts'))
        
        # Create scenario analyses
        ScenarioAnalysis.objects.create(
            name='Revenue Growth Scenario',
            scenario_type='revenue_change',
            description='Analysis of revenue growth impact',
            input_parameters={'change_percentage': 10.0, 'period_months': 12},
            predicted_outcomes={
                'initial_value': 100000,
                'projected_value': 110000,
                'change_percentage': 10.0
            },
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=12
        )
        
        ScenarioAnalysis.objects.create(
            name='Cost Reduction Scenario',
            scenario_type='expense_reduction',
            description='Analysis of expense reduction impact',
            input_parameters={'reduction_percentage': 5.0, 'period_months': 12},
            predicted_outcomes={
                'initial_value': 50000,
                'projected_savings': 30000,
                'reduction_percentage': 5.0
            },
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=12
        )
        
        self.stdout.write(self.style.SUCCESS('Created scenario analyses'))
        
        # Create recommendations
        recommendation_data = [
            {
                'type': 'expense_optimization',
                'title': 'Reduce marketing expenses by 15%',
                'description': 'Analysis shows marketing expenses are 25% above industry average',
                'action': 'Review and optimize marketing spend allocation',
                'impact': 3000.00
            },
            {
                'type': 'investment_opportunity',
                'title': 'Increase investment allocation to 35%',
                'description': 'Your portfolio represents only 25% of assets, consider diversifying',
                'action': 'Allocate 35-40% of total assets to investments',
                'impact': 12000.00
            },
            {
                'type': 'budget_adjustment',
                'title': 'Increase IT budget by 20%',
                'description': 'IT category utilization is at 95%, consider increasing budget',
                'action': 'Raise IT budget to accommodate growing needs',
                'impact': 1500.00
            }
        ]
        
        for rec_data in recommendation_data:
            Recommendation.objects.create(
                recommendation_type=rec_data['type'],
                title=rec_data['title'],
                description=rec_data['description'],
                suggested_action=rec_data['action'],
                impact_estimate=Decimal(str(rec_data['impact'])),
                confidence_score=Decimal(str(random.uniform(0.7, 0.95))),
                generated_by=user
            )
        
        self.stdout.write(self.style.SUCCESS('Created recommendations'))
        
        # Create anomaly detections
        expense_transactions = Transaction.objects.filter(type='expense')
        for trans in expense_transactions[:5]:  # Create anomalies for first 5 expense transactions
            severity = random.randint(1, 3)  # Low, Medium, or High
            anomaly_type = random.choice(['expense_spike', 'unusual_amount', 'frequency_change'])
            
            AnomalyDetection.objects.create(
                anomaly_type=anomaly_type,
                transaction=trans,
                detected_value=trans.amount,
                expected_value=trans.amount * Decimal(str(random.uniform(0.6, 0.9))),
                severity=severity,
                description=f'Anomaly detected in transaction: {trans.description}'
            )
        
        self.stdout.write(self.style.SUCCESS('Created anomaly detections'))
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created fresh seed data for all analytics features!')
        )