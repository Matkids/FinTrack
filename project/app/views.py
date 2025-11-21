from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from .models import (
    Transaction, Category, Asset, Investment, Budget, 
    UserProfile, Report, AuditLog, CompanyInfo
)
from .forms import (
    TransactionForm, AssetForm, InvestmentForm,
    BudgetForm, UserProfileForm, CompanyInfoForm
)


def dashboard(request):
    """
    Main dashboard view showing financial summary
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get date range for current month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = today
    
    # Calculate financial summary for the current month
    income_transactions = Transaction.objects.filter(
        type='income', 
        date__gte=start_of_month, 
        date__lte=end_of_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    expense_transactions = Transaction.objects.filter(
        type='expense', 
        date__gte=start_of_month, 
        date__lte=end_of_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    net_profit = income_transactions - expense_transactions
    
    # Get recent transactions (last 10)
    recent_transactions = Transaction.objects.select_related('category', 'created_by').order_by('-date')[:10]
    
    # Get asset summary
    total_assets = Asset.objects.filter(is_active=True).aggregate(total=Sum('current_value'))['total'] or Decimal('0.00')
    
    # Get investment summary
    total_investments = Investment.objects.filter(is_active=True).aggregate(total=Sum('current_value'))['total'] or Decimal('0.00')
    
    # Get upcoming budgets (with high utilization)
    # Note: budget_utilization_percentage is a property, so we need to filter differently
    all_budgets = Budget.objects.select_related('category')[:20]  # Get a reasonable number to check
    high_utilization_budgets = []
    for budget in all_budgets:
        if budget.budget_utilization_percentage() >= 80:
            high_utilization_budgets.append(budget)
            if len(high_utilization_budgets) >= 5:
                break
    
    context = {
        'income': income_transactions,
        'expenses': expense_transactions,
        'net_profit': net_profit,
        'total_assets': total_assets,
        'total_investments': total_investments,
        'recent_transactions': recent_transactions,
        'high_utilization_budgets': high_utilization_budgets,
        'current_month': start_of_month.strftime('%B %Y'),
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def transactions_list(request):
    """
    List all transactions with filtering options
    """
    transactions = Transaction.objects.select_related('category', 'created_by').order_by('-date')
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    transaction_type = request.GET.get('type')
    category_id = request.GET.get('category')
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Get categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
        'selected_type': transaction_type,
        'selected_category': category_id,
    }
    
    return render(request, 'transactions/list.html', context)


@login_required
def transaction_create(request):
    """
    Create a new transaction
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            
            # Log the transaction creation - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                elif hasattr(value, 'name'):  # File objects like InMemoryUploadedFile
                    cleaned_data_serializable[key] = value.name if value.name else None
                elif isinstance(value, (bytes, bytearray)):
                    cleaned_data_serializable[key] = '<binary_data>'
                elif value is None or isinstance(value, (str, int, float, bool)):
                    cleaned_data_serializable[key] = value
                else:
                    cleaned_data_serializable[key] = str(value)

            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Transaction',
                object_id=transaction.id,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Transaction created successfully!')
            return redirect('transactions_list')
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/form.html', {'form': form, 'title': 'Create Transaction'})


