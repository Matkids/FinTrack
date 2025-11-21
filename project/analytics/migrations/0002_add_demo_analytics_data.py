from django.db import migrations
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta


def create_dummy_analytics_data(apps, schema_editor):
    """
    Create dummy analytics data for demonstration purposes
    """
    # Get the models for this migration
    FinancialForecast = apps.get_model('analytics', 'FinancialForecast')
    AnomalyDetection = apps.get_model('analytics', 'AnomalyDetection')
    Recommendation = apps.get_model('analytics', 'Recommendation')
    PredictiveModel = apps.get_model('analytics', 'PredictiveModel')
    ScenarioAnalysis = apps.get_model('analytics', 'ScenarioAnalysis')
    Transaction = apps.get_model('app', 'Transaction')
    Category = apps.get_model('app', 'Category')
    User = apps.get_model('auth', 'User')

    # Get a user for the demo data - must exist for foreign key relationships
    user = User.objects.first()
    if not user:
        # If no user exists, we cannot create analytics data with user relationships
        # so we'll skip creating the analytics data
        return

    # Create some demo categories if they don't exist
    income_category, _ = Category.objects.get_or_create(
        name='Demo Sales',
        category_type='income',
        defaults={'name': 'Demo Sales', 'category_type': 'income'}
    )
    expense_category, _ = Category.objects.get_or_create(
        name='Demo Office Supplies',
        category_type='expense',
        defaults={'name': 'Demo Office Supplies', 'category_type': 'expense'}
    )

    # Create demo transactions for anomaly detection
    demo_transactions = []
    for i in range(10):
        transaction = Transaction.objects.create(
            date=timezone.now().date() - timedelta(days=random.randint(1, 90)),
            amount=Decimal(str(random.uniform(100, 5000))),
            type=random.choice(['expense', 'income']),
            category=expense_category if random.choice([True, False]) else income_category,
            description=f'Demo transaction {i+1}',
            created_by=user
        )
        demo_transactions.append(transaction)
    
    # Create 5 financial forecasts
    for i in range(5):
        prediction_date = timezone.now().date() + timedelta(days=30*(i+1))
        FinancialForecast.objects.create(
            forecast_type=random.choice(['cash_flow', 'revenue', 'expense']),
            predicted_value=Decimal(str(random.uniform(5000, 20000))),
            confidence_interval_low=Decimal(str(random.uniform(4000, 18000))),
            confidence_interval_high=Decimal(str(random.uniform(6000, 22000))),
            prediction_date=prediction_date,
            generated_by=user,
            model_used='Demo Model',
            training_period_start=timezone.now().date() - timedelta(days=365),
            training_period_end=timezone.now().date(),
            notes=f'Demo forecast for month {i+1}'
        )
    
    # Create 3 anomaly detections
    for i, transaction in enumerate(demo_transactions[:3]):
        AnomalyDetection.objects.create(
            anomaly_type=random.choice(['expense_spike', 'unusual_amount', 'frequency_change']),
            transaction=transaction,
            detected_value=transaction.amount,
            expected_value=Decimal(str(transaction.amount * Decimal('0.8'))),
            severity=random.choice([1, 2, 3]),
            description=f'Demo anomaly detected in transaction {transaction.id}',
        )
    
    # Create 4 recommendations
    recommendation_types = ['expense_optimization', 'investment_opportunity', 'budget_adjustment', 'category_suggestion']
    for i, rec_type in enumerate(recommendation_types):
        Recommendation.objects.create(
            recommendation_type=rec_type,
            title=f'Demo Recommendation {i+1}',
            description=f'This is a demo recommendation of type {rec_type} for testing purposes.',
            suggested_action=f'Suggested action for demo recommendation {i+1}',
            impact_estimate=Decimal(str(random.uniform(100, 1000))),
            confidence_score=random.uniform(0.5, 0.95),
            generated_by=user,
        )
    
    # Create 2 predictive models
    PredictiveModel.objects.create(
        model_name='Demo Cash Flow Model',
        model_type='cash_flow_forecast',
        version='1.0',
        description='Demo model for cash flow forecasting',
        training_data_start=timezone.now().date() - timedelta(days=365),
        training_data_end=timezone.now().date(),
        accuracy_score=random.uniform(0.7, 0.95),
        feature_columns=['month_number', 'trend'],
        algorithm_used='LinearRegression'
    )
    
    PredictiveModel.objects.create(
        model_name='Demo Anomaly Detection Model',
        model_type='expense_anomaly',
        version='1.0',
        description='Demo model for expense anomaly detection',
        training_data_start=timezone.now().date() - timedelta(days=180),
        training_data_end=timezone.now().date(),
        accuracy_score=random.uniform(0.6, 0.9),
        feature_columns=['amount', 'frequency'],
        algorithm_used='IsolationForest'
    )
    
    # Create 2 scenario analyses
    scenario_data = {
        'revenue_change': {
            'change_percentage': 10.5,
            'period_months': 12
        },
        'expense_reduction': {
            'reduction_percentage': 7.2,
            'period_months': 12
        }
    }
    
    for scenario_type, params in scenario_data.items():
        ScenarioAnalysis.objects.create(
            name=f'Demo {scenario_type.replace("_", " ").title()} Scenario',
            scenario_type=scenario_type,
            description=f'Demo scenario analysis for {scenario_type}',
            input_parameters=params,
            predicted_outcomes={
                'initial_value': 10000,
                'projected_value': 11000,
                'change_percentage': params.get('change_percentage', params.get('reduction_percentage', 0))
            },
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=params['period_months']
        )


def reverse_dummy_analytics_data(apps, schema_editor):
    """
    Reverse the dummy data creation
    """
    FinancialForecast = apps.get_model('analytics', 'FinancialForecast')
    AnomalyDetection = apps.get_model('analytics', 'AnomalyDetection')
    Recommendation = apps.get_model('analytics', 'Recommendation')
    PredictiveModel = apps.get_model('analytics', 'PredictiveModel')
    ScenarioAnalysis = apps.get_model('analytics', 'ScenarioAnalysis')
    
    # Delete all demo data
    FinancialForecast.objects.filter(model_used='Demo Model').delete()
    AnomalyDetection.objects.filter(description__contains='Demo').delete()
    Recommendation.objects.filter(title__contains='Demo').delete()
    PredictiveModel.objects.filter(description__contains='Demo').delete()
    ScenarioAnalysis.objects.filter(name__contains='Demo').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
        ('app', '0002_asset_maintenance_cost_forecast_and_more'),
    ]

    operations = [
        migrations.RunPython(create_dummy_analytics_data, reverse_dummy_analytics_data),
    ]