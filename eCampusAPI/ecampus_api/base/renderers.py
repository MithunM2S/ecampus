from django.conf import settings
from rest_framework import renderers

class APIJSONRenderer(renderers.JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = {}
        if renderer_context is not None:
            status_code = renderer_context['response'].status_code
            response['code'] = status_code
            try:
                is_api_error = data.get('exception', None)
            except:
                 is_api_error = False
            if status_code in settings.SUCCESS_CODES and not is_api_error:
                response['status'] = True
                response['message'] = 'OK'
                if not status_code == 201:
                    response['data'] = data if isinstance(data, list) else [data]
                else:
                    object_create_response = get_field_data(data, 'id', 'student_id', 'uuid')
                    if object_create_response:
                        response['data'] = [object_create_response]
            else:
                if data.get('exception', None):
                    del data['exception']
                response['status'] = False
                response['message'] = data
                # response['message'] = data.get('detail')
                response['message'] = [str(message_name) + ' - ' + str(data['detail'][message_name][0]) if isinstance(data['detail'][message_name], list) else str(data[message_name]) for message_name in data.get('detail')] if isinstance(data.get('detail'), dict) else data.get('detail')
        return super(APIJSONRenderer, self).render(response, accepted_media_type, renderer_context)

def get_field_data(dataObject, *argv):
    field_data = {}
    for arg in argv:
        try:
            argValue = dataObject.get(arg, None)
            if argValue:
                field_data[arg] = argValue
        except Exception as e:
            pass
    return field_data
