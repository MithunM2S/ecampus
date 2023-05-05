from rest_framework.views import exception_handler
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework import response

def ecampus_exception_handler(exc, context):
    # Custom exception handling
    exc_response = exception_handler(exc, context)
    if isinstance(exc, (exceptions.APIException, serializers.ValidationError)):
        exc.status_code = status.HTTP_200_OK
        if isinstance(exc.detail, dict):
            if exc.detail.get('detail', None) == None:
                data = {'detail': exc.detail}
            else:
                data = exc.detail
        else:
            data = {'detail': exc.detail}
        data['exception'] = 'APIException'
        return response.Response(data, status=exc.status_code)
    return exc_response
