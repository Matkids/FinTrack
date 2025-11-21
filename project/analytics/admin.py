from django.contrib import admin
from .models import FinancialForecast, AnomalyDetection, Recommendation, PredictiveModel, ScenarioAnalysis


@admin.register(FinancialForecast)
class FinancialForecastAdmin(admin.ModelAdmin):
    list_display = ['forecast_type', 'predicted_value', 'prediction_date', 'created_at', 'model_used']
    list_filter = ['forecast_type', 'created_at', 'model_used']
    search_fields = ['forecast_type', 'model_used']
    readonly_fields = ['created_at']


@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = ['anomaly_type', 'detected_value', 'severity', 'detected_at', 'is_resolved']
    list_filter = ['anomaly_type', 'severity', 'is_resolved', 'detected_at']
    search_fields = ['anomaly_type', 'description']
    readonly_fields = ['detected_at']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommendation_type', 'title', 'confidence_score', 'created_at', 'is_applied']
    list_filter = ['recommendation_type', 'is_applied', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']


@admin.register(PredictiveModel)
class PredictiveModelAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'model_type', 'version', 'accuracy_score', 'is_active']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['model_name', 'algorithm_used']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ScenarioAnalysis)
class ScenarioAnalysisAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario_type', 'created_at', 'period_months']
    list_filter = ['scenario_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