@login_required
def transaction_update(request, pk):
    """
    Update an existing transaction
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            old_values = {
                'date': transaction.date.isoformat() if hasattr(transaction.date, 'isoformat') else str(transaction.date),
                'amount': float(transaction.amount) if isinstance(transaction.amount, Decimal) else transaction.amount,
                'type': transaction.type,
                'category': transaction.category.name,
                'description': transaction.description,
            }

            transaction = form.save()

            # Log the transaction update - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                elif hasattr(value, 'name'):  # File objects like InMemoryUploadedFile
                    cleaned_data_serializable[key] = value.name if value.name else None
                elif isinstance(value, (bytes, bytearray)):
                    cleaned_data_serializable[key] = '<binary_data>'
                elif value is None or isinstance(value, (str, int, float, bool)):
                    cleaned_data_serializable[key] = value
                else:
                    cleaned_data_serializable[key] = str(value)

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='Transaction',
                object_id=transaction.id,
                old_values=old_values,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions_list')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transactions/form.html', {
        'form': form, 
        'title': 'Update Transaction',
        'transaction': transaction
    })


@login_required
def transaction_delete(request, pk):
    """
    Delete a transaction
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        # Log the transaction deletion
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Transaction',
            object_id=transaction.id,
            old_values={
                'date': transaction.date.isoformat() if hasattr(transaction.date, 'isoformat') else str(transaction.date),
                'amount': float(transaction.amount) if isinstance(transaction.amount, Decimal) else transaction.amount,
                'type': transaction.type,
                'category': transaction.category.name,
                'description': transaction.description,
            }
        )
        
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions_list')
    
    return render(request, 'transactions/confirm_delete.html', {'transaction': transaction})


@login_required
def assets_list(request):
    """
    List all assets
    """
    assets = Asset.objects.filter(is_active=True).select_related('created_by').order_by('-created_at')
    
    # Filter by type if provided
    asset_type = request.GET.get('type')
    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    
    context = {
        'assets': assets,
        'selected_type': asset_type,
    }
    
    return render(request, 'assets/list.html', context)


@login_required
def asset_create(request):
    """
    Create a new asset
    """
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.created_by = request.user
            asset.save()
            
            # Log the asset creation - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                else:
                    cleaned_data_serializable[key] = value

            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Asset',
                object_id=asset.id,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Asset created successfully!')
            return redirect('assets_list')
    else:
        form = AssetForm()
    
    return render(request, 'assets/form.html', {'form': form, 'title': 'Create Asset'})


@login_required
def asset_update(request, pk):
    """
    Update an existing asset
    """
    asset = get_object_or_404(Asset, pk=pk)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            old_values = {
                'name': asset.name,
                'asset_type': asset.asset_type,
                'category': str(asset.category),
                'purchase_date': asset.purchase_date.isoformat() if hasattr(asset.purchase_date, 'isoformat') else str(asset.purchase_date),
                'purchase_price': float(asset.purchase_price) if isinstance(asset.purchase_price, Decimal) else asset.purchase_price,
                'current_value': float(asset.current_value) if isinstance(asset.current_value, Decimal) else asset.current_value,
            }

            asset = form.save()

            # Log the asset update - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                else:
                    cleaned_data_serializable[key] = value

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='Asset',
                object_id=asset.id,
                old_values=old_values,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Asset updated successfully!')
            return redirect('assets_list')
    else:
        form = AssetForm(instance=asset)
    
    return render(request, 'assets/form.html', {
        'form': form, 
        'title': 'Update Asset',
        'asset': asset
    })


@login_required
def asset_delete(request, pk):
    """
    Delete an asset
    """
    asset = get_object_or_404(Asset, pk=pk)
    
    if request.method == 'POST':
        # Log the asset deletion
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Asset',
            object_id=asset.id,
            old_values={
                'name': asset.name,
                'asset_type': asset.asset_type,
                'category': asset.category,
                'purchase_date': asset.purchase_date.isoformat() if hasattr(asset.purchase_date, 'isoformat') else str(asset.purchase_date),
                'purchase_price': float(asset.purchase_price) if isinstance(asset.purchase_price, Decimal) else asset.purchase_price,
            }
        )
        
        asset.delete()
        messages.success(request, 'Asset deleted successfully!')
        return redirect('assets_list')
    
    return render(request, 'assets/confirm_delete.html', {'asset': asset})


@login_required
def investments_list(request):
    """
    List all investments
    """
    investments = Investment.objects.filter(is_active=True).select_related('created_by').order_by('-created_at')
    
    # Calculate additional investment metrics
    for investment in investments:
        investment.roi_percentage = investment.calculate_roi_percentage()
        investment.profit_loss = investment.calculate_profit_loss()
    
    context = {
        'investments': investments,
    }
    
    return render(request, 'investments/list.html', context)


