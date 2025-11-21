"""
Analytics and AI views for FinTrack application
This module contains views for predictive analytics and recommendations
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import FinancialForecast, AnomalyDetection, Recommendation, PredictiveModel, ScenarioAnalysis
from .services import (
    CashFlowForecastService, AnomalyDetectionService,
    RecommendationService, ScenarioAnalysisService
)
from app.models import Transaction, Category, Asset, Investment


@login_required
def analytics_dashboard(request):
    """
    Analytics dashboard showing advanced insights and predictions
    """
    # Get financial forecast data
    forecasts = FinancialForecast.objects.filter(
        prediction_date__gte=timezone.now().date(),
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-prediction_date')[:10]

    # Get recent anomalies
    anomalies = AnomalyDetection.objects.filter(
        detected_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-detected_at')[:10]

    # Get recommendations
    recommendations = Recommendation.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created_at')[:10]

    # Get active models count
    active_models_count = PredictiveModel.objects.filter(is_active=True).count()

    context = {
        'forecasts': forecasts,
        'anomalies': anomalies,
        'recommendations': recommendations,
        'active_models_count': active_models_count,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def generate_cash_flow_forecast(request):
    """
    Generate cash flow forecast based on historical data
    """
    try:
        if request.method == 'POST':
            months_ahead = int(request.POST.get('months_ahead', 6))

            # Use the CashFlowForecastService to generate the forecast
            result = CashFlowForecastService.generate_forecast(request.user, months_ahead)

            if result['success']:
                return JsonResponse(result)
            else:
                return JsonResponse({'error': result['message']}, status=400)

        return render(request, 'analytics/forecast_form.html')
    except Exception as e:
        import traceback
        error_message = str(e)
        print(f"Error in generate_cash_flow_forecast: {error_message}")
        print(traceback.format_exc())  # This will help debug the issue
        return JsonResponse({
            'success': False,
            'message': f'Error generating cash flow forecast: {error_message}'
        }, status=500)


@login_required
def detect_expense_anomalies(request):
    """
    Detect unusual expenses using anomaly detection algorithms
    """
    try:
        # Use the AnomalyDetectionService to detect anomalies
        result = AnomalyDetectionService.detect_expense_anomalies(request.user)
        return JsonResponse(result)
    except Exception as e:
        import traceback
        error_message = str(e)
        print(f"Error in detect_expense_anomalies: {error_message}")
        print(traceback.format_exc())  # This will help debug the issue
        return JsonResponse({
            'success': False,
            'message': f'Error detecting anomalies: {error_message}'
        }, status=500)


@login_required
def generate_recommendations(request):
    """
    Generate smart recommendations based on financial data analysis
    """
    try:
        # Use the RecommendationService to generate recommendations
        result = RecommendationService.generate_recommendations(request.user)
        return JsonResponse(result)
    except Exception as e:
        import traceback
        error_message = str(e)
        print(f"Error in generate_recommendations: {error_message}")
        print(traceback.format_exc())  # This will help debug the issue
        return JsonResponse({
            'success': False,
            'message': f'Error generating recommendations: {error_message}'
        }, status=500)


@login_required
def api_analytics_data(request):
    """
    API endpoint for analytics dashboard data
    """
    # Get data for the last 12 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Prepare monthly data
    months = []
    actual_income = []
    actual_expenses = []
    forecasted_income = []
    forecasted_expenses = []
    
    for i in range(12):
        month_start = (end_date.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=35)).replace(day=1) - timedelta(days=1)
        
        months.append(month_start.strftime('%b %Y'))
        
        # Actual income and expenses
        income = Transaction.objects.filter(
            type='income',
            date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        expense = Transaction.objects.filter(
            type='expense',
            date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        actual_income.append(float(income))
        actual_expenses.append(float(expense))
        
        # Forecasted values (if available)
        forecast_income = FinancialForecast.objects.filter(
            forecast_type='revenue',
            prediction_date__range=[month_start, month_end]
        ).aggregate(avg=Avg('predicted_value'))['avg'] or Decimal('0.00')
        
        forecast_expense = FinancialForecast.objects.filter(
            forecast_type='expense',
            prediction_date__range=[month_start, month_end]
        ).aggregate(avg=Avg('predicted_value'))['avg'] or Decimal('0.00')
        
        forecasted_income.append(float(forecast_income))
        forecasted_expenses.append(float(forecast_expense))
    
    # Reverse to show oldest first
    months.reverse()
    actual_income.reverse()
    actual_expenses.reverse()
    forecasted_income.reverse()
    forecasted_expenses.reverse()
    
    # Anomaly detection statistics
    recent_anomalies = AnomalyDetection.objects.filter(
        detected_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Recommendation statistics
    recent_recommendations = Recommendation.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    data = {
        'months': months,
        'actual_income': actual_income,
        'actual_expenses': actual_expenses,
        'forecasted_income': forecasted_income,
        'forecasted_expenses': forecasted_expenses,
        'recent_anomalies_count': recent_anomalies,
        'recent_recommendations_count': recent_recommendations,
        'next_forecast_date': (timezone.now().date() + timedelta(days=30)).isoformat()
    }
    
    return JsonResponse(data)


@login_required
def run_scenario_analysis(request):
    """
    Run what-if scenario analysis
    """
    if request.method == 'POST':
        scenario_type = request.POST.get('scenario_type', '')
        parameters_json = request.POST.get('parameters', '{}')

        try:
            parameters = json.loads(parameters_json)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid parameters JSON'}, status=400)

        # Use the ScenarioAnalysisService to run the analysis
        result = ScenarioAnalysisService.run_scenario_analysis(request.user, scenario_type, parameters)

        return JsonResponse(result)

    return render(request, 'analytics/scenario_form.html')