from django.contrib import admin
from .models import (
    Transaction, Category, Asset, Investment, 
    Budget, UserProfile, Report, AuditLog, CompanyInfo
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'amount', 'category', 'created_by', 'created_at']
    list_filter = ['type', 'category', 'created_at']
    search_fields = ['description', 'created_by__username']
    date_hierarchy = 'date'


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'category', 'purchase_price', 'current_value', 'is_active']
    list_filter = ['asset_type', 'is_active', 'category']
    search_fields = ['name', 'description']


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'investment_type', 'initial_amount', 'current_value', 'risk_level', 'is_active']
    list_filter = ['investment_type', 'risk_level', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'month', 'year', 'spent_amount', 'remaining_budget']
    list_filter = ['month', 'year', 'category__name']
    search_fields = ['category__name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__email', 'department']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'generated_by', 'generated_at', 'start_date', 'end_date']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['name', 'generated_by__username']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name']
    date_hierarchy = 'timestamp'


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'currency', 'timezone']
    search_fields = ['company_name', 'tax_id']