@login_required
def investment_create(request):
    """
    Create a new investment
    """
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_by = request.user
            investment.save()
            
            # Calculate and update ROI if not provided
            investment.actual_roi = investment.calculate_roi_percentage()
            investment.save()
            
            # Log the investment creation - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                else:
                    cleaned_data_serializable[key] = value

            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Investment',
                object_id=investment.id,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Investment created successfully!')
            return redirect('investments_list')
    else:
        form = InvestmentForm()
    
    return render(request, 'investments/form.html', {'form': form, 'title': 'Create Investment'})


@login_required
def investment_update(request, pk):
    """
    Update an existing investment
    """
    investment = get_object_or_404(Investment, pk=pk)
    
    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            old_values = {
                'name': investment.name,
                'investment_type': investment.investment_type,
                'initial_amount': float(investment.initial_amount) if isinstance(investment.initial_amount, Decimal) else investment.initial_amount,
                'current_value': float(investment.current_value) if isinstance(investment.current_value, Decimal) else investment.current_value,
                'purchase_date': investment.purchase_date.isoformat() if hasattr(investment.purchase_date, 'isoformat') else str(investment.purchase_date),
            }

            investment = form.save()

            # Calculate and update ROI
            investment.actual_roi = investment.calculate_roi_percentage()
            investment.save()

            # Log the investment update - convert non-serializable objects to strings
            cleaned_data_serializable = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (date, datetime)):
                    cleaned_data_serializable[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    cleaned_data_serializable[key] = float(value)
                elif hasattr(value, 'pk'):  # Foreign key objects (like Category)
                    cleaned_data_serializable[key] = str(value)
                else:
                    cleaned_data_serializable[key] = value

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='Investment',
                object_id=investment.id,
                old_values=old_values,
                new_values=cleaned_data_serializable
            )
            
            messages.success(request, 'Investment updated successfully!')
            return redirect('investments_list')
    else:
        form = InvestmentForm(instance=investment)
    
    return render(request, 'investments/form.html', {
        'form': form, 
        'title': 'Update Investment',
        'investment': investment
    })


@login_required
def investment_delete(request, pk):
    """
    Delete an investment
    """
    investment = get_object_or_404(Investment, pk=pk)
    
    if request.method == 'POST':
        # Log the investment deletion
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Investment',
            object_id=investment.id,
            old_values={
                'name': investment.name,
                'investment_type': investment.investment_type,
                'initial_amount': float(investment.initial_amount) if isinstance(investment.initial_amount, Decimal) else investment.initial_amount,
            }
        )
        
        investment.delete()
        messages.success(request, 'Investment deleted successfully!')
        return redirect('investments_list')
    
    return render(request, 'investments/confirm_delete.html', {'investment': investment})


@login_required
def reports_list(request):
    """
    List generated reports
    """
    reports = Report.objects.all().select_related('generated_by').order_by('-generated_at')
    
    context = {
        'reports': reports,
    }
    
    return render(request, 'reports/list.html', context)


@login_required
def report_generate_form(request, report_type=None):
    """
    Display form to select report dates and report type
    """
    if report_type:
        # If report type is specified, redirect to generate_report with date parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        params = ''
        if start_date:
            params += f'&start_date={start_date}'
        if end_date:
            params += f'&end_date={end_date}'
        return redirect(f'/reports/generate/{report_type}/?{params.lstrip("&")}')

    context = {
        'report_types': [
            {'type': 'pnl', 'name': 'Profit & Loss Statement', 'icon': 'fa-file-invoice-dollar', 'color': 'indigo'},
            {'type': 'cash_flow', 'name': 'Cash Flow Statement', 'icon': 'fa-water', 'color': 'green'},
            {'type': 'balance_sheet', 'name': 'Balance Sheet', 'icon': 'fa-balance-scale', 'color': 'purple'},
        ]
    }
    return render(request, 'reports/generate_form.html', context)


