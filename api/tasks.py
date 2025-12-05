# your_app/tasks.py
from celery import shared_task
from django.core.cache import cache
from django.db.models import Sum, Q
import jdatetime
from .models import Transaction

@shared_task
def cache_monthly_summary(user_id, shamsi_year, shamsi_month):

    from .models import Transaction

    if shamsi_month <= 6:
        end_day = 31
    elif shamsi_month <= 11:
        end_day = 30
    else:
        if jdatetime.date(shamsi_year, 1, 1).isleap():
            end_day = 30
        else:
            end_day = 29

    start_j_date = jdatetime.date(shamsi_year, shamsi_month, 1)
    end_j_date = jdatetime.date(shamsi_year, shamsi_month, end_day)

    start_date = start_j_date.togregorian()
    end_date = end_j_date.togregorian()

    income = Transaction.objects.filter(
        user_id=user_id,
        category__category_type='income',
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    expense = Transaction.objects.filter(
        user_id=user_id,
        category__category_type='expense',
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    cache_key = f'monthly_{user_id}_{shamsi_year}_{shamsi_month}'
    cache.set(cache_key, {
        'income': income,
        'expense': expense,
        'balance': income - expense
    }, timeout=3600)

    return cache_key


@shared_task
def cache_yearly_summary(user_id, shamsi_year):

    from .models import Transaction
    import jdatetime

    start_j_date = jdatetime.date(shamsi_year, 1, 1)
    if jdatetime.date(shamsi_year, 1, 1).isleap():
        end_day = 30
    else:
        end_day = 29
    end_j_date = jdatetime.date(shamsi_year, 12, end_day)

    start_date = start_j_date.togregorian()
    end_date = end_j_date.togregorian()

    income = Transaction.objects.filter(
        user_id=user_id,
        category__category_type='income',
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    expense = Transaction.objects.filter(
        user_id=user_id,
        category__category_type='expense',
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    cache_key = f'yearly_{user_id}_{shamsi_year}'
    cache.set(cache_key, {
        'income': income,
        'expense': expense,
        'balance': income - expense,
        'message': 'محاسبه با کش'
    }, timeout=3600)

    return cache_key