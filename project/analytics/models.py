"""
Analytics and AI models for FinTrack application
This module contains models for predictive analytics and recommendations
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class FinancialForecast(models.Model):
    """
    Model to store financial forecasts and predictions
    """
    FORECAST_TYPE_CHOICES = [
        ('cash_flow', 'Cash Flow'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('investment', 'Investment Return'),
    ]

    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPE_CHOICES)
    predicted_value = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_interval_low = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    confidence_interval_high = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prediction_date = models.DateField()  # Date for which prediction is made
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model_used = models.CharField(max_length=100, help_text="Algorithm/model used for prediction")
    training_period_start = models.DateField()
    training_period_end = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-prediction_date', '-created_at']

    def __str__(self):
        return f"{self.forecast_type.title()} Forecast - {self.prediction_date}: {self.predicted_value}"


class AnomalyDetection(models.Model):
    """
    Model to store detected financial anomalies
    """
    ANOMALY_TYPE_CHOICES = [
        ('expense_spike', 'Expense Spike'),
        ('unusual_amount', 'Unusual Amount'),
        ('category_deviation', 'Category Deviation'),
        ('frequency_change', 'Frequency Change'),
    ]

    anomaly_type = models.CharField(max_length=30, choices=ANOMALY_TYPE_CHOICES)
    transaction = models.ForeignKey('app.Transaction', on_delete=models.CASCADE, null=True, blank=True)
    detected_value = models.DecimalField(max_digits=15, decimal_places=2)
    expected_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    severity = models.IntegerField(default=1, help_text="1=Low, 2=Medium, 3=High")  # 1=Low, 2=Medium, 3=High
    description = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.anomaly_type.title()} - {self.detected_at}: ${self.detected_value}"


class Recommendation(models.Model):
    """
    Model to store AI-powered recommendations
    """
    RECOMMENDATION_TYPE_CHOICES = [
        ('expense_optimization', 'Expense Optimization'),
        ('investment_opportunity', 'Investment Opportunity'),
        ('budget_adjustment', 'Budget Adjustment'),
        ('category_suggestion', 'Category Suggestion'),
    ]

    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    suggested_action = models.TextField()
    impact_estimate = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                         help_text="Estimated financial impact")
    confidence_score = models.FloatField(default=0.0,
                                         help_text="Confidence score between 0.0 and 1.0")
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='recommendations_applied')
    related_transaction = models.ForeignKey('app.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    related_asset = models.ForeignKey('app.Asset', on_delete=models.SET_NULL, null=True, blank=True)
    related_investment = models.ForeignKey('app.Investment', on_delete=models.SET_NULL, null=True, blank=True)
    related_budget = models.ForeignKey('app.Budget', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recommendation_type.title()}: {self.title} ({self.confidence_score*100:.0f}% confidence)"


class PredictiveModel(models.Model):
    """
    Model to track predictive models and their performance
    """
    MODEL_TYPE_CHOICES = [
        ('cash_flow_forecast', 'Cash Flow Forecast'),
        ('revenue_prediction', 'Revenue Prediction'),
        ('expense_anomaly', 'Expense Anomaly Detection'),
        ('investment_roi', 'Investment ROI Prediction'),
    ]

    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPE_CHOICES)
    version = models.CharField(max_length=20)
    description = models.TextField()
    training_data_start = models.DateField()
    training_data_end = models.DateField()
    accuracy_score = models.FloatField(null=True, blank=True)
    feature_columns = models.JSONField(help_text="List of features used in the model")
    algorithm_used = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('model_name', 'version')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} v{self.version} ({self.accuracy_score or 'N/A'} accuracy)"


class ScenarioAnalysis(models.Model):
    """
    Model to store what-if scenario analyses
    """
    SCENARIO_TYPE_CHOICES = [
        ('revenue_change', 'Revenue Change'),
        ('expense_reduction', 'Expense Reduction'),
        ('investment_impact', 'Investment Impact'),
    ]

    name = models.CharField(max_length=255)
    scenario_type = models.CharField(max_length=30, choices=SCENARIO_TYPE_CHOICES)
    description = models.TextField()
    input_parameters = models.JSONField(help_text="Input parameters for the scenario")
    predicted_outcomes = models.JSONField(help_text="Predicted outcomes from the scenario")
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    base_date = models.DateField()
    period_months = models.IntegerField(default=12, help_text="Projection period in months")

    def __str__(self):
        return f"{self.name} ({self.scenario_type.title()})"
