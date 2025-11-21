from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Category, Asset, Investment, Budget, UserProfile, Report, AuditLog, CompanyInfo
from decimal import Decimal
from django.core.validators import MinValueValidator


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'type', 'category', 'description', 'attachment', 'is_recurring', 'recurrence_pattern']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'recurrence_pattern': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'asset_type', 'category', 'purchase_date', 'purchase_price', 
            'current_value', 'depreciation_rate', 'depreciation_method', 'useful_life_years',
            'location', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'asset_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'current_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'depreciation_rate': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.1', 'min': '0'}),
            'depreciation_method': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'rows': 3}),
        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = [
            'name', 'investment_type', 'initial_amount', 'current_value',
            'purchase_date', 'expected_roi', 'risk_level', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'investment_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'initial_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'current_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'expected_roi': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.1'}),
            'risk_level': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'rows': 3}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'step': '0.01'}),
            'month': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'year': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'department', 'phone_number']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'department': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
        }


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = [
            'company_name', 'company_address', 'fiscal_year_start', 'currency', 
            'timezone', 'logo', 'tax_id'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'company_address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'rows': 3}),
            'fiscal_year_start': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base', 'maxlength': 3}),
            'timezone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
            'tax_id': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base'}),
        }