Dakhl-o-Kharj API - Personal Financial Management System
📊 Project Overview
Dakhl-o-Kharj (Income & Expense) is a comprehensive financial management API built with Django REST Framework. It helps users track their income, expenses, and savings with advanced reporting and automated financial features.

🚀 Live Demo & Links
GitHub Repository: https://github.com/yourusername/Dakhl_o_kharj_API
---
✨ Key Features
🔐 Secure Authentication
Mobile-based OTP Verification (No password required)

JWT Token Authentication for secure API access

Custom User Model with phone number as primary identifier

Session-based authentication with token refresh capability
---
💰 Transaction Management
Three Category Types: Income, Expense, and Savings

Persian Date Support (Shamsi/Jalali calendar integration)

Real-time Balance Calculation

Rial Currency Support (Iranian currency)

Smart Budgeting System with min/max limits

Data Validation for all monetary inputs
---
📈 Advanced Financial Features
Monthly & Yearly Financial Reports

Automatic Savings from positive balance

Category-based Budget Tracking

User-specific Data Isolation (Users can only access their own data)

Comprehensive Transaction Filtering
---
📊 Analytics & Reporting
Real-time Balance Overview

Monthly Income/Expense Summaries

Yearly Financial Reports

Per-category Spending Analysis

Budget Utilization Tracking
---
🛠 Technology Stack
Backend
Python 3.9+ - Core programming language

Django 4.2+ - Web framework

Django REST Framework 3.14+ - API development

SQLite - Primary database

Redis - Caching & Celery broker

Celery - Asynchronous task processing

Authentication & Security
JWT (JSON Web Tokens) - Secure authentication

Simple JWT - JWT implementation for Django

OTP Verification - One-Time Password system

Custom User Model - Phone-based authentication

Date & Currency Handling
jdatetime - Persian (Shamsi) date support

Custom validators - Rial currency formatting

Timezone-aware operations for Iran
---
📁 Project Structure
text
Dakhl_o_kharj_API/
├── accounts/                     Authentication app
│   ├── models.py                Custom User model
│   ├── serializers.py          Auth serializers
│   ├── views.py#                Auth views (OTP, JWT)
│    ├── utils.py                 Generate_otp
│   ├── urls.py                  Endpoint
│   └── ...
├── api/                     Core finance app
│   ├── models.py                Category, Transaction, Budgeting
│   ├── serializers.py           Financial serializers
│   ├── views.py                 API endpoints and persian jdate handling
│   ├── tasks.py                 Celery tasks
│    ├── urls.py                  Endpoints
│   └── ...
├── root/                       Project
│   ├── settings.py           
│   ├── celery.py       
│   └── urls.py           
    └── ...
---
🔧 Installation & Setup
```bash
# 1. Clone the repository
git clone https://github.com/MrezaSahraei/Dakhl_o_kharj_API.git
cd Dakhl_o_kharj_API

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your configurations

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

# 8. Run Celery worker (in separate terminal)
celery -A root worker --loglevel=info

# 9. Run Celery beat (for scheduled tasks)
celery -A root beat --loglevel=info
```
---
🌟 Unique Features
1. Persian Financial System
- Full Shamsi Date Support - All dates in Persian calendar
- Rial Currency - Native Iranian currency handling
- Persian Month Names - درآمد فروردین، هزینه اردیبهشت, etc.

2. Automated Financial Management
- Automatic savings from positive balance
```python
if user_balance > 0:
    auto_save_to_savings(user, user_balance)
```
3. Advanced Reporting
- Monthly income/expense comparison
- Year-over-year financial growth
---
🚧 Future Improvements  
- Add notifications  
- Add advanced reporting  
- Fetching with a React-based frontend 
- Deploy on Docker
---
🤝 Contribution  
This project is open for feedback and improvements.
---
📬 Contact  
If you're interested in Django backend collaboration or opportunities, feel free to reach out.
