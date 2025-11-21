from django.db import migrations
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


def create_comprehensive_analytics_demo_data(apps, schema_editor):
    """
    Create comprehensive analytics demo data showing various features
    """
    FinancialForecast = apps.get_model('analytics', 'FinancialForecast')
    AnomalyDetection = apps.get_model('analytics', 'AnomalyDetection')
    Recommendation = apps.get_model('analytics', 'Recommendation')
    PredictiveModel = apps.get_model('analytics', 'PredictiveModel')
    ScenarioAnalysis = apps.get_model('analytics', 'ScenarioAnalysis')
    Transaction = apps.get_model('app', 'Transaction')
    Category = apps.get_model('app', 'Category')
    User = apps.get_model('auth', 'User')
    
    # Get a user for the demo data
    user = User.objects.first()
    if not user:
        return  # If no user exists, exit gracefully
    
    # Create more realistic financial forecasts showing trends
    import datetime
    for i in range(6):
        prediction_date = timezone.now().date() + datetime.timedelta(days=30*(i+1))
        base_value = 15000 + (i * 1000)  # Slight upward trend
        
        FinancialForecast.objects.create(
            forecast_type='cash_flow',
            predicted_value=Decimal(str(base_value + (i * 500))),
            confidence_interval_low=Decimal(str(base_value * 0.9)),
            confidence_interval_high=Decimal(str(base_value * 1.1)),
            prediction_date=prediction_date,
            generated_by=user,
            model_used='Linear Regression Trend Model',
            training_period_start=timezone.now().date() - datetime.timedelta(days=365),
            training_period_end=timezone.now().date(),
            notes=f'Month {i+1} cash flow forecast based on trend analysis'
        )
    
    # Create realistic anomaly detections 
    # Find some actual transactions to link to anomalies
    transactions = Transaction.objects.all()[:5]  # Get first 5 transactions
    
    for i, transaction in enumerate(transactions):
        if transaction:
            AnomalyDetection.objects.create(
                anomaly_type='unusual_amount',
                transaction=transaction,
                detected_value=transaction.amount,
                expected_value=transaction.amount * Decimal('0.6'),  # Expected lower amount
                severity=2,  # Medium severity
                description=f'Unusually high transaction amount detected for: {transaction.description[:50]}...',
            )
    
    # Create realistic recommendations
    recommendations_data = [
        {
            'type': 'expense_optimization',
            'title': 'Reduce Office Supply Costs',
            'description': 'Analysis shows office supply expenses are 25% higher than industry average',
            'action': 'Negotiate bulk discounts with suppliers or switch to cost-effective alternatives',
            'impact': 500.0,
            'confidence': 0.78
        },
        {
            'type': 'investment_opportunity',
            'title': 'Consider Tech Stock Investment',
            'description': 'Market analysis suggests tech stocks are undervalued for long-term growth',
            'action': 'Allocate 10% of portfolio to tech sector ETFs',
            'impact': 2500.0,
            'confidence': 0.82
        },
        {
            'type': 'budget_adjustment',
            'title': 'Increase Marketing Budget',
            'description': 'Marketing ROI analysis shows 300% return on investment, suggesting budget increase',
            'action': 'Increase marketing budget by 20% for next quarter',
            'impact': 1200.0,
            'confidence': 0.85
        },
        {
            'type': 'expense_optimization',
            'title': 'Optimize Subscriptions',
            'description': 'Identified 3 duplicate subscriptions costing $150/month',
            'action': 'Cancel duplicate subscriptions and consolidate tools',
            'impact': 1800.0,
            'confidence': 0.90
        }
    ]
    
    for rec_data in recommendations_data:
        Recommendation.objects.create(
            recommendation_type=rec_data['type'],
            title=rec_data['title'],
            description=rec_data['description'],
            suggested_action=rec_data['action'],
            impact_estimate=Decimal(str(rec_data['impact'])),
            confidence_score=rec_data['confidence'],
            generated_by=user,
        )
    
    # Create predictive models with realistic data
    PredictiveModel.objects.create(
        model_name='Advanced Cash Flow Predictor',
        model_type='cash_flow_forecast',
        version='2.1',
        description='Advanced model using seasonal decomposition and trend analysis',
        training_data_start=timezone.now().date() - datetime.timedelta(days=730),  # 2 years
        training_data_end=timezone.now().date(),
        accuracy_score=0.87,
        feature_columns=['month', 'quarter', 'trend', 'seasonality'],
        algorithm_used='ARIMA with Exogenous Variables'
    )
    
    # Create scenario analyses
    scenario_params = {
        'revenue_change': {
            'change_percentage': 15.0,
            'period_months': 12,
            'initial_value': 25000
        },
        'expense_reduction': {
            'reduction_percentage': 12.0,
            'period_months': 12,
            'initial_value': 18000
        }
    }
    
    for scenario_type, params in scenario_params.items():
        change_key = 'change_percentage' if scenario_type == 'revenue_change' else 'reduction_percentage'
        ScenarioAnalysis.objects.create(
            name=f'Business Growth Scenario - {params[change_key]}% {scenario_type.replace("_", " ").strip()}',
            scenario_type=scenario_type,
            description=f'Comprehensive {scenario_type.replace("_", " ")} analysis for business planning',
            input_parameters={
                'change_percentage': params[change_key],
                'period_months': params['period_months'],
                'initial_value': params['initial_value']
            },
            predicted_outcomes={
                'initial_value': params['initial_value'],
                'projected_value': params['initial_value'] * (1 + params[change_key]/100 if scenario_type == 'revenue_change' else 1 - params[change_key]/100),
                'change_percentage': params[change_key],
                'period_months': params['period_months']
            },
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=params['period_months']
        )


def reverse_comprehensive_analytics_demo_data(apps, schema_editor):
    """
    Reverse the comprehensive analytics demo data creation
    """
    FinancialForecast = apps.get_model('analytics', 'FinancialForecast')
    AnomalyDetection = apps.get_model('analytics', 'AnomalyDetection')
    Recommendation = apps.get_model('analytics', 'Recommendation')
    PredictiveModel = apps.get_model('analytics', 'PredictiveModel')
    ScenarioAnalysis = apps.get_model('analytics', 'ScenarioAnalysis')
    
    # Delete demo data
    FinancialForecast.objects.filter(model_used='Linear Regression Trend Model').delete()
    AnomalyDetection.objects.filter(description__contains='Unusually high transaction amount detected').delete()
    Recommendation.objects.filter(title__in=[
        'Reduce Office Supply Costs', 'Consider Tech Stock Investment', 
        'Increase Marketing Budget', 'Optimize Subscriptions'
    ]).delete()
    PredictiveModel.objects.filter(model_name='Advanced Cash Flow Predictor').delete()
    ScenarioAnalysis.objects.filter(name__contains='Business Growth Scenario').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_update_existing_analytics_fields'),
        ('app', '0002_asset_maintenance_cost_forecast_and_more'),
    ]

    operations = [
        migrations.RunPython(create_comprehensive_analytics_demo_data, reverse_comprehensive_analytics_demo_data),
    ]