from django.core.validators import RegexValidator

fee_type_name_validator = RegexValidator(r'^[a-zA-Z ]+$', 'only valid fee type name is required')
