from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/update/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # Assets
    path('assets/', views.assets_list, name='assets_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/update/', views.asset_update, name='asset_update'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    
    # Investments
    path('investments/', views.investments_list, name='investments_list'),
    path('investments/create/', views.investment_create, name='investment_create'),
    path('investments/<int:pk>/update/', views.investment_update, name='investment_update'),
    path('investments/<int:pk>/delete/', views.investment_delete, name='investment_delete'),
    
    # Reports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/generate/', views.report_generate_form, name='report_generate_form'),
    path('reports/generate/<str:report_type>/', views.generate_report, name='generate_report'),
]