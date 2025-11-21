from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Transaction, Category
from decimal import Decimal

class Command(BaseCommand):
    help = 'Test the logic used in cash flow statement to verify data extraction'

    def handle(self, *args, **options):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found'))
            return

        # Test data retrieval similar to cash flow statement
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        start_date = today.replace(day=1) - timedelta(days=30)  # 1 month back
        end_date = today
        
        print(f"Testing period: {start_date} to {end_date}")
        
        # Get transactions for the period
        all_transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            created_by=user
        ).select_related('category')
        
        print(f"Total transactions found for period: {all_transactions.count()}")
        
        # Show all transactions in the period
        for trans in all_transactions:
            print(f"  - {trans.date}: {trans.type} ${trans.amount} for category '{trans.category.name}' (lowercase: '{trans.category.name.lower()}')")
        
        # Now let's test categorization logic
        operating_inflows = Decimal('0.00')
        operating_outflows = Decimal('0.00')
        investing_inflows = Decimal('0.00')
        investing_outflows = Decimal('0.00')
        financing_inflows = Decimal('0.00')
        financing_outflows = Decimal('0.00')

        for trans in all_transactions:
            cat_name = trans.category.name.lower()
            
            print(f"Checking category: {cat_name}")

            if any(keyword in cat_name for keyword in [
                'sales', 'revenue', 'income', 'salary', 'wages', 'rent', 'utilities',
                'office', 'supplies', 'marketing', 'advertising', 'insurance', 'commission'
            ]):
                print(f"  -> Matches OPERATING: {trans.amount}")
                if trans.type == 'income':
                    operating_inflows += trans.amount
                else:
                    operating_outflows += trans.amount

            elif any(keyword in cat_name for keyword in [
                'investment', 'dividend', 'interest', 'equipment', 'vehicle', 'building',
                'property', 'purchase', 'sale of asset', 'stock', 'bond', 'real estate'
            ]):
                print(f"  -> Matches INVESTING: {trans.amount}")
                if trans.type == 'income':
                    investing_inflows += trans.amount
                else:
                    investing_outflows += trans.amount

            elif any(keyword in cat_name for keyword in [
                'loan', 'equity', 'dividend paid', 'share', 'borrowing',
                'repayment', 'debt', 'capital', 'mortgage', 'credit'
            ]):
                print(f"  -> Matches FINANCING: {trans.amount}")
                if trans.type == 'income':
                    financing_inflows += trans.amount
                else:
                    financing_outflows += trans.amount
            else:
                print(f"  -> DEFAULT to OPERATING: {trans.amount}")
                # Default to operating if not categorized as investing or financing
                if trans.type == 'income':
                    operating_inflows += trans.amount
                else:
                    operating_outflows += trans.amount

        print(f"\n--- RESULTS ---")
        print(f"Operating Inflows: ${operating_inflows}")
        print(f"Operating Outflows: ${operating_outflows}")
        print(f"Operating Net: ${operating_inflows - operating_outflows}")
        print(f"\\nInvesting Inflows: ${investing_inflows}")
        print(f"Investing Outflows: ${investing_outflows}")
        print(f"Investing Net: ${investing_inflows - investing_outflows}")
        print(f"\\nFinancing Inflows: ${financing_inflows}")
        print(f"Financing Outflows: ${financing_outflows}")
        print(f"Financing Net: ${financing_inflows - financing_outflows}")
        
        total_net = (operating_inflows - operating_outflows) + (investing_inflows - investing_outflows) + (financing_inflows - financing_outflows)
        print(f"\\nTotal Net Change: ${total_net}")