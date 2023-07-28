from fee.models import PaymentMode

def get_payment_mode(mode_id):
    try:
        mode = PaymentMode.objects.get(id=mode_id)
        return mode
    except Exception as e:
        return None