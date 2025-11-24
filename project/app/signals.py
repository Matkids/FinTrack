from django.db.models import Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal
from .models import UserProfile, Transaction, Budget


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved
    """
    # Ensure the user has a profile
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


@receiver(post_save, sender=Transaction)
def update_budget_on_transaction_save(sender, instance, created, **kwargs):
    """
    Update budget spent_amount when a transaction is saved
    """
    if instance.type == 'expense':
        # Find the budget for this category and the month of the transaction
        from django.utils import timezone
        from datetime import date

        budget, created = Budget.objects.get_or_create(
            category=instance.category,
            month=instance.date.month,
            year=instance.date.year,
            defaults={'amount': instance.amount, 'created_by': instance.created_by}
        )

        # Recalculate spent amount for this category and month
        expenses_for_category = Transaction.objects.filter(
            category=instance.category,
            type='expense',
            date__month=instance.date.month,
            date__year=instance.date.year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        budget.spent_amount = expenses_for_category
        budget.save()


@receiver(post_delete, sender=Transaction)
def update_budget_on_transaction_delete(sender, instance, **kwargs):
    """
    Update budget spent_amount when a transaction is deleted
    """
    if instance.type == 'expense':
        try:
            budget = Budget.objects.get(
                category=instance.category,
                month=instance.date.month,
                year=instance.date.year
            )

            # Recalculate spent amount for this category and month
            expenses_for_category = Transaction.objects.filter(
                category=instance.category,
                type='expense',
                date__month=instance.date.month,
                date__year=instance.date.year
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            budget.spent_amount = expenses_for_category
            budget.save()
        except Budget.DoesNotExist:
            pass  # Budget doesn't exist, which is fine


@receiver(pre_save, sender=Transaction)
def update_budget_on_transaction_change(sender, instance, **kwargs):
    """
    Handle budget updates when a transaction is modified (date, amount, category changed)
    """
    if instance.pk and instance.type == 'expense':  # Only for existing transactions
        try:
            old_instance = Transaction.objects.get(pk=instance.pk)
            # If any important fields changed, update both old and new budgets
            if (old_instance.date != instance.date or
                old_instance.category != instance.category or
                old_instance.amount != instance.amount or
                old_instance.type != instance.type):

                # Update old budget
                old_budget = Budget.objects.get(
                    category=old_instance.category,
                    month=old_instance.date.month,
                    year=old_instance.date.year
                )
                old_expenses = Transaction.objects.filter(
                    category=old_instance.category,
                    type='expense',
                    date__month=old_instance.date.month,
                    date__year=old_instance.date.year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                old_budget.spent_amount = old_expenses
                old_budget.save()

                # Update new budget if category or date changed
                if (old_instance.category != instance.category or
                    old_instance.date.month != instance.date.month or
                    old_instance.date.year != instance.date.year):
                    new_budget, created = Budget.objects.get_or_create(
                        category=instance.category,
                        month=instance.date.month,
                        year=instance.date.year,
                        defaults={'amount': instance.amount, 'created_by': instance.created_by}
                    )
                    new_expenses = Transaction.objects.filter(
                        category=instance.category,
                        type='expense',
                        date__month=instance.date.month,
                        date__year=instance.date.year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    new_budget.spent_amount = new_expenses
                    new_budget.save()
        except Transaction.DoesNotExist:
            # This is a new transaction
            pass
        except Budget.DoesNotExist:
            # Budget doesn't exist for old category/date, which is fine
            pass