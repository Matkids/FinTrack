"""
Analytics services for FinTrack application
This module contains business logic for predictive analytics and recommendations
"""
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone

from app.models import Transaction, Category, Asset, Investment, Budget
from analytics.models import (
    FinancialForecast, AnomalyDetection, Recommendation, 
    PredictiveModel, ScenarioAnalysis
)


class CashFlowForecastService:
    """
    Service for generating cash flow forecasts using ML algorithms
    """
    
    @staticmethod
    def generate_forecast(user, months_ahead=6, model_type='linear_regression'):
        """
        Generate cash flow forecast based on historical data
        """
        try:
            # Get historical transaction data for the user
            historical_data = Transaction.objects.filter(
                created_by=user,
                date__gte=timezone.now().date() - timedelta(days=365)  # Last year of data
            ).order_by('date')

            if not historical_data:
                return {'success': False, 'message': 'No historical data available'}

            # Process data into DataFrame
            df = pd.DataFrame(list(historical_data.values('date', 'type', 'amount')))
            if df.empty:
                return {'success': False, 'message': 'No historical data available after filtering'}

            df['date'] = pd.to_datetime(df['date'])
            df['month_year'] = df['date'].dt.to_period('M')

            # Aggregate transaction amounts by month
            monthly_data = df.groupby('month_year').agg({
                'amount': 'sum'
            }).reset_index()

            if len(monthly_data) == 0:
                return {'success': False, 'message': 'No monthly data could be aggregated'}

            # Convert period to numeric for regression
            monthly_data['month_number'] = range(len(monthly_data))
            X = monthly_data['month_number'].values.reshape(-1, 1)
            y = monthly_data['amount'].values

            # Check if we have sufficient data
            if len(X) < 3:  # Need at least 3 data points for forecasting
                return {
                    'success': False,
                    'message': f'Insufficient historical data for forecasting (need at least 3 months, got {len(X)})'
                }

            # Train model
            model = LinearRegression()
            try:
                model.fit(X, y)
            except Exception as e:
                return {'success': False, 'message': f'Error training model: {str(e)}'}

            # Generate predictions for next months
            last_month_number = X[-1][0] if len(X) > 0 else 0
            future_X = np.array([[last_month_number + i + 1] for i in range(months_ahead)])
            try:
                predictions = model.predict(future_X)
            except Exception as e:
                return {'success': False, 'message': f'Error making predictions: {str(e)}'}

            # Create FinancialForecast objects
            created_forecasts = []
            for i, pred_value in enumerate(predictions):
                prediction_date = (timezone.now().date().replace(day=1) +
                                 timedelta(days=32*(i+1))).replace(day=1)

                forecast = FinancialForecast.objects.create(
                    forecast_type='cash_flow',
                    predicted_value=abs(Decimal(str(pred_value))),
                    prediction_date=prediction_date,
                    generated_by=user,
                    model_used=f'{model_type}',
                    training_period_start=monthly_data['month_year'].min().start_time.date() if len(monthly_data) > 0 else timezone.now().date(),
                    training_period_end=monthly_data['month_year'].max().start_time.date() if len(monthly_data) > 0 else timezone.now().date(),
                    notes=f'Cash flow forecast for month {i+1}'
                )
                created_forecasts.append({
                    'date': prediction_date.isoformat(),
                    'value': float(forecast.predicted_value)
                })

            # Save model information
            try:
                PredictiveModel.objects.update_or_create(
                    model_name='Cash Flow Forecast',
                    version='1.0',
                    defaults={
                        'model_type': 'cash_flow_forecast',
                        'description': 'Linear regression model for cash flow forecasting',
                        'training_data_start': monthly_data['month_year'].min().start_time.date(),
                        'training_data_end': monthly_data['month_year'].max().start_time.date(),
                        'accuracy_score': model.score(X, y) if len(X) > 1 else 0.0,
                        'feature_columns': ['month_number'],
                        'algorithm_used': 'LinearRegression'
                    }
                )
            except Exception as e:
                print(f"Warning: Error saving model information: {str(e)}")

            return {
                'success': True,
                'predictions': created_forecasts,
                'message': f'Generated {months_ahead} months of cash flow forecasts'
            }
        except Exception as e:
            print(f"Unexpected error in generate_forecast: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating forecast: {str(e)}'
            }


