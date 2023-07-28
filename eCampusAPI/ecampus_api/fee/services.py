from fee.models import PaymentMode

def get_payment_mode(mode_id):
    try:
        mode = PaymentMode.objects.get(id=mode_id)
        return mode
    except Exception as e:
        return None
    
def calculate_month_difference(start_date, end_date):
    months_difference = (start_date.year - end_date.year) * 12 + (start_date.month - end_date.month)
    return abs(months_difference)
