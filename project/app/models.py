from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Categories for transactions (income and expense categories)
    """
    CATEGORY_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'category_type')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Transaction(models.Model):
    """
    Financial transactions (income and expenses)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    attachment = models.FileField(upload_to='transactions/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, blank=True, null=True)  # daily, weekly, monthly, yearly
    # Add field for ML-based category suggestions
    ml_predicted_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_predicted_transactions',
        help_text="Machine learning predicted category"
    )
    ml_confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence score for ML-based category prediction"
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.type.title()} - {self.amount} - {self.date}"


class Asset(models.Model):
    """
    Company assets (fixed and current assets)
    """
    ASSET_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('current', 'Current'),
    ]

    DEPRECIATION_METHOD_CHOICES = [
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
    ]

    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    category = models.CharField(max_length=100)  # Equipment, Vehicle, Building, etc.
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    depreciation_rate = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    depreciation_method = models.CharField(max_length=20, choices=DEPRECIATION_METHOD_CHOICES, default='straight_line')
    useful_life_years = models.PositiveIntegerField(default=0)  # Useful life in years
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add fields for predictive analytics
    predicted_maintenance_date = models.DateField(null=True, blank=True,
                                                  help_text="Predicted next maintenance date")
    maintenance_cost_forecast = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Predicted future maintenance costs"
    )

    def calculate_depreciation(self):
        """Calculate accumulated depreciation"""
        if self.depreciation_method == 'straight_line':
            # Straight line depreciation: (purchase_price / useful_life_years)
            if self.useful_life_years > 0:
                annual_depreciation = self.purchase_price / self.useful_life_years
                # Calculate how many years have passed since purchase
                from datetime import date
                years_since_purchase = Decimal(str((date.today() - self.purchase_date).days / 365.25))
                return min(annual_depreciation * years_since_purchase, self.purchase_price)
        elif self.depreciation_method == 'declining_balance':
            # Declining balance depreciation: depreciation rate * current book value
            if self.useful_life_years > 0:
                # Calculate declining balance rate (usually 2x straight-line rate)
                if self.depreciation_rate > 0:
                    declining_rate = self.depreciation_rate / 100  # Convert percentage to decimal
                    from datetime import date
                    years_since_purchase = Decimal(str((date.today() - self.purchase_date).days / 365.25))
                    # For declining balance, we calculate depreciation based on rate
                    # Simple declining balance calculation (more complex ones handle partial years differently)
                    if years_since_purchase > 0:
                        # Calculate depreciation but ensure it doesn't exceed original value
                        depreciation_for_period = self.purchase_price * (1 - (1 - Decimal(str(declining_rate))) ** years_since_purchase)
                        return min(depreciation_for_period, self.purchase_price)
        return Decimal('0.00')

    def current_book_value(self):
        """Calculate current book value after depreciation"""
        depreciation = self.calculate_depreciation()
        return self.purchase_price - depreciation

    def __str__(self):
        return self.name


class Investment(models.Model):
    """
    Investment portfolio management
    """
    INVESTMENT_TYPE_CHOICES = [
        ('stocks', 'Stocks'),
        ('bonds', 'Bonds'),
        ('real_estate', 'Real Estate'),
        ('business', 'Business'),
        ('mutual_funds', 'Mutual Funds'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('other', 'Other'),
    ]

    RISK_LEVEL_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    name = models.CharField(max_length=255)
    investment_type = models.CharField(max_length=100, choices=INVESTMENT_TYPE_CHOICES)
    initial_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    purchase_date = models.DateField()
    expected_roi = models.FloatField(validators=[MinValueValidator(0.0)])  # Expected ROI in percentage
    actual_roi = models.FloatField(default=0.0)  # Actual ROI in percentage
    risk_level = models.IntegerField(choices=RISK_LEVEL_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_investments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add fields for predictive analytics
    predicted_roi = models.FloatField(
        default=0.0,
        help_text="AI/ML predicted ROI for this investment"
    )
    predicted_value_12m = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Predicted value in 12 months"
    )
    risk_assessment_updated = models.DateTimeField(null=True, blank=True,
                                                   help_text="Last date when risk was assessed by ML model")

    def calculate_roi_percentage(self):
        """Calculate ROI percentage based on initial and current value"""
        if self.initial_amount > 0:
            roi = ((self.current_value - self.initial_amount) / self.initial_amount) * 100
            return round(roi, 2)
        return 0.0

    def calculate_profit_loss(self):
        """Calculate profit or loss"""
        return self.current_value - self.initial_amount

    def __str__(self):
        return f"{self.name} - {self.investment_type}"


class Budget(models.Model):
    """
    Budget management per category
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()  # 4-digit year
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'month', 'year')
        ordering = ['-year', '-month']

    def remaining_budget(self):
        """Calculate remaining budget amount"""
        return self.amount - self.spent_amount

    def budget_utilization_percentage(self):
        """Calculate budget utilization percentage"""
        if self.amount > 0:
            return round((self.spent_amount / self.amount) * 100, 2)
        return 0.0

    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.spent_amount > self.amount

    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year}"


class UserProfile(models.Model):
    """
    Extended user profile with role-based permissions
    """
    USER_ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('finance_manager', 'Finance Manager'),
        ('accountant', 'Accountant'),
        ('viewer', 'Viewer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='viewer')
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Report(models.Model):
    """
    Generated financial reports
    """
    REPORT_TYPE_CHOICES = [
        ('pnl', 'Profit and Loss Statement'),
        ('cash_flow', 'Cash Flow Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('investment', 'Investment Report'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.name} - {self.generated_at}"


class AuditLog(models.Model):
    """
    Audit trail for tracking important changes
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)  # Name of the model affected
    object_id = models.PositiveIntegerField()  # ID of the affected object
    old_values = models.JSONField(blank=True, null=True)  # Old values before change
    new_values = models.JSONField(blank=True, null=True)  # New values after change
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name}:{self.object_id}"


class CompanyInfo(models.Model):
    """
    Company information for the application
    """
    company_name = models.CharField(max_length=255)
    company_address = models.TextField()
    fiscal_year_start = models.DateField()  # Start date of fiscal year
    currency = models.CharField(max_length=3, default='USD')  # ISO currency code
    timezone = models.CharField(max_length=50, default='UTC')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name