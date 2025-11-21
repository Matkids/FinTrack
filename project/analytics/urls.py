from django.urls import path
from . import views

urlpatterns = [
    # Analytics dashboard
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/analytics-data/', views.api_analytics_data, name='api_analytics_data'),
    
    # Forecasting
    path('forecast/cash-flow/', views.generate_cash_flow_forecast, name='generate_cash_flow_forecast'),
    
    # Anomaly detection
    path('anomalies/detect/', views.detect_expense_anomalies, name='detect_expense_anomalies'),
    
    # Recommendations
    path('recommendations/generate/', views.generate_recommendations, name='generate_recommendations'),
    
    # Scenario analysis
    path('scenarios/run/', views.run_scenario_analysis, name='run_scenario_analysis'),
]