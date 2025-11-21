# FinTrack - Company Financial Management Application

## Overview
FinTrack is a full-stack application designed to manage all aspects of company finances in a centralized platform. This application provides a comprehensive solution for tracking expenses, income, assets, and investments with an intuitive interface and detailed reporting capabilities.

## Prerequisites
- Python 3.8 or higher
- pip package manager

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd django_ai_starter
```

### 2. Environment Variables Setup
The application uses environment variables for configuration. The `.env` file contains the PostgreSQL configuration:

```bash
# Database Configuration for PostgreSQL
DB_NAME=fintrack_db
DB_USER=fintrack_user
DB_PASSWORD=fintrack_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DJANGO_SETTINGS_MODULE=project.settings

# Security Settings
SECRET_KEY=gpf$-vd=@ry!xvvr!@xk(w7*xh#qdjqi5sb34g2=5+kr5!%nt8
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Integration
# To connect with pgAdmin:
# Host: localhost
# Database: fintrack_db
# Username: fintrack_user
# Password: fintrack_password
# Port: 5432

# Timezone
TIME_ZONE=UTC
USE_TZ=True

# Email settings (for production)
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

The application uses `python-decouple` to read these environment variables automatically. PostgreSQL is the primary database as specified in the requirements.

### 3. Create and Activate Virtual Environment
You can use the provided setup script:

```bash
# Make the script executable (first time only)
chmod +x setup_env.sh

# Run the setup script
./setup_env.sh
```

Alternatively, you can set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup
The application uses PostgreSQL as specified in the environment variables. All necessary tables including analytics models have already been set up. If you need to reset or make changes:

```bash
# Navigate to project directory
cd project

# Create new migrations (if you made model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# For analytics features, run the data seeding
python manage.py seed_analytics_data
```

### 5. Create Superuser (Optional - already done)
If you need to create another superuser:

```bash
python manage.py createsuperuser
```

### 5. Running the Development Server
```bash
# From the project directory
cd project
python manage.py runserver
```

The application will be accessible at http://127.0.0.1:8000/

## Project Structure
```
django_ai_starter/                # Root project directory
├── setup_env.sh                  # Setup script for virtual environment
├── setup_postgres.sh             # PostgreSQL setup script
├── check_and_start.sh            # Health check and startup script
├── requirements.txt              # Python dependencies including analytics libraries
├── project/                      # Django project directory
│   ├── manage.py                 # Django management script
│   ├── app/                      # Main application
│   │   ├── models.py             # Database models
│   │   ├── views.py              # View functions
│   │   ├── forms.py              # Form classes including analytics forms
│   │   ├── urls.py               # URL patterns
│   │   └── ...
│   ├── analytics/                # Advanced analytics application
│   │   ├── models.py             # Analytics-specific models
│   │   ├── views.py              # Analytics view functions
│   │   ├── services.py           # ML/AI service implementations
│   │   └── urls.py               # Analytics URL patterns
│   └── project/                  # Project settings
│       └── settings.py           # Configuration settings with analytics integration
├── templates/                    # HTML templates
│   ├── base.html                 # Base template with analytics integration
│   ├── dashboard.html            # Main dashboard with analytics widgets
│   └── analytics/                # Analytics-specific templates
├── static/                       # Static assets
│   └── dist/                     # Compiled CSS
└── media/                        # File uploads directory
```

## Features
- **Dashboard**: Real-time financial summary with charts
- **Transaction Management**: Income and expense tracking with attachment support
- **Asset Management**: Fixed and current assets with depreciation and maintenance forecasting
- **Investment Management**: Portfolio tracking with ROI analysis and predictive insights
- **Reporting**: Automated financial reports (P&L, Cash Flow, Balance Sheet)
- **User Management**: Role-based access control
- **Audit Trail**: Complete change tracking
- **Analytics & AI**: Advanced analytics including:
  - Predictive cash flow forecasting
  - Anomaly detection for unusual expenses
  - Smart recommendations for expense optimization
  - Investment opportunity identification
  - Scenario analysis for "what-if" planning
  - Asset maintenance prediction
  - Budget utilization alerts
- **File Attachments**: Support for uploading receipts and documents to transactions
- **Data Visualization**: Interactive charts and graphs for financial data

## User Roles
- **Super Admin**: Full access to all features
- **Finance Manager**: Transaction management and reporting
- **Accountant**: Transaction input and report viewing
- **Viewer**: Dashboard and reports only

## Troubleshooting
If you encounter issues:
1. Make sure your virtual environment is activated
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check that migrations are applied: `python manage.py migrate`
4. For CSS issues, make sure Tailwind was built: `npx tailwindcss build ./project/static/src/input.css -o ./project/static/dist/output.css`

## Analytics and AI Features
After starting the server, navigate to the Analytics Dashboard at:
- **URL**: `http://127.0.0.1:8000/analytics/`

### Available Analytics Features:
1. **Cash Flow Forecasting**: Predict future cash flows based on historical data
2. **Expense Anomaly Detection**: Identify unusual expense patterns
3. **Smart Recommendations**: AI-powered financial optimization suggestions
4. **Scenario Analysis**: "What-if" planning with interactive projections
5. **Investment Insights**: ROI predictions and investment opportunity identification
6. **Maintenance Forecasting**: Predict future asset maintenance needs
7. **Budget Monitoring**: Real-time budget utilization tracking

### File Attachments
The application supports uploading receipt files and transaction documents through:
- **Transaction Creation/Update**: Direct attachment upload
- **File Preview**: Integrated file preview in transaction list and detail views
- **Download Links**: Easy access to downloaded files

## Stopping the Server
Press `Ctrl+C` in the terminal where the server is running.

## Activating the Virtual Environment in Future Sessions
```bash
source venv/bin/activate
cd project
python manage.py runserver
```

## Default Credentials
- **Username**: admin
- **Password**: adminpass123