def generate_report(request, report_type):
    """
    Generate a specific type of report
    """
    today = timezone.now().date()

    if report_type == 'pnl':
        # Profit and Loss Statement
        # Calculate income and expenses for the current period
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse dates from GET parameters or use defaults
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)  # Default to first day of current month
        else:
            start_date = today.replace(day=1)  # Default to first day of current month

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today  # Default to today
        else:
            end_date = today  # Default to today
        
        # Get all income and expense transactions for the period with details
        income_transactions = Transaction.objects.filter(
            type='income',
            date__gte=start_date,
            date__lte=end_date,
            created_by=request.user
        ).select_related('category').order_by('date')

        expense_transactions = Transaction.objects.filter(
            type='expense',
            date__gte=start_date,
            date__lte=end_date,
            created_by=request.user
        ).select_related('category').order_by('date')

        # Calculate totals
        total_income = sum(trans.amount for trans in income_transactions)
        total_expenses = sum(trans.amount for trans in expense_transactions)
        net_profit = total_income - total_expenses

        # Group transactions by category for detailed breakdown
        income_by_category = {}
        for trans in income_transactions:
            cat_name = trans.category.name
            if cat_name not in income_by_category:
                income_by_category[cat_name] = Decimal('0.00')
            income_by_category[cat_name] += trans.amount

        expense_by_category = {}
        for trans in expense_transactions:
            cat_name = trans.category.name
            if cat_name not in expense_by_category:
                expense_by_category[cat_name] = Decimal('0.00')
            expense_by_category[cat_name] += trans.amount

        context = {
            'report_type': 'Profit and Loss Statement',
            'start_date': start_date,
            'end_date': end_date,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'income_transactions': income_transactions,
            'expense_transactions': expense_transactions,
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category,
        }

        # Save the generated report to the Report model
        Report.objects.create(
            name=f"Profit and Loss Statement - {start_date} to {end_date}",
            report_type='pnl',
            generated_by=request.user,
            start_date=start_date,
            end_date=end_date,
            description=f"Profit and Loss Statement from {start_date} to {end_date}",
        )

        return render(request, 'reports/pnl.html', context)
    
    elif report_type == 'cash_flow':
        # Cash Flow Statement
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse dates from GET parameters or use defaults
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)  # Default to first day of current month
        else:
            start_date = today.replace(day=1)  # Default to first day of current month

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today  # Default to today
        else:
            end_date = today  # Default to today

        # Get transactions for the period for this specific user
        all_transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            created_by=request.user
        ).select_related('category').order_by('date')

        # Categorize transactions for different cash flow activities
        operating_inflows = Decimal('0.00')
        operating_outflows = Decimal('0.00')
        investing_inflows = Decimal('0.00')
        investing_outflows = Decimal('0.00')
        financing_inflows = Decimal('0.00')
        financing_outflows = Decimal('0.00')

        # Separate transactions by type
        operating_transactions = []
        investing_transactions = []
        financing_transactions = []

        for trans in all_transactions:
            cat_name = trans.category.name.lower()

            # Check for investing activities first to avoid conflict with general 'income' keyword
            investing_keywords = [
                'investment', 'dividend', 'stock', 'bond', 'real estate',
                'equipment', 'vehicle', 'building', 'property', 'purchase of equipment',
                'sale of asset', 'purchase of asset'
            ]

            financing_keywords = [
                'loan', 'equity', 'dividend paid', 'share', 'borrowing',
                'repayment', 'debt', 'capital', 'mortgage', 'credit'
            ]

            # Special check for "interest" - determine if it's investment or loan interest
            if 'interest' in cat_name and any(keyword in cat_name for keyword in investing_keywords):
                # If it's investment interest
                if trans.type == 'income':
                    investing_inflows += trans.amount
                else:
                    investing_outflows += trans.amount
                investing_transactions.append(trans)
            elif 'interest' in cat_name and any(keyword in cat_name for keyword in financing_keywords):
                # If it's loan interest
                if trans.type == 'income':
                    financing_inflows += trans.amount
                else:
                    financing_outflows += trans.amount
                financing_transactions.append(trans)
            elif any(keyword in cat_name for keyword in investing_keywords):
                if trans.type == 'income':
                    investing_inflows += trans.amount
                else:
                    investing_outflows += trans.amount
                investing_transactions.append(trans)
            elif any(keyword in cat_name for keyword in financing_keywords):
                if trans.type == 'income':
                    financing_inflows += trans.amount
                else:
                    financing_outflows += trans.amount
                financing_transactions.append(trans)
            elif any(keyword in cat_name for keyword in [
                'sales', 'revenue', 'salary', 'wages', 'rent', 'utilities',
                'office', 'supplies', 'marketing', 'advertising', 'insurance',
                'commission', 'professional services', 'software licenses', 'travel'
            ]):
                # Operating activities - exclude those already categorized as investing/financing
                if trans.type == 'income':
                    operating_inflows += trans.amount
                else:
                    operating_outflows += trans.amount
                operating_transactions.append(trans)
            else:
                # Default to operating if not categorized elsewhere
                if trans.type == 'income':
                    operating_inflows += trans.amount
                else:
                    operating_outflows += trans.amount
                operating_transactions.append(trans)

        # Calculate net amounts for each category
        operating_net = operating_inflows - operating_outflows
        investing_net = investing_inflows - investing_outflows
        financing_net = financing_inflows - financing_outflows

        # Calculate total net change
        net_change = operating_net + investing_net + financing_net

        context = {
            'report_type': 'Cash Flow Statement',
            'start_date': start_date,
            'end_date': end_date,
            'operating_inflows': operating_inflows,
            'operating_outflows': operating_outflows,
            'operating_net': operating_net,
            'operating_net_abs': abs(float(operating_net)) if isinstance(operating_net, Decimal) else abs(operating_net),
            'investing_inflows': investing_inflows,
            'investing_outflows': investing_outflows,
            'investing_net': investing_net,
            'investing_net_abs': abs(float(investing_net)) if isinstance(investing_net, Decimal) else abs(investing_net),
            'financing_inflows': financing_inflows,
            'financing_outflows': financing_outflows,
            'financing_net': financing_net,
            'financing_net_abs': abs(float(financing_net)) if isinstance(financing_net, Decimal) else abs(financing_net),
            'net_change': net_change,
            'net_change_abs': abs(float(net_change)) if isinstance(net_change, Decimal) else abs(net_change),
            # Include transaction details for detailed view
            'operating_transactions': operating_transactions,
            'investing_transactions': investing_transactions,
            'financing_transactions': financing_transactions,
        }

        # Save the generated report to the Report model
        Report.objects.create(
            name=f"Cash Flow Statement - {start_date} to {end_date}",
            report_type='cash_flow',
            generated_by=request.user,
            start_date=start_date,
            end_date=end_date,
            description=f"Cash Flow Statement from {start_date} to {end_date}",
        )

        return render(request, 'reports/cash_flow.html', context)
    
    elif report_type == 'balance_sheet':
        # Balance Sheet
        # For balance sheet, we use the as_of_date (which is today by default)
        # but we still parse the date if it's provided in the request for consistency
        date_str = request.GET.get('as_of_date')  # Optional date parameter
        if date_str:
            try:
                as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                as_of_date = today  # Default to today
        else:
            as_of_date = today  # Default to today

        # Calculate total assets
        total_assets = Asset.objects.filter(is_active=True).aggregate(total=Sum('current_value'))['total'] or Decimal('0.00')

        # Calculate total liabilities - for now, we'll base this on transactions with specific liability categories
        # In a real system, you'd have a separate Liabilities model
        liability_categories = Category.objects.filter(
            Q(name__icontains='loan') |
            Q(name__icontains='debt') |
            Q(name__icontains='payable') |
            Q(name__icontains='obligation') |
            Q(name__icontains='accrued') |
            Q(name__icontains='liability')
        )

        # Calculate total liabilities based on transactions that are categorized as liabilities
        total_liabilities = Transaction.objects.filter(
            date__lte=as_of_date,
            category__in=liability_categories,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calculate equity as cumulative retained earnings: net income over time
        # Net Income = Total Income - Total Expenses
        total_income = Transaction.objects.filter(
            date__lte=as_of_date,
            type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_expenses = Transaction.objects.filter(
            date__lte=as_of_date,
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        net_income = total_income - total_expenses  # This represents accumulated retained earnings

        # For a basic balance sheet, we'll consider equity as the net income (retained earnings)
        # In a real system, equity includes contributed capital, retained earnings, etc.
        total_equity = net_income if net_income > 0 else Decimal('0.00')

        context = {
            'report_type': 'Balance Sheet',
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'as_of_date': as_of_date,
        }

        # Save the generated report to the Report model
        Report.objects.create(
            name=f"Balance Sheet - As of {as_of_date}",
            report_type='balance_sheet',
            generated_by=request.user,
            start_date=as_of_date,
            end_date=as_of_date,
            description=f"Balance Sheet as of {as_of_date}",
        )

        return render(request, 'reports/balance_sheet.html', context)

    elif report_type == 'investment':
        # Investment Report
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse dates from GET parameters or use defaults
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)  # Default to first day of current month
        else:
            start_date = today.replace(day=1)  # Default to first day of current month

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today  # Default to today
        else:
            end_date = today  # Default to today

        investments = Investment.objects.filter(
            purchase_date__range=[start_date, end_date]
        ).select_related('created_by')

        context = {
            'report_type': 'Investment Report',
            'start_date': start_date,
            'end_date': end_date,
            'investments': investments,
        }

        # Save the generated report to the Report model
        Report.objects.create(
            name=f"Investment Report - {start_date} to {end_date}",
            report_type='investment',
            generated_by=request.user,
            start_date=start_date,
            end_date=end_date,
            description=f"Investment Report from {start_date} to {end_date}",
        )

        return render(request, 'reports/investment.html', context)

    elif report_type == 'custom':
        # Custom Report - redirect to reports list or show a form to define custom report
        # For now, we'll redirect to reports list
        messages.info(request, 'Custom reports require additional configuration.')
        return redirect('reports_list')

    else:
        # Invalid report type
        messages.error(request, f'Invalid report type: {report_type}')
        return redirect('reports_list')




def api_dashboard_data(request):
    """
    API endpoint for dashboard chart data
    """
    # Get data for the last 6 months
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    
    # Income and expense data for the last 6 months
    income_data = []
    expense_data = []
    months = []
    
    for i in range(6):
        month_date = today - timedelta(days=30*i)
        start_of_month = month_date.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append(start_of_month.strftime('%b %Y'))
        
        income = Transaction.objects.filter(
            type='income',
            date__gte=start_of_month,
            date__lte=end_of_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        expense = Transaction.objects.filter(
            type='expense',
            date__gte=start_of_month,
            date__lte=end_of_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        income_data.append(float(income))
        expense_data.append(float(expense))
    
    # Reverse the lists to show oldest first
    months.reverse()
    income_data.reverse()
    expense_data.reverse()
    
    # Category breakdown for expenses
    expense_categories = Transaction.objects.filter(
        type='expense',
        date__gte=six_months_ago
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    category_labels = [item['category__name'] for item in expense_categories]
    category_values = [float(item['total']) for item in expense_categories]
    
    data = {
        'monthly_income': income_data,
        'monthly_expenses': expense_data,
        'months': months,
        'expense_categories': {
            'labels': category_labels,
            'values': category_values,
        }
    }

    return JsonResponse(data)


