from django.db import migrations
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta


def update_existing_analytics_fields(apps, schema_editor):
    """
    Update existing model instances with analytics-related fields
    """
    Transaction = apps.get_model('app', 'Transaction')
    Asset = apps.get_model('app', 'Asset')
    Investment = apps.get_model('app', 'Investment')
    Category = apps.get_model('app', 'Category')
    
    # Get all models with data and update analytics fields
    transactions = Transaction.objects.all()
    for transaction in transactions:
        # Set ML predicted category and confidence for some transactions
        if transaction.category and random.choice([True, False, False]):
            all_categories = Category.objects.all()
            if all_categories.exists():
                ml_category = random.choice(list(all_categories))
                transaction.ml_predicted_category = ml_category
                transaction.ml_confidence_score = random.uniform(0.6, 0.95)
                transaction.save()
    
    # Update assets with predictive maintenance fields
    assets = Asset.objects.all()
    for asset in assets:
        # Set predicted maintenance date (in next 1-12 months)
        asset.predicted_maintenance_date = timezone.now().date() + timedelta(days=random.randint(30, 365))
        asset.maintenance_cost_forecast = Decimal(str(random.uniform(100, 2000)))
        asset.save()
    
    # Update investments with predictive fields
    investments = Investment.objects.all()
    for investment in investments:
        # Set predicted ROI and 12-month value
        investment.predicted_roi = random.uniform(5.0, 15.0)
        investment.predicted_value_12m = investment.current_value * Decimal(str(1 + random.uniform(0.05, 0.15)))
        investment.risk_assessment_updated = timezone.now()
        investment.save()


def reverse_update_existing_analytics_fields(apps, schema_editor):
    """
    Reverse the updates to existing analytics fields
    """
    Transaction = apps.get_model('app', 'Transaction')
    Asset = apps.get_model('app', 'Asset')
    Investment = apps.get_model('app', 'Investment')
    
    # Clear the analytics fields
    Transaction.objects.update(
        ml_predicted_category=None,
        ml_confidence_score=0.0
    )
    
    Asset.objects.update(
        predicted_maintenance_date=None,
        maintenance_cost_forecast=None
    )
    
    Investment.objects.update(
        predicted_roi=0.0,
        predicted_value_12m=None,
        risk_assessment_updated=None
    )


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_add_demo_analytics_data'),
        ('app', '0002_asset_maintenance_cost_forecast_and_more'),
    ]

    operations = [
        migrations.RunPython(update_existing_analytics_fields, reverse_update_existing_analytics_fields),
    ]