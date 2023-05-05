from django.core.validators import RegexValidator

alpha_space = RegexValidator(r'^[a-zA-Z ]+$', 'Only alphabetic and space allowed')