class AnomalyDetectionService:
    """
    Service for detecting financial anomalies using ML algorithms
    """
    
    @staticmethod
    def detect_expense_anomalies(user, lookback_days=90):
        """
        Detect unusual expenses using anomaly detection algorithms
        """
        try:
            # Get recent expenses for the user
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=lookback_days)

            expenses = Transaction.objects.filter(
                type='expense',
                created_by=user,
                date__range=[start_date, end_date]
            ).order_by('date')

            if not expenses:
                return {'success': False, 'message': 'No expense data available for analysis'}

            # Prepare data for anomaly detection
            df = pd.DataFrame(list(expenses.values('id', 'date', 'amount', 'category__name')))
            if df.empty:
                return {'success': False, 'message': 'No expense data available for analysis after filtering'}

            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            df['day_of_month'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.dayofweek

            # Check if we have enough data points
            if len(df) < 5:  # Need at least 5 data points
                return {
                    'success': False,
                    'message': f'Insufficient data for anomaly detection (need at least 5 transactions, got {len(df)})'
                }

            # Use Isolation Forest for anomaly detection
            # Prepare features
            features = df[['amount', 'day_of_month', 'day_of_week']].values

            # Check if features array has valid values
            if len(features) == 0 or features.size == 0:
                return {'success': False, 'message': 'No valid features to analyze for anomaly detection'}

            # Normalize the features
            scaler = StandardScaler()
            try:
                features_scaled = scaler.fit_transform(features)
            except Exception:
                return {'success': False, 'message': 'Error normalizing features for anomaly detection'}

            # Apply Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)  # Flag 10% as anomalies
            try:
                anomalies = iso_forest.fit_predict(features_scaled)
            except Exception as e:
                return {'success': False, 'message': f'Error in anomaly detection algorithm: {str(e)}'}

            # Create AnomalyDetection records for detected anomalies
            anomaly_transactions = df[anomalies == -1]  # -1 indicates anomaly

            created_anomalies = []
            for _, row in anomaly_transactions.iterrows():
                try:
                    transaction = Transaction.objects.get(id=row['id'])

                    # Determine anomaly type based on the detected pattern
                    anomaly_type = 'unusual_amount'
                    if row['amount'] > df['amount'].quantile(0.9):  # Top 10% by amount
                        anomaly_type = 'unusual_amount'
                    elif row['day_of_month'] in [1, 15] and len(df[df['day_of_month'].isin([1, 15])]) > 0:
                        anomaly_type = 'frequency_change'

                    severity = 3 if row['amount'] > df['amount'].quantile(0.95) else 2  # High or medium severity

                    anomaly = AnomalyDetection.objects.create(
                        anomaly_type=anomaly_type,
                        transaction=transaction,
                        detected_value=Decimal(str(row['amount'])),
                        expected_value=Decimal(str(df['amount'].mean())),
                        severity=severity,
                        description=f'Unusual expense detected: ${row["amount"]:.2f} for {row["category__name"]} on {row["date"].date()}',
                    )
                    created_anomalies.append({
                        'transaction_id': transaction.id,
                        'amount': float(transaction.amount),
                        'category': transaction.category.name,
                        'date': transaction.date.isoformat(),
                        'severity': severity
                    })
                except Transaction.DoesNotExist:
                    # Skip if transaction doesn't exist
                    continue
                except Exception as e:
                    # Log the error but continue processing other anomalies
                    print(f"Error processing anomaly for transaction {row['id']}: {str(e)}")
                    continue

            # Save model information (only if we have valid data)
            # Use get_or_create to avoid duplicate key constraint violations
            PredictiveModel.objects.update_or_create(
                model_name='Expense Anomaly Detection',
                version='1.0',
                defaults={
                    'model_type': 'expense_anomaly',
                    'description': f'Isolation Forest model for detecting unusual expenses (last {lookback_days} days)',
                    'training_data_start': start_date,
                    'training_data_end': end_date,
                    'feature_columns': ['amount', 'day_of_month', 'day_of_week'],
                    'algorithm_used': 'IsolationForest',
                    'accuracy_score': None  # We don't have accuracy for anomaly detection in this implementation
                }
            )

            return {
                'success': True,
                'anomalies_detected': len(created_anomalies),
                'anomalies': created_anomalies
            }
        except Exception as e:
            print(f"Unexpected error in detect_expense_anomalies: {str(e)}")
            return {
                'success': False,
                'message': f'Error in anomaly detection: {str(e)}'
            }


class RecommendationService:
    """
    Service for generating smart financial recommendations
    """
    
    @staticmethod
    def generate_recommendations(user):
        """
        Generate smart recommendations based on financial data analysis
        """
        try:
            recommendations_created = []

            # 1. Budget adjustment recommendations
            budgets = Budget.objects.filter(created_by=user)

            for budget in budgets:
                try:
                    utilization = budget.budget_utilization_percentage()
                    if utilization > 90:  # Over 90% used
                        rec = Recommendation.objects.create(
                            recommendation_type='budget_adjustment',
                            title=f'Increase budget for {budget.category.name}',
                            description=f'The budget for {budget.category.name} is at {utilization}% utilization. Consider increasing the budget.',
                            suggested_action=f'Increase the budget for {budget.category.name} by at least 20%',
                            impact_estimate=budget.amount * Decimal('0.20'),
                            confidence_score=0.85,
                            generated_by=user,
                            related_budget=budget
                        )
                        recommendations_created.append({
                            'type': 'budget_adjustment',
                            'title': rec.title,
                            'confidence': rec.confidence_score
                        })
                    elif utilization < 20:  # Under 20% used
                        rec = Recommendation.objects.create(
                            recommendation_type='budget_adjustment',
                            title=f'Consider reducing budget for {budget.category.name}',
                            description=f'The budget for {budget.category.name} is at only {utilization}% utilization. Consider reducing the budget.',
                            suggested_action=f'Review and potentially reduce the budget for {budget.category.name}',
                            impact_estimate=budget.amount * Decimal('-0.15'),  # Potential savings
                            confidence_score=0.70,
                            generated_by=user,
                            related_budget=budget
                        )
                        recommendations_created.append({
                            'type': 'budget_adjustment',
                            'title': rec.title,
                            'confidence': rec.confidence_score
                        })
                except Exception as e:
                    print(f"Error processing budget recommendation: {str(e)}")
                    continue

            # 2. Expense optimization recommendations
            expense_transactions = Transaction.objects.filter(
                type='expense',
                created_by=user
            ).select_related('category')

            # Group expenses by category
            category_stats = {}
            for trans in expense_transactions:
                try:
                    cat_name = trans.category.name
                    if cat_name not in category_stats:
                        category_stats[cat_name] = {'total': Decimal('0.00'), 'count': 0, 'transactions': []}
                    category_stats[cat_name]['total'] += trans.amount
                    category_stats[cat_name]['count'] += 1
                    category_stats[cat_name]['transactions'].append(trans.amount)
                except Exception:
                    # Skip if there are issues with the transaction
                    continue

            for cat_name, stats in category_stats.items():
                try:
                    avg_amount_decimal = Decimal(str(stats['total'] / stats['count'] if stats['count'] > 0 else 0))
                    # If category has multiple transactions and high average
                    if stats['count'] > 3 and avg_amount_decimal > Decimal('100'):
                        rec = Recommendation.objects.create(
                            recommendation_type='expense_optimization',
                            title=f'Review expenses in {cat_name} category',
                            description=f'Average expense of ${avg_amount_decimal:.2f} in {cat_name} category across {stats["count"]} transactions.',
                            suggested_action=f'Analyze transactions in {cat_name} to identify potential cost savings opportunities',
                            impact_estimate=avg_amount_decimal * Decimal('0.10'),  # Potential 10% savings
                            confidence_score=0.75,
                            generated_by=user
                        )
                        recommendations_created.append({
                            'type': 'expense_optimization',
                            'title': rec.title,
                            'confidence': rec.confidence_score
                        })
                except Exception as e:
                    print(f"Error processing expense optimization recommendation: {str(e)}")
                    continue

            # 3. Investment opportunity recommendations
            try:
                investments = Investment.objects.filter(created_by=user)
                total_investment_value = sum(inv.current_value for inv in investments) if investments else Decimal('0.00')
                total_assets_value = sum(asset.current_value for asset in Asset.objects.filter(created_by=user)) if Asset.objects.filter(created_by=user) else Decimal('0.00')

                # Convert to Decimal to avoid mixed type operations
                total_investment_value = Decimal(str(total_investment_value))
                total_assets_value = Decimal(str(total_assets_value))

                if total_assets_value > 0 and total_investment_value < total_assets_value * Decimal('0.3'):  # Less than 30% in investments
                    rec = Recommendation.objects.create(
                        recommendation_type='investment_opportunity',
                        title='Consider increasing investment allocation',
                        description=f'Your investment portfolio represents {(total_investment_value/total_assets_value)*100:.1f}% of your total assets. Consider diversifying.',
                        suggested_action='Consider allocating 30-40% of total assets to investments',
                        impact_estimate=total_assets_value * Decimal('0.05'),  # Potential growth
                        confidence_score=0.65,
                        generated_by=user
                    )
                    recommendations_created.append({
                        'type': 'investment_opportunity',
                        'title': rec.title,
                        'confidence': rec.confidence_score
                    })
            except Exception as e:
                print(f"Error processing investment opportunity recommendation: {str(e)}")

            # 4. Cash flow recommendations
            try:
                recent_income = Transaction.objects.filter(
                    type='income',
                    created_by=user,
                    date__gte=timezone.now().date() - timedelta(days=90)
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

                recent_expenses = Transaction.objects.filter(
                    type='expense',
                    created_by=user,
                    date__gte=timezone.now().date() - timedelta(days=90)
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

                if recent_income > 0 and recent_expenses > recent_income * Decimal('0.9'):  # Expenses > 90% of income
                    rec = Recommendation.objects.create(
                        recommendation_type='expense_optimization',
                        title='High expense to income ratio detected',
                        description=f'Expenses ({recent_expenses}) represent {(recent_expenses/recent_income)*100:.1f}% of income ({recent_income}).',
                        suggested_action='Review and reduce non-essential expenses to maintain healthy cash flow',
                        impact_estimate=recent_income * Decimal('0.05'),  # Potential 5% improvement
                        confidence_score=0.80,
                        generated_by=user
                    )
                    recommendations_created.append({
                        'type': 'expense_optimization',
                        'title': rec.title,
                        'confidence': rec.confidence_score
                    })
            except Exception as e:
                print(f"Error processing cash flow recommendation: {str(e)}")

            return {
                'success': True,
                'recommendations_created': len(recommendations_created),
                'recommendations': recommendations_created
            }
        except Exception as e:
            print(f"Unexpected error in generate_recommendations: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating recommendations: {str(e)}'
            }


class ScenarioAnalysisService:
    """
    Service for running what-if scenario analyses
    """
    
    @staticmethod
    def run_scenario_analysis(user, scenario_type, parameters):
        """
        Run what-if scenario analysis based on parameters
        """
        try:
            if scenario_type == 'revenue_change':
                return ScenarioAnalysisService._analyze_revenue_change(user, parameters)
            elif scenario_type == 'expense_reduction':
                return ScenarioAnalysisService._analyze_expense_reduction(user, parameters)
            elif scenario_type == 'investment_impact':
                return ScenarioAnalysisService._analyze_investment_impact(user, parameters)
            else:
                return {'success': False, 'message': 'Invalid scenario type'}
        except Exception as e:
            print(f"Unexpected error in run_scenario_analysis: {str(e)}")
            return {
                'success': False,
                'message': f'Error running scenario analysis: {str(e)}'
            }
    
    @staticmethod
    def _analyze_revenue_change(user, parameters):
        """
        Analyze impact of revenue changes
        """
        change_percentage = parameters.get('change_percentage', 0)
        period_months = parameters.get('period_months', 12)
        
        # Get current monthly revenue
        current_monthly_revenue = Transaction.objects.filter(
            type='income',
            created_by=user,
            date__month=timezone.now().date().month,
            date__year=timezone.now().date().year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate projected revenue
        monthly_revenue_projection = []
        change_decimal = Decimal(str(1 + change_percentage / 100))
        for month in range(period_months):
            projected_revenue = current_monthly_revenue * change_decimal
            projection_date = (timezone.now().date().replace(day=1) + timedelta(days=32*month)).replace(day=1)
            monthly_revenue_projection.append({
                'date': projection_date.isoformat(),
                'projected_revenue': float(projected_revenue)
            })

        predicted_outcomes = {
            'current_monthly_revenue': float(current_monthly_revenue),
            'projected_total_revenue': float(sum(item['projected_revenue'] for item in monthly_revenue_projection)),
            'change_percentage': change_percentage,
            'monthly_projections': monthly_revenue_projection
        }
        
        # Create scenario analysis record
        scenario = ScenarioAnalysis.objects.create(
            name=f"Revenue Change Scenario ({change_percentage:+.1f}%)",
            scenario_type='revenue_change',
            description=f"Analysis of revenue change by {change_percentage:+.1f}%",
            input_parameters=parameters,
            predicted_outcomes=predicted_outcomes,
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=period_months
        )
        
        return {
            'success': True,
            'scenario_id': scenario.id,
            'predicted_outcomes': predicted_outcomes
        }
    
    @staticmethod
    def _analyze_expense_reduction(user, parameters):
        """
        Analyze impact of expense reduction
        """
        reduction_percentage = parameters.get('reduction_percentage', 0)
        period_months = parameters.get('period_months', 12)
        
        # Get current monthly expenses
        current_monthly_expenses = Transaction.objects.filter(
            type='expense',
            created_by=user,
            date__month=timezone.now().date().month,
            date__year=timezone.now().date().year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate projected expenses
        monthly_expense_projection = []
        reduction_decimal = Decimal(str(1 - reduction_percentage / 100))
        for month in range(period_months):
            projected_expenses = current_monthly_expenses * reduction_decimal
            projection_date = (timezone.now().date().replace(day=1) + timedelta(days=32*month)).replace(day=1)
            monthly_expense_projection.append({
                'date': projection_date.isoformat(),
                'projected_expenses': float(projected_expenses)
            })

        # Calculate total savings
        reduction_rate = Decimal(str(reduction_percentage / 100))
        total_savings_calc = current_monthly_expenses * reduction_rate * Decimal(str(period_months))

        predicted_outcomes = {
            'current_monthly_expenses': float(current_monthly_expenses),
            'projected_total_expenses': float(sum(item['projected_expenses'] for item in monthly_expense_projection)),
            'total_savings': float(total_savings_calc),
            'reduction_percentage': reduction_percentage,
            'monthly_projections': monthly_expense_projection
        }
        
        # Create scenario analysis record
        scenario = ScenarioAnalysis.objects.create(
            name=f"Expense Reduction Scenario ({reduction_percentage:.1f}%)",
            scenario_type='expense_reduction',
            description=f"Analysis of expense reduction by {reduction_percentage:.1f}%",
            input_parameters=parameters,
            predicted_outcomes=predicted_outcomes,
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=period_months
        )
        
        return {
            'success': True,
            'scenario_id': scenario.id,
            'predicted_outcomes': predicted_outcomes
        }
    
    @staticmethod
    def _analyze_investment_impact(user, parameters):
        """
        Analyze impact of investment changes
        """
        # This would involve more complex investment modeling
        # For now, we'll create a simplified analysis
        initial_investment_float = parameters.get('initial_investment', 10000)
        expected_roi = parameters.get('expected_roi', 8)  # 8% annually
        period_months = parameters.get('period_months', 12)

        monthly_roi = expected_roi / 12 / 100  # Monthly ROI as decimal

        monthly_projections = []
        current_value_decimal = Decimal(str(initial_investment_float))
        monthly_multiplier = Decimal(str(1 + monthly_roi))

        for month in range(period_months):
            current_value_decimal = current_value_decimal * monthly_multiplier
            projection_date = (timezone.now().date().replace(day=1) + timedelta(days=32*month)).replace(day=1)
            initial_investment_decimal = Decimal(str(initial_investment_float))
            monthly_projections.append({
                'date': projection_date.isoformat(),
                'projected_value': float(current_value_decimal),
                'gained': float(current_value_decimal - initial_investment_decimal)
            })

        predicted_outcomes = {
            'initial_investment': float(initial_investment_float),
            'expected_annual_roi': expected_roi,
            'projected_value_end': float(monthly_projections[-1]['projected_value']) if monthly_projections else float(initial_investment_float),
            'projected_gain': float(monthly_projections[-1]['gained']) if monthly_projections else 0.0,
            'monthly_projections': monthly_projections
        }
        
        # Create scenario analysis record
        scenario = ScenarioAnalysis.objects.create(
            name=f"Investment Impact Scenario ({expected_roi:.1f}% ROI)",
            scenario_type='investment_impact',
            description=f"Analysis of investment with {expected_roi:.1f}% annual ROI",
            input_parameters=parameters,
            predicted_outcomes=predicted_outcomes,
            generated_by=user,
            base_date=timezone.now().date(),
            period_months=period_months
        )
        
        return {
            'success': True,
            'scenario_id': scenario.id,
            'predicted_outcomes': predicted_outcomes
        }